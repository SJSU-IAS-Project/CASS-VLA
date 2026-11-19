"""Render the ego's front-camera frame at each decision point, for the offline VLM pass.

    python scripts/render_frames.py --records out/dataset/test.jsonl --out out/frames
    python scripts/render_frames.py --records out/dataset/train.jsonl --per-family 500 --out out/frames
    python scripts/render_frames.py --family occluded_pedestrian --start-seed 100 --seeds 2 --t 1.5 2.5 --out out/frames

Records can be dataset rows (build_dataset.py) or sweep records (run_sweep.py); a directory means every
*.jsonl in it. Sweep records that are skipped or not retained are ignored. Frames go to
<out>/<family>/<seed>_<t_dec>.png and one line per frame is appended to <out>/index.jsonl. Frames that are
already in the index are skipped, so the script can be rerun after an interruption. All decisions of one
seed are rendered from a single rollout (FrameRenderer.render_seed), which is about 7x faster than one
reset per frame.
"""
import argparse
import glob
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def read_decisions(paths):
    out = []
    for path in paths:
        files = sorted(glob.glob(os.path.join(path, "*.jsonl"))) if os.path.isdir(path) else [path]
        for fp in files:
            with open(fp) as f:
                for line in f:
                    r = json.loads(line)
                    if "skipped" in r or not r.get("retained", True):
                        continue
                    out.append((r["family"], int(r["seed"]), round(float(r["t_dec"]), 2)))
    return sorted(set(out))


def stratify(decisions, per_family, seed):
    """At most ``per_family`` decisions from each family, drawn without replacement."""
    rng = np.random.default_rng(seed)
    by_fam = defaultdict(list)
    for d in decisions:
        by_fam[d[0]].append(d)
    out = []
    for fam in sorted(by_fam):
        items = by_fam[fam]
        idx = rng.permutation(len(items))[:per_family]
        out.extend(items[i] for i in sorted(idx))
    return out


def load_index(path):
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {json.loads(line)["key"] for line in f}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--records", nargs="*", default=None, help="dataset/sweep JSONL files or directories")
    p.add_argument("--family", nargs="*", default=None, help="with --seeds/--t: render a grid instead of records")
    p.add_argument("--start-seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--t", type=float, nargs="*", default=None, help="decision times for the grid (default: each family's window)")
    p.add_argument("--per-family", type=int, default=None, help="stratified subsample size per family")
    p.add_argument("--sample-seed", type=int, default=0)
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--height", type=int, default=360)
    args = p.parse_args()

    import cv2
    from cassvla.perception import FrameRenderer, frame_key
    from cassvla.scenarios import FAMILIES

    if args.records:
        decisions = read_decisions(args.records)
    else:
        decisions = []
        for fam in args.family or list(FAMILIES):
            times = args.t or FAMILIES[fam].decision_times()
            decisions += [(fam, s, round(float(t), 2)) for s in range(args.start_seed, args.start_seed + args.seeds) for t in times]
    if args.per_family:
        decisions = stratify(decisions, args.per_family, args.sample_seed)

    os.makedirs(args.out, exist_ok=True)
    index_path = os.path.join(args.out, "index.jsonl")
    done = load_index(index_path)
    todo = [d for d in decisions if frame_key(*d) not in done]
    print(f"{len(decisions)} decisions, {len(decisions) - len(todo)} already rendered, {len(todo)} to render", flush=True)

    by_fam = defaultdict(list)
    for d in todo:
        by_fam[d[0]].append(d)
    t_start, n = time.time(), 0
    with open(index_path, "a") as index:
        for fam, items in sorted(by_fam.items()):
            seeds = [s for _, s, _ in items]
            renderer = FrameRenderer(fam, start_seed=min(seeds), num_scenarios=max(seeds) - min(seeds) + 1, size=(args.width, args.height))
            per_seed = defaultdict(list)
            for _, seed, t_dec in items:
                per_seed[seed].append(t_dec)
            try:
                for seed, times in sorted(per_seed.items()):
                    got = 0
                    for out in renderer.render_seed(seed, times):
                        t_dec = out["t_dec"]
                        rel = os.path.join(fam, f"{seed}_{t_dec:.1f}.png")
                        os.makedirs(os.path.join(args.out, fam), exist_ok=True)
                        cv2.imwrite(os.path.join(args.out, rel), out["image"][..., ::-1])
                        index.write(json.dumps(dict(key=out["key"], family=fam, seed=seed, t_dec=t_dec, path=rel, ego=out["ego"],
                                                    seconds=out["seconds"], size=[args.width, args.height])) + "\n")
                        index.flush()
                        got += 1
                    if got < len(times):
                        print(f"{fam} s{seed}: prefix ended the episode, {len(times) - got} decisions skipped", flush=True)
                    n += got
            finally:
                renderer.close()
            print(f"{fam}: {len(items)} frames, {time.time() - t_start:.0f}s elapsed", flush=True)
    print(f"rendered {n} frames in {time.time() - t_start:.0f}s -> {args.out}")


if __name__ == "__main__":
    main()
