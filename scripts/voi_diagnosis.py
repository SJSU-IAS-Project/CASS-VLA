"""Why VoI falls short: how its scores track the true expected gain, plus on-device latencies.

    OMP_NUM_THREADS=1 python scripts/voi_diagnosis.py --voi out/voi/v2_fitted.jsonl --data out/v2_dataset --split val \
        --expgain out/v2_expgain.jsonl --vlm-profile out/vlm_dev_fp32/profile.json --out out/voi_eval/diagnosis.json

Per noise level: the base ranker's accuracy, AUROC of the best VoI (and of minus the ranker margin) for "some tool has
a positive expected gain", the per-tool Spearman correlation between VoI and expected gain, and how often VoI's tool
is the best one when some tool helps. Latency: the learned selector's MLP forward pass (timed here, same shape as
fit_mlp: 32 hidden units), VoI seconds per decision from the score file, and the VLM profile.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from eval_vlm_yesno import auroc  # noqa: E402
from eval_voi import key, load_voi  # noqa: E402

TOOLS = ("roi", "depth", "collision")
LEVELS = ("low", "mid", "high")


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def diagnose(voi, gain, base_correct, margin):
    """voi, gain: (N, 3); base_correct, margin: (N,)."""
    helped = gain.max(axis=1) > 0
    return dict(base_correct_rate=round(float(np.mean(base_correct)), 4),
                auroc_maxvoi_any_gain=round(auroc(voi.max(axis=1), helped), 4),
                auroc_neg_margin_any_gain=round(auroc(-np.asarray(margin), helped), 4),
                spearman_per_tool=[round(spearman(voi[:, j], gain[:, j]), 4) for j in range(gain.shape[1])],
                tool_optimal_when_gain=round(float((voi.argmax(axis=1) == gain.argmax(axis=1))[helped].mean()), 4))


def mlp_forward_seconds(n_features, hidden=32, reps=20000):
    rng = np.random.default_rng(0)
    w1, w2, x = rng.normal(size=(n_features, hidden)), rng.normal(size=(hidden, 3)), rng.normal(size=(1, n_features))
    t0 = time.perf_counter()
    for _ in range(reps):
        np.maximum(x @ w1, 0.0) @ w2
    return (time.perf_counter() - t0) / reps


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--voi", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--split", default="val")
    p.add_argument("--expgain", required=True)
    p.add_argument("--vlm-profile", default=None)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    from cassvla.planning.features import FEATURE_NAMES
    rows = [json.loads(line) for line in open(os.path.join(a.data, f"{a.split}.jsonl"))]
    eg = {key(r): r for r in map(json.loads, open(a.expgain))}
    vrows = load_voi(a.voi)
    v = {key(r): r for r in vrows}
    base = np.array([float(r["no_tool"]["correct"]) for r in rows])
    margin = np.array([r["features"][FEATURE_NAMES.index("margin")] for r in rows])
    out = dict(voi_file=a.voi, split=a.split, n=len(rows), levels={})
    for lv in LEVELS:
        gain = np.array([[eg[key(r)][lv][t] for t in TOOLS] for r in rows]) - base[:, None]
        voi = np.array([[v[key(r)]["levels"][lv]["voi"][t] for t in TOOLS] for r in rows])
        out["levels"][lv] = diagnose(voi, gain, base, margin)
    lat = {"Learned selector (MLP forward pass)": round(mlp_forward_seconds(len(FEATURE_NAMES)), 7),
           "VoI selector (per decision, per noise level)": round(float(np.mean([r["seconds"] for r in vrows])), 4)}
    if a.vlm_profile:
        prof = json.load(open(a.vlm_profile))
        lat["VLM embedding (float32)"] = prof["embed"]["mean_s"]
        lat["VLM prompted answer (float32)"] = prof["ask"]["mean_s"]
    out["latency_s"] = lat
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    json.dump(lat, open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "latency.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
