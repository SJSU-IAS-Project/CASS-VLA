"""Label each retained decision with every tool's expected correctness over several noise draws.

    python scripts/label_expected_gain.py --sweep out/v2_sweep --out out/v2_expgain.jsonl --draws 8 --procs 8

A single draw decides whether a noisy tool happens to fix a decision, and no selector can foresee that draw.
Training on the mean over draws removes that luck from the target. Extra draws use the level keys '<level>#k',
which share the level's noise parameters but get their own random stream. Each output line holds, per level and
tool, the fraction of draws in which the ranker's top candidate is c*.
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LEVELS = ("low", "mid", "high")


def label_file(task):
    path, draws = task
    from cassvla.planning import tools as T
    from cassvla.planning.ranker import rank
    for lv in LEVELS:
        for k in range(draws):
            T.LEVELS[f"{lv}#{k}"] = T.LEVELS[lv]
    out = []
    for line in open(path):
        rec = json.loads(line)
        if not rec.get("retained"):
            continue
        base = T.base_observation(rec)
        row = dict(family=rec["family"], seed=rec["seed"], t_dec=rec["t_dec"])
        for lv in LEVELS:
            row[lv] = {t: sum(rank(rec, T.merge(base, [T.TOOL_FNS[t](rec, f"{lv}#{k}")]))["top1"] == rec["c_star"]
                              for k in range(draws)) / draws for t in T.TOOLS}
        out.append(row)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sweep", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--draws", type=int, default=8)
    p.add_argument("--procs", type=int, default=8)
    args = p.parse_args()
    files = sorted(glob.glob(os.path.join(args.sweep, "*.jsonl")))
    n = 0
    with mp.Pool(args.procs) as pool, open(args.out, "w") as f:
        for rows in pool.imap_unordered(label_file, [(path, args.draws) for path in files]):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            n += len(rows)
            print(f"{n} decisions", flush=True)


if __name__ == "__main__":
    main()
