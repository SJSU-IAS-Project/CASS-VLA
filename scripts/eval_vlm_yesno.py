"""How well the VLM's yes/no probabilities detect what is really in front of the car (AUROC per question).

    python scripts/eval_vlm_yesno.py --yesno out/vlm_yesno/v2_valtest.jsonl --sweep out/v2_sweep --out out/vlm_yesno/eval.json

Truth comes from the sweep records (privileged, used only for scoring):
- pedestrian: a pedestrian within camera range and field of view, whether visible or hidden; pedestrian_visible
  and pedestrian_hidden split it by line of sight
- hidden: some actor within camera range and field of view has no line of sight from the ego
- red_light: the ego's light is red or yellow and a stop line is ahead
AUROC is reported overall and per family, with a 95% bootstrap interval over scenario seeds (1000 resamples).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
N_BOOT = 1000
PAIRS = (("pedestrian", "pedestrian"), ("pedestrian", "pedestrian_visible"), ("pedestrian", "pedestrian_hidden"),
         ("hidden", "hidden"), ("red_light", "red_light"))


def _in_view(rec, a):
    from cassvla.planning import tools as T
    origin, heading = T._ego(rec)
    r = np.asarray(a["position"], float) - origin
    bearing = abs((math.atan2(r[1], r[0]) - heading + math.pi) % (2 * math.pi) - math.pi)
    return float(np.linalg.norm(r)) <= T.CAMERA_RANGE and bearing <= T.CAMERA_HALF_FOV


def truth(rec):
    from cassvla.planning import tools as T
    from cassvla.scenarios.signals import RED, YELLOW
    view = [a for a in rec["actors"] if _in_view(rec, a)]
    los = {id(a): T.line_of_sight(rec, a) for a in view}
    peds = [a for a in view if a["type"] == "Pedestrian"]
    return dict(pedestrian=bool(peds), pedestrian_visible=any(los[id(a)] for a in peds), pedestrian_hidden=any(not los[id(a)] for a in peds),
                hidden=any(not los[id(a)] for a in view),
                red_light=bool(rec["signals"].get("ego_status") in (RED, YELLOW) and T.light_stop_distance(rec) is not None))


def auroc(p, y):
    """Mann-Whitney AUROC with ties counted half. None when only one class is present."""
    p, y = np.asarray(p, float), np.asarray(y, bool)
    pos, neg = p[y], p[~y]
    if len(pos) == 0 or len(neg) == 0:
        return None
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    allv = np.concatenate([pos, neg])[order]
    ranks = np.empty(len(allv))
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1] == allv[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2 + 1
        i = j + 1
    r = np.empty(len(allv))
    r[order] = ranks
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def seed_ci(p, y, seeds, rng):
    uniq = np.unique(seeds)
    groups = {s: np.where(seeds == s)[0] for s in uniq}
    stats = []
    for _ in range(N_BOOT):
        idx = np.concatenate([groups[s] for s in rng.choice(uniq, len(uniq))])
        a = auroc(p[idx], y[idx])
        if a is not None:
            stats.append(a)
    return [round(float(np.percentile(stats, q)), 4) for q in (2.5, 97.5)] if stats else None


def main():
    from cassvla.perception.frames import frame_key
    ap = argparse.ArgumentParser()
    ap.add_argument("--yesno", nargs="+", required=True)
    ap.add_argument("--sweep", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    probs, header = {}, None
    for path in args.yesno:
        with open(path) as f:
            header = json.loads(f.readline())["header"]
            for line in f:
                r = json.loads(line)
                probs[r["key"]] = r["p"]
    rows = []
    for d in args.sweep:
        for f in (sorted(glob.glob(os.path.join(d, "*.jsonl"))) if os.path.isdir(d) else [d]):
            for line in open(f):
                rec = json.loads(line)
                k = frame_key(rec["family"], rec["seed"], rec["t_dec"])
                if rec.get("retained") and k in probs:
                    rows.append((rec["family"], int(rec["seed"]), probs[k], truth(rec)))
    if not rows:
        raise SystemExit("no sweep record matches a yes/no row")
    rng = np.random.default_rng(0)
    fams = np.array([r[0] for r in rows])
    seeds = np.array([r[1] for r in rows])
    out = dict(header=header, n=len(rows), questions={})
    for q, t in PAIRS:
        p = np.array([r[2][q] for r in rows])
        y = np.array([r[3][t] for r in rows])
        per_fam = {f: auroc(p[fams == f], y[fams == f]) for f in sorted(set(fams))}
        out["questions"][f"{q} vs {t}"] = dict(auroc=auroc(p, y), ci95=seed_ci(p, y, seeds, rng), positives=int(y.sum()),
                                               mean_p_pos=round(float(p[y].mean()), 4) if y.any() else None,
                                               mean_p_neg=round(float(p[~y].mean()), 4) if (~y).any() else None,
                                               by_family={f: (round(a, 4) if a is not None else None) for f, a in per_fam.items()})
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)
    for k, v in out["questions"].items():
        print(f"{k:32s} AUROC {v['auroc']} {v['ci95']} positives {v['positives']}/{len(rows)}")


if __name__ == "__main__":
    main()
