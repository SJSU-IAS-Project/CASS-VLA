"""Counterfactual flip features: does the ranker's top candidate change under answers a tool could give?

    python scripts/flip_features.py --sweep out/v2_sweep --out out/v3_flip/v2_sweep.jsonl --procs 8

Each feature reranks the candidates under hypotheses built only from the base observation, the ego state and the
map, so nothing privileged enters. flip_depth resamples the range and velocity of visible actors with the base
noise. flip_occl_static and flip_occl_ped place a stopped vehicle or a crossing pedestrian at occluded points on
the candidate paths. flip_light reranks an unread light as red and as green. flip_rear adds a fast vehicle behind
in each adjacent lane. The features were fixed on 2026-11-07 before any evaluation with them.
"""
import argparse
import glob
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NAMES = ("flip_depth", "flip_occl_static", "flip_occl_ped", "flip_light", "flip_rear", "occl_points")
DRAWS = 8
MAX_POINTS = 6
LANE_WIDTH = 3.5


def _actor(name, kind, pos, vel, heading):
    length, width = (4.5, 1.9) if kind == "DefaultVehicle" else (0.5, 0.5)
    return dict(name=name, type=kind, position=np.asarray(pos, float), velocity=np.asarray(vel, float), heading=float(heading),
                length=length, width=width, source="hypothesis")


def flip_row(rec):
    from cassvla.planning import tools as T
    from cassvla.planning.ranker import rank
    from cassvla.scenarios.signals import GREEN, RED
    base = T.base_observation(rec)
    top = rank(rec, base)["top1"]
    rng = T.rng_for(rec, "flip")
    origin, heading = T._ego(rec)
    fwd = np.array([math.cos(heading), math.sin(heading)])
    left = np.array([-fwd[1], fwd[0]])

    def flips(beliefs):
        return float(np.mean([rank(rec, b)["top1"] != top for b in beliefs])) if beliefs else 0.0

    def with_actors(extra, **kw):
        return dict(base, actors=list(base["actors"]) + extra, **kw)

    depth = []
    for _ in range(DRAWS):
        acts = []
        for a in base["actors"]:
            r = a["position"] - origin
            d = float(np.linalg.norm(r))
            pos = a["position"] + (r / d * rng.normal(0.0, T.BASE_NOISE["depth_rel"] * d) if d > 1e-6 else 0.0)
            acts.append(dict(a, position=pos, velocity=a["velocity"] + rng.normal(0.0, T.BASE_NOISE["vel"], 2)))
        depth.append(dict(base, actors=acts))

    visible = {a["name"] for a in base["actors"]}
    occluders = [a["poly"] for a in rec["actors"] if a["name"] in visible and a["length"] >= T.MIN_OCCLUDER_LENGTH]
    points = []
    for c in rec["candidates"]:
        xy = np.asarray(c["xy"], float)
        for i in range(5, len(xy), 5):
            if np.linalg.norm(xy[i] - origin) <= T.CAMERA_RANGE and occluders and T.blocked(origin, xy[i], occluders):
                step = xy[i] - xy[i - 1]
                points.append((xy[i], math.atan2(step[1], step[0])))
    if len(points) > MAX_POINTS:
        points = [points[j] for j in np.linspace(0, len(points) - 1, MAX_POINTS).round().astype(int)]
    static = [with_actors([_actor("hyp", "DefaultVehicle", p, (0.0, 0.0), h)]) for p, h in points]
    ped = [with_actors([_actor("hyp", "Pedestrian", p, (0.0, 0.0), h + math.pi / 2)]) for p, h in points]

    light = 0.0
    if T.light_stop_distance(rec) is not None and base["light"] is None:
        light = float(rank(rec, dict(base, light=RED))["top1"] != rank(rec, dict(base, light=GREEN))["top1"])

    speed = float(rec["ego"]["speed"]) + 4.0
    rear = [with_actors([_actor("hyp", "DefaultVehicle", origin - 12.0 * fwd + s * LANE_WIDTH * left, speed * fwd, heading)]) for s in (1, -1)]
    values = dict(flip_depth=flips(depth), flip_occl_static=flips(static), flip_occl_ped=flips(ped), flip_light=light,
                  flip_rear=flips(rear), occl_points=len(points) / MAX_POINTS)
    return dict(family=rec["family"], seed=rec["seed"], t_dec=rec["t_dec"], flip=[round(values[k], 4) for k in NAMES])


def label_file(path):
    return [flip_row(rec) for rec in map(json.loads, open(path)) if rec.get("retained")]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sweep", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--procs", type=int, default=8)
    args = p.parse_args()
    files = sorted(glob.glob(os.path.join(args.sweep, "*.jsonl")))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    n = 0
    with mp.Pool(args.procs) as pool, open(args.out, "w") as f:
        f.write(json.dumps(dict(names=NAMES)) + "\n")
        for rows in pool.imap_unordered(label_file, files):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            n += len(rows)
            print(f"{n} decisions", flush=True)


if __name__ == "__main__":
    main()
