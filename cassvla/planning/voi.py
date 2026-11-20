"""Training-free counterfactual value-of-information (VoI) tool selector.

For one decision, the selector weighs world hypotheses built from the base observation only
(``hypotheses.py``), simulates what each tool would report in each world, reruns the ranker on the merged
belief and scores the tool by the expected gain in ranker utility over not calling it:

    VoI(t) = sum_k w_k U(c_t,k, world_k) - sum_k w_k U(c_now, world_k)

``c_now`` is the ranker's pick from the base observation, ``c_t,k`` its pick after tool ``t`` answers in world
``k``, and ``U`` the ranker's own objective (score, minus ``UNSAFE_MARGIN_OFFSET`` when unsafe). A negative VoI
predicts a harmful call. Nothing privileged is read: no hidden actor, no ``c_star``, ``metrics``,
``oracle_order`` and no true light state (the pseudo-record carries each world's light instead).

    from cassvla.planning.voi import voi, select
    out = voi(rec, "mid")                      # {"voi": {tool: float}, "top_now", "n_worlds", "seconds"}
    score, tool_index, allow = select(out["voi"], lam=0.0)
"""
import math
import time

import numpy as np

from cassvla.planning.hypotheses import hypotheses
from cassvla.planning.ranker import UNSAFE_MARGIN_OFFSET, predicted_metrics, rank
from cassvla.planning.tools import TOOL_FNS, TOOLS, base_observation, in_camera, merge

CLASSES = ("null", "depth", "occl_static", "occl_ped", "light", "rear")
UNIFORM = {c: 1.0 for c in CLASSES}


def weighted_worlds(rec, base, priors, draws=8, classes=CLASSES):
    """[(weight, belief)]: each non-empty class gets its prior, renormalised, split evenly over its worlds."""
    hyp = hypotheses(rec, base, draws=draws)
    groups = {c: ([base] if c == "null" else hyp[c]) for c in classes}
    groups = {c: ws for c, ws in groups.items() if ws and priors.get(c, 0.0) > 0}
    total = sum(priors[c] for c in groups)
    if not groups or total <= 0:
        return [(1.0, base)]
    return [(priors[c] / total / len(ws), w) for c, ws in groups.items() for w in ws]


def _box(pos, heading, length, width):
    c, s = math.cos(heading), math.sin(heading)
    f, l = np.array([c, s]) * length / 2, np.array([-s, c]) * width / 2
    p = np.asarray(pos, float)
    return [list(p + f + l), list(p + f - l), list(p - f - l), list(p - f + l)]


def pseudo_record(rec, world, k, base):
    """A record in which ``world`` is the truth, for running the tool models on it, with its own noise stream.

    A visible actor keeps the polygon the ego observes (as ``features.py`` and ``hypotheses.py`` use it), moved
    by the world's offset from the base estimate, so occlusion in the world matches the occluded points the
    hypotheses were placed at. Hypothetical actors get a box from their pose."""
    # base["actors"] are the in-camera rec actors in order, and every world lists them first (names repeat, e.g. cones)
    observed = [a for a in rec["actors"] if in_camera(rec, a)]
    actors = []
    for i, a in enumerate(world["actors"]):
        pos = np.asarray(a["position"], float)
        if i < len(base["actors"]):
            poly = (np.asarray(observed[i]["poly"], float) + (pos - np.asarray(base["actors"][i]["position"], float))).tolist()
        else:
            poly = _box(pos, a["heading"], a["length"], a["width"])
        actors.append(dict(name=a["name"], type=a["type"], position=pos.tolist(), measured_velocity=[float(x) for x in a["velocity"]],
                           heading=float(a["heading"]), length=float(a["length"]), width=float(a["width"]), poly=poly))
    return dict(family=rec["family"], seed=f"{rec['seed']}|voi{k}", t_dec=rec["t_dec"], ego=rec["ego"], candidates=rec["candidates"],
                actors=actors, signals=dict(rec["signals"], ego_status=world["light"]))


def utility(cand, belief, stops):
    m = predicted_metrics(cand, belief, stops)
    return float(m["score"] - (0.0 if m["safe"] else UNSAFE_MARGIN_OFFSET))


def voi(rec, level, priors=UNIFORM, draws=8, classes=CLASSES):
    t0 = time.time()
    base = base_observation(rec)
    now = rank(rec, base)["top1"]
    cands = {c["name"]: c for c in rec["candidates"]}
    stops = [p[:2] for p in (rec["signals"].get("ego_stop_points") or {}).values()]
    worlds = weighted_worlds(rec, base, priors, draws, classes)
    u_now = [utility(cands[now], wd, stops) for _, wd in worlds]
    v_now = sum(w * u for (w, _), u in zip(worlds, u_now))
    pseudo = [pseudo_record(rec, wd, k, base) for k, (_, wd) in enumerate(worlds)]
    out = {}
    for t in TOOLS:
        v_t = 0.0
        for k, (w, wd) in enumerate(worlds):
            pick = rank(rec, merge(base, [TOOL_FNS[t](pseudo[k], level)]))["top1"]
            v_t += w * (u_now[k] if pick == now else utility(cands[pick], wd, stops))
        out[t] = float(v_t - v_now)
    return dict(voi=out, top_now=now, n_worlds=len(worlds), seconds=round(time.time() - t0, 4))


def select(voi_by_tool, lam=0.0):
    """-> (score, tool index into TOOLS, allow): call the best tool only if its VoI is above ``lam``."""
    vals = [voi_by_tool[t] for t in TOOLS]
    j = int(np.argmax(vals))
    return float(vals[j]), j, bool(vals[j] > lam)
