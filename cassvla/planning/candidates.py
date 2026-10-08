"""Candidate trajectory generator (refined proposal section 3).

A deliberately simple maneuver bank fitted to the road geometry, not a
learned planner: lane keep at the current and a higher speed, decelerate,
stop, and lane change left/right where an adjacent lane exists. Every
candidate is a time-indexed reference (t, xy, heading, speed) at the env
step (0.1 s) over ``horizon`` seconds, in world frame.

Paths follow the ego's route: a lane "chain" starts at the ego's current
lane and continues through ``navigation.checkpoints``, keeping the same lane
index (clipped to each road's lane count). Lane 0 is the leftmost, so
"left" means index k-1.
"""
from dataclasses import dataclass, field

import numpy as np

from cassvla.planning.geometry import Polyline

DT = 0.1
HORIZON = 5.0         # s; long enough that "fast into an obstacle" shows up before the rollout ends
V_MAX = 15.0
ACCEL = 2.0           # m/s^2, comfortable
DECEL = 2.5           # m/s^2, comfortable
STOP_DECEL = 4.0      # m/s^2, firm but not emergency
LANE_CHANGE_T = 3.0   # s
SPEED_UP = 3.0        # m/s added by keep_fast


@dataclass
class Candidate:
    name: str
    maneuver: str               # keep | decelerate | stop | change
    target_lane: tuple          # lane index the maneuver ends in
    target_speed: float
    t: np.ndarray
    xy: np.ndarray              # (N, 2)
    heading: np.ndarray         # (N,)
    speed: np.ndarray           # (N,)
    meta: dict = field(default_factory=dict)

    def to_dict(self, decimals=2):
        return dict(name=self.name, maneuver=self.maneuver, target_lane=list(self.target_lane), target_speed=round(self.target_speed, 2),
                    xy=np.round(self.xy, decimals).tolist(), speed=np.round(self.speed, decimals).tolist())


def speed_profile(v0, v_target, accel, decel, horizon=HORIZON, dt=DT):
    """Constant-rate ramp from v0 to v_target, then hold. Returns t, v, s (arc length)."""
    t = np.arange(0.0, horizon + 1e-9, dt)
    if v_target >= v0:
        v = np.minimum(v0 + accel * t, v_target)
    else:
        v = np.maximum(v0 - decel * t, v_target)
    s = np.r_[0.0, np.cumsum(0.5 * (v[1:] + v[:-1]) * dt)]
    return t, v, s


def lane_chain(env, lane_index, s_ahead, step=0.5):
    """Polyline along ``lane_index`` and its continuation on the ego's route, starting ``s_ahead`` metres
    behind the ego's projection so blending stays valid near the start."""
    rn = env.engine.current_map.road_network
    route = list(env.agent.navigation.checkpoints)
    a, b, k = lane_index
    lane = rn.get_lane((a, b, k))
    lon0, _ = lane.local_coordinates(env.agent.position)
    lon0 = max(0.0, lon0 - 5.0)
    pts, total = [], 0.0
    while True:
        lons = np.arange(lon0, lane.length, step)
        if len(lons):
            pts += [lane.position(float(l), 0.0) for l in lons]
            total += lane.length - lon0
        if total >= s_ahead:
            break
        nxt = _next_road(rn, route, a, b)
        if nxt is None:
            break
        a, b = nxt
        lanes = rn.graph[a][b]
        lane = lanes[min(k, len(lanes) - 1)]
        lon0 = 0.0
    pts.append(lane.position(lane.length, 0.0))
    xy = np.asarray(pts, dtype=float)
    if total < s_ahead:   # route ends: extend straight
        d = xy[-1] - xy[-2]
        d /= np.linalg.norm(d)
        xy = np.vstack([xy, xy[-1] + d * (s_ahead - total + 10.0)])
    return Polyline(xy)


def _next_road(rn, route, a, b):
    if b in route and route.index(b) + 1 < len(route):
        c = route[route.index(b) + 1]
        if c in rn.graph.get(b, {}):
            return b, c
    succ = rn.graph.get(b, {})
    return (b, next(iter(succ))) if succ else None


def _build(name, maneuver, chain_from, chain_to, ego_s0, v0, v_target, accel, decel, target_lane, horizon):
    t, v, s = speed_profile(v0, v_target, accel, decel, horizon)
    p_from, _ = chain_from.at(ego_s0 + s)
    if chain_to is chain_from:
        xy = p_from
    else:
        u = np.clip(t / LANE_CHANGE_T, 0.0, 1.0)
        w = (3 * u ** 2 - 2 * u ** 3)[:, None]     # smoothstep lateral blend
        p_to, _ = chain_to.at(chain_to.project(chain_from.at(ego_s0)[0][0]) + s)
        xy = (1 - w) * p_from + w * p_to
    d = np.gradient(xy, axis=0)
    heading = np.arctan2(d[:, 1], d[:, 0])
    still = np.linalg.norm(d, axis=1) < 1e-4       # stopped: keep the last moving heading
    for i in np.flatnonzero(still):
        heading[i] = heading[i - 1] if i > 0 else chain_from.at(ego_s0)[1][0]
    return Candidate(name, maneuver, tuple(target_lane), float(v_target), t, xy, heading, v)


def cruise_candidate(env, v_cruise, horizon):
    """Lane keep at ``v_cruise`` from the ego's state: the hazard-blind prefix policy that brings the ego
    to a decision point."""
    ego = env.agent
    chain = lane_chain(env, ego.lane_index, max(v_cruise, V_MAX) * horizon + 20.0)
    return _build("cruise", "keep", chain, chain, chain.project(ego.position), float(ego.speed), v_cruise, ACCEL, DECEL, ego.lane_index, horizon)


def generate_candidates(env, horizon=HORIZON):
    """The maneuver bank for the ego's current state. Returns a list of Candidates (5-6)."""
    ego = env.agent
    rn = env.engine.current_map.road_network
    a, b, k = ego.lane_index
    n_lanes = len(rn.graph[a][b])
    v0 = float(ego.speed)
    reach = max(v0, V_MAX) * horizon + 20.0

    here = lane_chain(env, (a, b, k), reach)
    s0 = here.project(ego.position)
    v_keep = max(v0, 3.0)
    out = [
        _build("keep", "keep", here, here, s0, v0, v_keep, ACCEL, DECEL, (a, b, k), horizon),
        _build("keep_fast", "keep", here, here, s0, v0, min(v0 + SPEED_UP, V_MAX), ACCEL, DECEL, (a, b, k), horizon),
        _build("decelerate", "decelerate", here, here, s0, v0, 0.5 * v0, ACCEL, DECEL, (a, b, k), horizon),
        _build("stop", "stop", here, here, s0, v0, 0.0, ACCEL, STOP_DECEL, (a, b, k), horizon),
    ]
    for name, kk in (("change_left", k - 1), ("change_right", k + 1)):
        if 0 <= kk < n_lanes:
            other = lane_chain(env, (a, b, kk), reach)
            out.append(_build(name, "change", here, other, s0, v0, v_keep, ACCEL, DECEL, (a, b, kk), horizon))
    return out
