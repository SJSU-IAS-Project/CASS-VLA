"""Counterfactual flip features: does the ranker's top candidate change under answers a tool could give?

    python scripts/flip_features.py --sweep out/v2_sweep --out out/v3_flip/v2_sweep.jsonl --procs 8

Each feature reranks the candidates under hypotheses built only from the base observation, the ego state and the
map, so nothing privileged enters. flip_depth resamples the range and velocity of visible actors with the base
noise. flip_occl_static and flip_occl_ped place a stopped vehicle or a crossing pedestrian at occluded points on
the candidate paths. flip_light reranks an unread light as red and as green. flip_rear adds a fast vehicle behind
in each adjacent lane. The features were fixed on 2026-11-07 before any evaluation with them. The worlds come from
cassvla/planning/hypotheses.py, which the VoI selector shares.
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NAMES = ("flip_depth", "flip_occl_static", "flip_occl_ped", "flip_light", "flip_rear", "occl_points")
DRAWS = 8
MAX_POINTS = 6


def flip_row(rec):
    from cassvla.planning import tools as T
    from cassvla.planning.hypotheses import hypotheses
    from cassvla.planning.ranker import rank
    base = T.base_observation(rec)
    top = rank(rec, base)["top1"]

    def flips(beliefs):
        return float(np.mean([rank(rec, b)["top1"] != top for b in beliefs])) if beliefs else 0.0

    h = hypotheses(rec, base, draws=DRAWS, max_points=MAX_POINTS)
    light = float(rank(rec, h["light"][0])["top1"] != rank(rec, h["light"][1])["top1"]) if h["light"] else 0.0
    values = dict(flip_depth=flips(h["depth"]), flip_occl_static=flips(h["occl_static"]), flip_occl_ped=flips(h["occl_ped"]), flip_light=light,
                  flip_rear=flips(h["rear"]), occl_points=len(h["occl_static"]) / MAX_POINTS)
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
