"""Run the VLM once over rendered frames and cache embeddings and prompted answers (Phase 5).

    pip install -r requirements-vlm.txt          # Apple Silicon only (mlx)
    python scripts/cache_vlm.py --frames out/frames --records out/dataset --out out/vlm
    python scripts/cache_vlm.py --frames out/frames --records out/dataset --out out/vlm --limit 20   # smoke test

Writes <out>/meta.json (model, revision, prompt hash), <out>/emb_*.npz (keys + embeddings),
<out>/prompted.jsonl (parsed answers plus the raw reply), <out>/timings.jsonl and <out>/profile.json.
Frames already in the cache are skipped. --records supplies each decision's candidate names for the prompt
(dataset rows or sweep records); without it the full maneuver bank is listed.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cassvla.perception.frames import frame_key  # noqa: E402
from cassvla.perception.vlm import DEFAULT_MODEL, MANEUVERS, cache_frames, summarize_timings  # noqa: E402


def candidate_names(paths):
    names = {}
    for path in paths or []:
        files = sorted(glob.glob(os.path.join(path, "*.jsonl"))) if os.path.isdir(path) else [path]
        for fp in files:
            with open(fp) as f:
                for line in f:
                    r = json.loads(line)
                    if "skipped" in r:
                        continue
                    cands = [c["name"] for c in r["candidates"]] if "candidates" in r else list(r.get("safe", {}))
                    if cands:
                        names[frame_key(r["family"], r["seed"], r["t_dec"])] = cands
    return names


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frames", required=True, help="directory written by render_frames.py")
    p.add_argument("--out", required=True)
    p.add_argument("--records", nargs="*", default=None)
    p.add_argument("--mode", choices=("both", "embed", "ask"), default="both")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--revision", default=None)
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()

    names = candidate_names(args.records)
    with open(os.path.join(args.frames, "index.jsonl")) as f:
        index = [json.loads(line) for line in f]
    frames = [dict(key=r["key"], path=r["path"], speed=r["ego"]["speed"], candidates=names.get(r["key"], list(MANEUVERS))) for r in index]
    frames = frames[:args.limit] if args.limit else frames
    missing = sum(r["key"] not in names for r in index[:len(frames)])
    print(f"{len(frames)} frames; {missing} without candidate names (full bank listed)", flush=True)

    from cassvla.perception.vlm import MLXBackend
    backend = MLXBackend(args.model, revision=args.revision)
    timings = cache_frames(frames, args.frames, backend, args.out, mode=args.mode)

    tpath = os.path.join(args.out, "timings.jsonl")
    with open(tpath, "a") as f:
        for t in timings:
            f.write(json.dumps(t) + "\n")
    with open(tpath) as f:
        everything = [json.loads(line) for line in f]
    profile = summarize_timings(everything, backend.peak_memory_gb())
    profile.update(model=backend.model_id, revision=backend.revision)
    with open(os.path.join(args.out, "profile.json"), "w") as f:
        json.dump(profile, f, indent=1)
    print(json.dumps(profile, indent=1))


if __name__ == "__main__":
    main()
