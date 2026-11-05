"""Rule-based candidate ranker. It scores candidates from a belief with the oracle's safety rules and
weights, using constant-velocity actor prediction and a disc approximation of each box."""
import numpy as np

from cassvla.planning.oracle import SAFE_CLEARANCE, SAFE_TTC, TTC_CAP, W_CLEARANCE, W_COLLISION, W_RED, W_TTC
from cassvla.scenarios.signals import RED, YELLOW

EGO_LENGTH, EGO_WIDTH = 4.515, 1.852
DT = 0.1
PEDESTRIAN_PRIOR_SPEED = 1.4
YELLOW_RED_AFTER = 1.5
STOP_LINE_RADIUS = 1.5
UNSAFE_MARGIN_OFFSET = 200.0


def _discs(length, width):
    offset = max(0.0, (length - width) / 2)
    return np.array([-offset, 0.0, offset]), width / 2


def predicted_metrics(cand, belief, stop_points):
    xy = np.asarray(cand["xy"], float)
    n = len(xy)
    t = DT * np.arange(n)
    d = np.gradient(xy, axis=0)
    norm = np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
    fwd = d / norm
    vel_e = d / DT
    off_e, rad_e = _discs(EGO_LENGTH, EGO_WIDTH)
    ego_c = xy[:, None, :] + off_e[None, :, None] * fwd[:, None, :]

    clearance, ttc = np.inf, TTC_CAP
    for a in belief["actors"]:
        v = np.asarray(a["velocity"], float)
        h = np.array([np.cos(a["heading"]), np.sin(a["heading"])])
        if a["type"] == "Pedestrian" and np.linalg.norm(v) < 0.1:
            v = PEDESTRIAN_PRIOR_SPEED * h
        off_a, rad_a = _discs(a["length"], a["width"])
        p = np.asarray(a["position"], float)[None, :] + t[:, None] * v[None, :]
        act_c = p[:, None, :] + off_a[None, :, None] * h[None, None, :]
        gaps = np.linalg.norm(ego_c[:, :, None, :] - act_c[:, None, :, :], axis=3) - rad_e - rad_a
        step_gap = np.maximum(gaps.min(axis=(1, 2)), 0.0)
        clearance = min(clearance, float(step_gap.min()))
        r = p - xy
        dist = np.maximum(np.linalg.norm(r, axis=1, keepdims=True), 1e-6)
        closing = -np.sum(r / dist * (v[None, :] - vel_e), axis=1)
        moving = closing > 1e-3
        if moving.any():
            ttc = min(ttc, float((step_gap[moving] / closing[moving]).min()))

    red = False
    if stop_points and belief.get("light") in (RED, YELLOW):
        pts = np.asarray(stop_points, float)
        near = np.min(np.linalg.norm(xy[:, None, :] - pts[None, :, :], axis=2), axis=1) <= STOP_LINE_RADIUS
        if near.any():
            red = belief["light"] == RED or float(t[np.argmax(near)]) >= YELLOW_RED_AFTER
    collision = clearance <= 0.0
    progress = float(np.sum(np.linalg.norm(np.diff(xy, axis=0), axis=1)))
    clearance_v = clearance if np.isfinite(clearance) else 99.0
    score = (progress - W_COLLISION * collision - W_RED * red
             - W_TTC * max(0.0, 1.5 * SAFE_TTC - ttc) - W_CLEARANCE * max(0.0, 2.0 * SAFE_CLEARANCE - clearance_v))
    safe = not (collision or red) and clearance_v >= SAFE_CLEARANCE and ttc >= SAFE_TTC
    return dict(clearance=clearance_v, ttc=ttc, red=red, progress=progress, score=score, safe=safe)


def rank(rec, belief):
    """Returns the candidate order (safe first, then score), per-candidate metrics, and the top-two margin."""
    stops = [p[:2] for p in (rec["signals"].get("ego_stop_points") or {}).values()]
    m = {c["name"]: predicted_metrics(c, belief, stops) for c in rec["candidates"]}
    order = sorted(m, key=lambda n: (not m[n]["safe"], -m[n]["score"]))
    effective = [m[n]["score"] - (0.0 if m[n]["safe"] else UNSAFE_MARGIN_OFFSET) for n in order]
    margin = float(effective[0] - effective[1]) if len(order) > 1 else float("inf")
    return dict(order=order, top1=order[0], margin=margin, metrics=m)
