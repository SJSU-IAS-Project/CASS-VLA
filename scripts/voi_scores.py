"""VoI scores for every retained decision in sweep records (cassvla/planning/voi.py), one JSON line per decision.

    OMP_NUM_THREADS=1 python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/v2_uniform.jsonl --priors uniform --procs 8
    OMP_NUM_THREADS=1 python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/v2_fitted.jsonl --priors out/voi/priors_fitted.json
    OMP_NUM_THREADS=1 python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/abl_no_rear.jsonl --classes null depth occl_static occl_ped light

The first line is {"config": {...}} (priors, draws, classes, levels, git sha). Each further line is
{"family", "seed", "t_dec", "levels": {level: {"voi": {tool: float}, "top_now": str}}, "seconds"}. --sim-level
simulates tool answers at one fixed level for every evaluated level (the noise-unaware ablation).
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
LEVELS = ("low", "mid", "high")


def sweep_files(paths):
    out = []
    for p in paths:
        out += sorted(glob.glob(os.path.join(p, "*.jsonl"))) if os.path.isdir(p) else [p]
    return [f for f in out if not f.endswith("summary.json")]


def load_priors(spec):
    from cassvla.planning.voi import UNIFORM
    if spec == "uniform":
        return dict(UNIFORM)
    p = json.load(open(spec))
    return dict(p.get("priors", p))


def score_file(task):
    path, cfg = task
    from cassvla.planning.voi import voi
    rows = []
    for line in open(path):
        rec = json.loads(line)
        if not rec.get("retained"):
            continue
        levels, secs = {}, 0.0
        for lv in cfg["levels"]:
            o = voi(rec, cfg["sim_level"] or lv, priors=cfg["priors"], draws=cfg["draws"], classes=tuple(cfg["classes"]))
            levels[lv] = dict(voi={t: round(v, 4) for t, v in o["voi"].items()}, top_now=o["top_now"])
            secs += o["seconds"]
        rows.append(dict(family=rec["family"], seed=rec["seed"], t_dec=rec["t_dec"], levels=levels, n_worlds=o["n_worlds"],
                         seconds=round(secs / len(cfg["levels"]), 4)))
    return rows


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return None


def main():
    from cassvla.planning.voi import CLASSES
    p = argparse.ArgumentParser()
    p.add_argument("--sweep", nargs="+", required=True, help="sweep directories or record files")
    p.add_argument("--out", required=True)
    p.add_argument("--levels", nargs="+", default=list(LEVELS))
    p.add_argument("--priors", default="uniform", help="'uniform' or a JSON file from voi_priors.py")
    p.add_argument("--draws", type=int, default=8)
    p.add_argument("--classes", nargs="+", default=list(CLASSES))
    p.add_argument("--sim-level", default=None, help="simulate tool answers at this level for every evaluated level")
    p.add_argument("--procs", type=int, default=8)
    args = p.parse_args()
    cfg = dict(priors=load_priors(args.priors), draws=args.draws, classes=args.classes, levels=args.levels, sim_level=args.sim_level,
               priors_source=args.priors, git_sha=git_sha())
    files = sweep_files(args.sweep)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    n, secs = 0, 0.0
    tasks = [(f, cfg) for f in files]
    with open(args.out, "w") as fh:
        fh.write(json.dumps(dict(config=cfg)) + "\n")
        results = map(score_file, tasks) if args.procs == 1 else mp.Pool(args.procs).imap_unordered(score_file, tasks)
        for rows in results:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
                secs += r["seconds"]
            n += len(rows)
            print(f"{n} decisions", flush=True)
    print(f"wrote {n} decisions to {args.out}; mean {secs / max(n, 1):.4f} s per decision per level", flush=True)


if __name__ == "__main__":
    main()
