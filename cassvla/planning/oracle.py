"""Oracle rollout scoring: c* and the full oracle ordering over a candidate set.

For one decision point (family, seed, t_dec):

1. Prefix. Reset the episode and drive the hazard-blind cruise policy for
   t_dec seconds, recording the actions.
2. Candidates. Generate the maneuver bank from the state at t_dec.
3. Rollouts. For each candidate: reset the same seed, replay the recorded
   prefix actions, then drive the candidate with the tracking controller for
   its horizon. Re-simulation (rather than checking candidates against one
   logged actor future) is required because hazard triggers react to the ego:
   a pedestrian steps out only when the ego gets close, the red-light runner
   launches on the ego's ETA.
4. Score. Per step: polygon clearance to every actor, constant-velocity TTC,
   MetaDrive crash flags, red-light flag, out-of-road. Candidates are ranked
   safe first, then by ``score`` (progress minus safety penalties).

Note on determinism: a fresh env replays bit-identically (Phase 1, Q4), but
re-``reset`` on the same env drifts by ~1e-5 m over 50 steps. All rollouts of
one decision share an env, so the drift is identical in kind for every
candidate and far below any scoring threshold.
"""
import math

import numpy as np
from metadrive.component.traffic_light.base_traffic_light import BaseTrafficLight

from cassvla.planning.candidates import HORIZON, cruise_candidate, generate_candidates
from cassvla.planning.control import Tracker
from cassvla.planning.geometry import box, poly_distance
from cassvla.scenarios import make_env

CRUISE = 8.0            # m/s, prefix policy target speed
SAFE_CLEARANCE = 0.5    # m
SAFE_TTC = 1.0          # s
TTC_CAP = 10.0          # s, reported when nothing is closing
NO_ACTOR_CLEARANCE = 99.0
W_COLLISION, W_RED, W_OFFROAD = 1000.0, 500.0, 500.0
W_TTC, W_CLEARANCE = 20.0, 20.0


def _actors(env):
    ego = env.agent
    for o in env.engine.get_objects().values():
        if o is ego or isinstance(o, BaseTrafficLight):
            continue
        yield o


def _poly(o):
    try:
        bb = np.asarray(o.bounding_box, dtype=float)[:, :2]
        if bb.shape == (4, 2):
            return bb
    except Exception:
        pass
    return box(o.position, o.heading_theta, o.LENGTH, o.WIDTH)


def _ttc(clearance, p_e, v_e, p_a, v_a):
    r = np.asarray(p_a, float)[:2] - np.asarray(p_e, float)[:2]
    n = np.linalg.norm(r)
    if n < 1e-6:
        return 0.0
    closing = -float(np.dot(r / n, np.asarray(v_a, float)[:2] - np.asarray(v_e, float)[:2]))
    return clearance / closing if closing > 1e-3 else TTC_CAP


def score(m):
    """Scalar used for ranking: progress minus safety penalties."""
    return (m["progress"]
            - W_COLLISION * m["collision"] - W_RED * m["red_light"] - W_OFFROAD * m["off_road"]
            - W_TTC * max(0.0, 1.5 * SAFE_TTC - m["min_ttc"])
            - W_CLEARANCE * max(0.0, 2.0 * SAFE_CLEARANCE - m["min_clearance"]))


def is_safe(m):
    return not (m["collision"] or m["red_light"] or m["off_road"]) and m["min_clearance"] >= SAFE_CLEARANCE and m["min_ttc"] >= SAFE_TTC


class Oracle:
    """Owns one HazardEnv for a family (MetaDrive allows one engine per process)."""

    def __init__(self, family, start_seed=0, num_scenarios=1, horizon=HORIZON, cruise=CRUISE):
        self.family, self.horizon, self.cruise = family, horizon, cruise
        self.env = make_env(family, seed=start_seed, num_scenarios=num_scenarios)

    def close(self):
        self.env.close()

    # ---- episode helpers -------------------------------------------------
    def _prefix(self, seed, t_dec):
        env = self.env
        env.reset(seed=seed)
        n = int(round(t_dec / 0.1))
        tracker = Tracker(cruise_candidate(env, self.cruise, t_dec + 1.0), env.agent)
        actions = []
        for _ in range(n):
            a = tracker.act(env.agent)
            _, _, term, trunc, info = env.step(a)
            actions.append(a)
            if term or trunc:
                return actions, info
        return actions, None

    def _replay(self, seed, actions):
        self.env.reset(seed=seed)
        for a in actions:
            self.env.step(a)

    def rollout(self, seed, actions, cand):
        """Replay the prefix, drive ``cand``, and return its metrics."""
        self._replay(seed, actions)
        env = self.env
        ego = env.agent
        tracker = Tracker(cand, ego)
        start = tracker.path.project(ego.position)
        m = dict(collision=False, red_light=False, off_road=False, min_clearance=math.inf, min_ttc=TTC_CAP,
                 closest_actor=None, t_collision=None, steps=0, end=None)
        for k in range(len(cand.t) - 1):
            _, _, term, trunc, info = env.step(tracker.act(ego))
            m["steps"] = k + 1
            ego_poly, p_e, v_e = _poly(ego), ego.position, ego.velocity
            for o in _actors(env):
                c = poly_distance(ego_poly, _poly(o))
                if c < m["min_clearance"]:
                    m["min_clearance"], m["closest_actor"] = c, type(o).__name__
                m["min_ttc"] = min(m["min_ttc"], _ttc(c, p_e, v_e, o.position, o.velocity))
            m["red_light"] |= bool(ego.red_light)
            m["off_road"] |= bool(info.get("out_of_road") or info.get("crash_sidewalk") or info.get("crash_building"))
            if info.get("crash_vehicle") or info.get("crash_object") or info.get("crash_human"):
                m["collision"], m["t_collision"] = True, round((k + 1) * 0.1, 1)
            if term or trunc:
                m["end"] = [key for key in ("arrive_dest", "crash_vehicle", "crash_object", "crash_human", "out_of_road", "max_step") if info.get(key)]
                break
        m["collision"] |= m["min_clearance"] <= 0.0
        m["min_clearance"] = round(float(m["min_clearance"]), 2) if math.isfinite(m["min_clearance"]) else NO_ACTOR_CLEARANCE
        m["min_ttc"] = round(float(m["min_ttc"]), 2)
        m["progress"] = round(tracker.path.project(ego.position) - start, 2)
        m["tracking"] = tracker.tracking_error()
        m["score"] = round(score(m), 2)
        m["safe"] = is_safe(m)
        return m

    # ---- one decision point ------------------------------------------------
    def label(self, seed, t_dec):
        """Oracle record for one decision point, or a record with ``skipped`` set if the prefix ended the episode."""
        actions, ended = self._prefix(seed, t_dec)
        rec = dict(family=self.family, seed=int(seed), t_dec=float(t_dec), cruise=self.cruise, horizon=self.horizon)
        if ended is not None:
            rec["skipped"] = "prefix ended episode: " + ",".join(k for k in ("crash_vehicle", "crash_object", "crash_human", "out_of_road", "arrive_dest") if ended.get(k))
            return rec
        env = self.env
        ego = env.agent
        rec["ego"] = dict(position=[round(float(x), 2) for x in ego.position], heading=round(float(ego.heading_theta), 3),
                          speed=round(float(ego.speed), 2), lane=list(ego.lane_index))
        rec["hazards"] = env.hazards.get_state()
        rec["signals"] = {k: v for k, v in env.signals.get_state().items() if k != "stop_points"}
        cands = generate_candidates(env, self.horizon)
        rec["prefix_actions"] = [[round(a, 4) for a in act] for act in actions]
        rec["candidates"] = [c.to_dict() for c in cands]
        rec["metrics"] = {c.name: self.rollout(seed, actions, c) for c in cands}
        # safe candidates first, then by score: a risky-but-fast candidate never outranks a safe one
        order = sorted(rec["metrics"], key=lambda n: (not rec["metrics"][n]["safe"], -rec["metrics"][n]["score"]))
        rec["oracle_order"] = order
        rec["c_star"] = order[0]
        n_safe = sum(m["safe"] for m in rec["metrics"].values())
        rec["n_safe"] = n_safe
        # refined proposal section 3: keep only scenes where candidates disagree under the oracle
        rec["retained"] = 0 < n_safe < len(cands)
        return rec
