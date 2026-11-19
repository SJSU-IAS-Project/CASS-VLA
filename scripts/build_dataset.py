"""Turn a label sweep into the tool-discriminativeness dataset, split by seed.

    python scripts/build_dataset.py --sweep out/sweep --out out/dataset --procs 8

Writes <out>/{train,val,test}.jsonl and <out>/manifest.json. Records with no retained scene are dropped.
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SPLIT_SEED = 20261105


def split_seeds(seeds, fractions=(0.70, 0.15, 0.15)):
    seeds = sorted(set(int(s) for s in seeds))
    perm = np.random.default_rng(SPLIT_SEED).permutation(seeds)
    a = int(round(fractions[0] * len(perm)))
    b = a + int(round(fractions[1] * len(perm)))
    return dict(train=sorted(map(int, perm[:a])), val=sorted(map(int, perm[a:b])), test=sorted(map(int, perm[b:])))


def label_file(path):
    from cassvla.planning.labels import label_record
    out = []
    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("retained"):
                out.append(label_record(rec))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sweep", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--procs", type=int, default=8)
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.sweep, "*.jsonl")))
    with mp.get_context("spawn").Pool(args.procs) as pool:
        rows = [r for chunk in pool.imap_unordered(label_file, files) for r in chunk]
    rows.sort(key=lambda r: (r["family"], r["seed"], r["t_dec"]))
    all_seeds = set()
    for path in files:
        with open(path) as f:
            all_seeds.update(json.loads(line)["seed"] for line in f)
    splits = split_seeds(all_seeds)
    which = {s: k for k, v in splits.items() for s in v}
    counts = {}
    handles = {k: open(os.path.join(args.out, f"{k}.jsonl"), "w") for k in splits}
    for r in rows:
        k = which[r["seed"]]
        handles[k].write(json.dumps(r) + "\n")
        counts.setdefault(k, {}).setdefault(r["family"], 0)
        counts[k][r["family"]] += 1
    for h in handles.values():
        h.close()
    from cassvla.planning.features import AGNOSTIC_FEATURES, FEATURE_NAMES
    with open(os.path.join(args.out, "manifest.json"), "w") as f:
        json.dump(dict(sweep=args.sweep, splits=splits, counts=counts, feature_names=FEATURE_NAMES, agnostic_features=AGNOSTIC_FEATURES), f, indent=1)
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
