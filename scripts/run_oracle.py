"""Generate candidates and oracle-score them over a grid of decision points.

    python scripts/run_oracle.py                              # all families, seeds 0-1, t_dec 0.5..6.0
    python scripts/run_oracle.py --family lane_blockage --seeds 5 --t 1.0 2.0 3.0
    python scripts/run_oracle.py --out out/oracle/run.jsonl   # one JSON record per decision point

Prints one line per decision: c*, how many candidates are safe, and whether
the scene is retained (at least one safe and one unsafe candidate).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cassvla.planning import Oracle  # noqa: E402
from cassvla.scenarios import FAMILIES  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--family", default=None)
p.add_argument("--seeds", type=int, default=2)
p.add_argument("--start-seed", type=int, default=0)
p.add_argument("--t", type=float, nargs="+", default=list(np.arange(0.5, 6.01, 0.5)), help="decision times (s)")
p.add_argument("--out", default=None, help="JSONL output path")
args = p.parse_args()

fams = [args.family] if args.family else list(FAMILIES)
out = None
if args.out:
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    out = open(args.out, "w")

totals = {}
for fam in fams:
    oracle = Oracle(fam, start_seed=args.start_seed, num_scenarios=args.seeds)
    n = kept = 0
    try:
        for seed in range(args.start_seed, args.start_seed + args.seeds):
            for t in args.t:
                t0 = time.time()
                rec = oracle.label(seed, round(float(t), 2))
                if out:
                    out.write(json.dumps(rec) + "\n")
                if "skipped" in rec:
                    print(f"{fam:24s} s{seed:<3d} t={t:4.1f}  skipped ({rec['skipped']}); later decisions for this seed skipped too")
                    break
                n += 1
                kept += rec["retained"]
                safe = "".join("S" if rec["metrics"][c]["safe"] else "." for c in rec["metrics"])
                print(f"{fam:24s} s{seed:<3d} t={t:4.1f} v={rec['ego']['speed']:4.1f}  c*={rec['c_star']:12s} safe={safe:6s} "
                      f"{'RETAIN' if rec['retained'] else '      '}  {time.time() - t0:.1f}s")
    finally:
        oracle.close()
    totals[fam] = (n, kept)

print(f"\n{'family':24s} {'decisions':>9s} {'retained':>8s}")
for fam, (n, kept) in totals.items():
    print(f"{fam:24s} {n:9d} {kept:8d}")
if out:
    out.close()
    print(f"\nwrote {args.out}")
