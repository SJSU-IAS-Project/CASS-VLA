"""Reproducible diagnosis of the prompted VLM (docs/vlm_failure_analysis.md).

    python scripts/vlm_probe.py --cache out/vlm_dev_fp32 --sweep out/sweep_dev --out out/vlm_probe/report.json
    python scripts/vlm_probe.py --cache out/vlm_dev_fp32 --sweep out/sweep_dev --frames out/frames_dev \
        --variants orig describe ped occl noschema forced --keys occluded_pedestrian/100_2.0 ... --out out/vlm_probe/report.json

From the cache it counts distinct replies, template copies ("roi|depth|collision|none" returned verbatim), "!!!"
replies, the query/occlusion/hazard answers, and the VLM's light answer against the true ego light. With --variants
it reruns chosen frames under prompt variants that separate perception from the decision. The report carries the
cache's model, revision and prompt hash.
"""
import argparse
import collections
import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
TEMPLATE = "roi|depth|collision|none"
LIGHT_NAMES = {"TRAFFIC_LIGHT_GREEN": "green", "TRAFFIC_LIGHT_YELLOW": "yellow", "TRAFFIC_LIGHT_RED": "red"}


def _key(family, seed, t_dec):
    return f"{family}/{int(seed)}_{float(t_dec):.1f}"


def summarize_replies(rows):
    raws = collections.Counter(r["raw"] for r in rows)
    hazards = collections.Counter(h for r in rows for h in r["hazards"])
    return dict(n=len(rows), distinct_replies=len(raws), top_replies=[[c, raw[:160]] for raw, c in raws.most_common(8)],
                template_copies=sum(TEMPLATE in r["raw"] for r in rows), bang_replies=sum(r["raw"].lstrip().startswith("!!!") for r in rows),
                parse_errors=sum(bool(r["parse_error"]) for r in rows), query_counts=dict(collections.Counter(r["query"] for r in rows)),
                occlusion_true=sum(bool(r["occlusion"]) for r in rows), hazards=dict(hazards.most_common(10)),
                query_by_family={f: dict(c) for f, c in _by_family(rows, "query").items()})


def _by_family(rows, field):
    out = collections.defaultdict(collections.Counter)
    for r in rows:
        out[r["key"].split("/")[0]][r[field]] += 1
    return out


def light_confusion(rows, records):
    truth = {_key(r["family"], r["seed"], r["t_dec"]): r["signals"].get("ego_status") for r in records if "signals" in r}
    conf, hit, n, none_n, none_green = collections.Counter(), 0, 0, 0, 0
    for r in rows:
        if r["key"] not in truth:
            continue
        t = truth[r["key"]]
        if t is None:
            none_n += 1
            none_green += r["light"] == "green"
            continue
        conf[f"{t} -> {r['light']}"] += 1
        n += 1
        hit += LIGHT_NAMES.get(t) == r["light"]
    return dict(confusion=dict(conf), accuracy=round(hit / n, 4) if n else None, n_with_light=n,
                no_light_families=dict(n=none_n, answered_green=none_green))


def variant_prompts():
    from cassvla.perception.vlm import MANEUVERS, build_prompt
    names = list(MANEUVERS)
    return {
        "orig": lambda sp: build_prompt(sp, names),
        "describe": lambda sp: "Describe this front-camera driving image. List every vehicle and every pedestrian you can see and where they are.",
        "ped": lambda sp: "Look at the road ahead. Is there a pedestrian anywhere in the image? Answer yes or no, then say where.",
        "occl": lambda sp: "Is any object (a parked car, a truck, a wall) blocking the view of the road ahead, so that something could be hidden behind it? "
                           "Answer yes or no, then explain briefly.",
        "noschema": lambda sp: build_prompt(sp, names).split("Reply with JSON only")[0]
        + "First list the hazards you see, then say which single query (roi, depth, collision or none) you would make and why.",
        "forced": lambda sp: build_prompt(sp, names).split("- none:")[0]
        + 'Reply with JSON only: {"hazards": [...], "occlusion": <true/false>, "light": <light colour>, "query": <one of roi, depth, collision>}',
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", required=True)
    p.add_argument("--sweep", nargs="+", required=True)
    p.add_argument("--frames", default=None)
    p.add_argument("--variants", nargs="*", default=[])
    p.add_argument("--keys", nargs="*", default=[])
    p.add_argument("--out", required=True)
    args = p.parse_args()
    from cassvla.perception.vlm import load_cache
    import numpy as np
    cache = load_cache(args.cache)
    rows = list(cache["prompted"].values())
    records = []
    for path in args.sweep:
        for f in (sorted(glob.glob(os.path.join(path, "*.jsonl"))) if os.path.isdir(path) else [path]):
            records += [json.loads(line) for line in open(f)]
    emb = cache["emb"]
    nan_keys = [k for k, e in zip(cache["keys"], emb) if not np.isfinite(e).all()] if len(emb) else []
    report = dict(model=cache["meta"].get("model"), revision=cache["meta"].get("revision"), prompt_hash=cache["meta"].get("prompt_hash"),
                  vision_dtype=cache["meta"].get("vision_dtype"), replies=summarize_replies(rows), light=light_confusion(rows, records),
                  nan_embeddings=dict(n=len(nan_keys), keys=nan_keys))
    if args.variants:
        from cassvla.perception.vlm import MLXBackend
        index = {json.loads(line)["key"]: json.loads(line) for line in open(os.path.join(args.frames, "index.jsonl"))}
        be, prompts = MLXBackend(), variant_prompts()
        report["variants"] = {}
        for k in args.keys:
            img = os.path.join(args.frames, index[k]["path"])
            report["variants"][k] = {v: be.ask(img, prompts[v](index[k]["ego"]["speed"]))[0].strip() for v in args.variants}
            print(k, flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(report, open(args.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "variants"}, indent=1)[:2500])


if __name__ == "__main__":
    main()
