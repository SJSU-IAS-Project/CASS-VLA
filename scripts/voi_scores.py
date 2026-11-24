"""VoI scores for every retained decision in sweep records (cassvla/planning/voi.py), one JSON line per decision.

    OMP_NUM_THREADS=1 python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/v2_uniform.jsonl --priors uniform --procs 8
    OMP_NUM_THREADS=1 python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/v2_fitted.jsonl --priors out/voi/priors_fitted.json
    OMP_NUM_THREADS=1 python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/abl_no_rear.jsonl --classes null depth occl_static occl_ped light

The first line is {"config": {...}} (priors, draws, classes, levels, git sha). Each further line is
{"family", "seed", "t_dec", "levels": {level: {"voi": {tool: float}, "top_now": str}}, "seconds"}. --sim-level
simulates tool answers at one fixed level for every evaluated level (the noise-unaware ablation). --vlm-yesno
(from cache_vlm.py --mode yesno) sets each decision's occlusion priors from the VLM: occl_static = occl_ped =
P(hidden) / 2; every retained decision must have a yes/no row.
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


def priors_for(priors, p_hidden):
    """The VLM's P(hidden road user), halved onto each occlusion class. These are relative weights next to the
    other classes (null 1.0, light, rear), so the occlusion share of the world weight is below P(hidden); see
    docs/voi_selector.md."""
    return dict(priors, occl_static=p_hidden / 2.0, occl_ped=p_hidden / 2.0)


def load_yesno(path):
    with open(path) as f:
        f.readline()
        return {r["key"]: r["p"]["hidden"] for r in map(json.loads, f)}


def score_file(task):
    path, cfg, yesno, seeds = task
    from cassvla.perception.frames import frame_key
    from cassvla.planning.voi import voi
    rows = []
    for line in open(path):
        rec = json.loads(line)
        if not rec.get("retained") or (seeds is not None and rec["seed"] not in seeds):
            continue
        priors = cfg["priors"] if yesno is None else priors_for(cfg["priors"], yesno[frame_key(rec["family"], rec["seed"], rec["t_dec"])])
        levels, secs = {}, 0.0
        for lv in cfg["levels"]:
            o = voi(rec, cfg["sim_level"] or lv, priors=priors, draws=cfg["draws"], classes=tuple(cfg["classes"]), world_model=cfg["world_model"])
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


def git_dirty():
    """True if tracked code differs from HEAD, so git_sha alone does not identify the code that made the file."""
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True).stdout
        return bool(out.strip())
    except OSError:
        return True


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
    p.add_argument("--world-model", default="compositional", choices=("compositional", "alternatives"))
    p.add_argument("--vlm-yesno", default=None, help="yes/no cache; its P(hidden) sets the occlusion priors per decision")
    p.add_argument("--manifest", default=None, help="with --splits: score only the seeds of these dataset splits")
    p.add_argument("--splits", nargs="*", default=None)
    p.add_argument("--procs", type=int, default=8)
    args = p.parse_args()
    cfg = dict(priors=load_priors(args.priors), draws=args.draws, classes=args.classes, levels=args.levels, sim_level=args.sim_level,
               priors_source=args.priors, world_model=args.world_model, git_sha=git_sha(), git_dirty=git_dirty())
    files = sweep_files(args.sweep)
    seeds = None
    if args.manifest:
        man = json.load(open(args.manifest))["splits"]
        seeds = {s for sp in (args.splits or list(man)) for s in man[sp]}
        cfg["splits"] = args.splits
    yesno = None
    if args.vlm_yesno:
        from cassvla.perception.frames import frame_key
        yesno = load_yesno(args.vlm_yesno)
        keys = [frame_key(r["family"], r["seed"], r["t_dec"]) for f in files for r in map(json.loads, open(f))
                if r.get("retained") and (seeds is None or r["seed"] in seeds)]
        miss = [k for k in keys if k not in yesno]
        if miss:
            raise SystemExit(f"{len(miss)} of {len(keys)} retained decisions have no yes/no row in {args.vlm_yesno} (e.g. {miss[:3]})")
        cfg["vlm_yesno"] = args.vlm_yesno
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    n, secs = 0, 0.0
    tasks = [(f, cfg, yesno, seeds) for f in files]
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
