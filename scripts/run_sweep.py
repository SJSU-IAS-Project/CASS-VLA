"""Label many seeds in parallel, one process per (family, seed chunk), resumable.

    python scripts/run_sweep.py --out out/sweep --start-seed 100 --seeds 300 --procs 8
    python scripts/run_sweep.py --out out/grid --seeds 10 --procs 8 --t-grid 0.5 20.0

Finished chunks are written atomically to <out>/<family>_<seed>.jsonl and skipped on rerun.
summary.json holds decisions, retained, wall time, per-task peak memory and the code version.
"""
import argparse
import json
import multiprocessing as mp
import os
import resource
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)


def run_chunk(task):
    family, first, count, grid, path = task
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from cassvla.planning import Oracle
    from cassvla.scenarios import FAMILIES
    times = grid if grid else FAMILIES[family].decision_times()
    t0 = time.time()
    n = kept = 0
    oracle = Oracle(family, start_seed=first, num_scenarios=count)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w") as f:
            for seed in range(first, first + count):
                for t in times:
                    rec = oracle.label(seed, round(float(t), 2))
                    f.write(json.dumps(rec) + "\n")
                    if "skipped" in rec:
                        break
                    n += 1
                    kept += rec["retained"]
    finally:
        oracle.close()
    os.replace(tmp, path)
    return dict(family=family, first=first, decisions=n, retained=int(kept), wall=round(time.time() - t0, 1),
                peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1))


def mem_available_mb():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) / 1024
    return float("nan")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--start-seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--chunk", type=int, default=5)
    p.add_argument("--procs", type=int, default=8)
    p.add_argument("--family", nargs="*", default=None)
    p.add_argument("--t-grid", type=float, nargs=2, default=None, metavar=("LO", "HI"), help="use this 0.5 s grid instead of each family's window")
    p.add_argument("--min-free-mb", type=float, default=800.0, help="stop starting work below this much available memory")
    args = p.parse_args()

    from cassvla.scenarios import FAMILIES
    os.makedirs(args.out, exist_ok=True)
    grid = [round(float(t), 2) for t in np.arange(args.t_grid[0], args.t_grid[1] + 1e-9, 0.5)] if args.t_grid else None
    tasks = []
    for fam in args.family or list(FAMILIES):
        for first in range(args.start_seed, args.start_seed + args.seeds, args.chunk):
            count = min(args.chunk, args.start_seed + args.seeds - first)
            path = os.path.join(args.out, f"{fam}_{first}.jsonl")
            if not os.path.exists(path):
                tasks.append((fam, first, count, grid, path))

    t0 = time.time()
    done, low_mem = [], mem_available_mb()
    print(f"{len(tasks)} chunks, {args.procs} processes", flush=True)
    with mp.get_context("spawn").Pool(args.procs, maxtasksperchild=1) as pool:
        for res in pool.imap_unordered(run_chunk, tasks):
            done.append(res)
            low_mem = min(low_mem, mem_available_mb())
            print(f"[{len(done)}/{len(tasks)}] {res['family']} s{res['first']} n={res['decisions']} kept={res['retained']} "
                  f"{res['wall']}s rss={res['peak_rss_mb']}MB free={low_mem:.0f}MB t={time.time() - t0:.0f}s", flush=True)
            if low_mem < args.min_free_mb:
                pool.terminate()
                raise SystemExit(f"stopped: only {low_mem:.0f} MB available")
    wall = time.time() - t0
    n = sum(r["decisions"] for r in done)
    summary = dict(procs=args.procs, wall_s=round(wall, 1), decisions=n, retained=sum(r["retained"] for r in done),
                   decisions_per_hour=round(n / wall * 3600) if wall else 0, min_available_mb=round(low_mem),
                   max_rss_mb=max((r["peak_rss_mb"] for r in done), default=0),
                   git=subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                   dirty=bool(subprocess.run(["git", "-C", ROOT, "status", "--porcelain"], capture_output=True, text=True).stdout.strip()),
                   args=vars(args), chunks=done)
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print({k: summary[k] for k in ("procs", "wall_s", "decisions", "retained", "decisions_per_hour", "min_available_mb", "max_rss_mb")}, flush=True)


if __name__ == "__main__":
    main()
