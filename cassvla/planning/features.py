"""Selector inputs, computed only from what the ego has before any tool call."""
import numpy as np

from cassvla.planning.oracle import SAFE_CLEARANCE, SAFE_TTC
from cassvla.planning.tools import BASE_NOISE, CAMERA_RANGE, _ego, blocked, light_stop_distance
from cassvla.scenarios.signals import GREEN, RED, YELLOW

CANDIDATE_NAMES = ("keep", "keep_fast", "decelerate", "stop", "change_left", "change_right")
OCCLUSION_STEPS = 31
FEATURE_NAMES = (
    "ego_speed", "n_visible", "n_visible_ped", "nearest_visible", "light_known", "light_green", "light_yellow", "light_red", "has_stop", "stop_dist",
    "margin", "frac_pred_safe", "top_clearance", "top_ttc", "n_near_threshold", "range_uncertainty_near_top",
    "endpoint_spread", "progress_spread", "occl_top", "occl_mean", "occl_max", "stop_in_reach_light_unknown", "top_is_change",
    *[f"top_{n}" for n in CANDIDATE_NAMES],
)
AGNOSTIC_FEATURES = ("ego_speed", "n_visible", "n_visible_ped", "nearest_visible", "light_known", "light_green", "light_yellow", "light_red",
                     "has_stop", "stop_dist", "margin")


def _occluded_fraction(xy, origin, occluders):
    pts = xy[:OCCLUSION_STEPS:3]
    return float(np.mean([blocked(origin, p, occluders) for p in pts])) if occluders else 0.0


def selector_features(rec, base, ranked):
    origin, _ = _ego(rec)
    actors = base["actors"]
    occluders = [next(a["poly"] for a in rec["actors"] if a["name"] == b["name"]) for b in actors if b["length"] >= 3.0]
    paths = {c["name"]: np.asarray(c["xy"], float) for c in rec["candidates"]}
    m, top = ranked["metrics"], ranked["top1"]
    dists = [float(np.linalg.norm(a["position"] - origin)) for a in actors]
    stop = light_stop_distance(rec)
    light = base["light"]
    occl = {n: _occluded_fraction(p, origin, occluders) for n, p in paths.items()}
    ends = np.array([p[-1] for p in paths.values()])
    progress = [v["progress"] for v in m.values()]
    near = sum(abs(v["clearance"] - SAFE_CLEARANCE) < 1.0 or abs(v["ttc"] - SAFE_TTC) < 0.5 for v in m.values())
    unc = 0.0
    for a, d in zip(actors, dists):
        gap = float(np.min(np.linalg.norm(paths[top] - a["position"], axis=1)))
        sigma = max(BASE_NOISE["depth_rel"] * d, 0.5)
        unc = max(unc, float(np.exp(-gap / sigma)))
    reach = stop is not None and light is None and any(np.linalg.norm(p[-1] - origin) >= stop for p in paths.values())
    values = dict(
        ego_speed=rec["ego"]["speed"], n_visible=len(actors), n_visible_ped=sum(a["type"] == "Pedestrian" for a in actors),
        nearest_visible=min(dists + [CAMERA_RANGE]) / CAMERA_RANGE, light_known=float(light is not None), light_green=float(light == GREEN),
        light_yellow=float(light == YELLOW), light_red=float(light == RED), has_stop=float(stop is not None), stop_dist=min(stop if stop is not None else 100.0, 100.0) / 100.0,
        margin=float(np.log1p(max(ranked["margin"], 0.0))), frac_pred_safe=float(np.mean([v["safe"] for v in m.values()])),
        top_clearance=min(m[top]["clearance"], 20.0) / 20.0, top_ttc=min(m[top]["ttc"], 10.0) / 10.0, n_near_threshold=float(near),
        range_uncertainty_near_top=unc, endpoint_spread=float(np.max(np.linalg.norm(ends[:, None] - ends[None, :], axis=2))),
        progress_spread=float(max(progress) - min(progress)), occl_top=occl[top], occl_mean=float(np.mean(list(occl.values()))),
        occl_max=max(occl.values()), stop_in_reach_light_unknown=float(reach), top_is_change=float(top.startswith("change")),
        **{f"top_{n}": float(top == n) for n in CANDIDATE_NAMES})
    return [round(float(values[k]), 4) for k in FEATURE_NAMES]
