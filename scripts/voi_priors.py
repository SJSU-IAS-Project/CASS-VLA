"""Fitted VoI class priors: how often each hypothesis class is real, on the train-split seeds only.

    python scripts/voi_priors.py --sweep out/v2_sweep --manifest out/v2_dataset/manifest.json --out out/voi/priors_fitted.json

For each train decision where a class has worlds, the event is:
- occl_static / occl_ped: a vehicle / pedestrian the ego cannot see lies within ROI_MARGIN of an occluded point
- light: the light the ego could not read is not green
- rear: a real vehicle up to REAR_RANGE behind, in an adjacent lane
The prior is the event rate. null and depth stay 1.0. This reads hidden actors and the true light, which is
allowed here only: it is a calibration on training data, like fitting a model.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voi_scores import sweep_files  # noqa: E402

REAR_RANGE = 20.0
LANE_WIDTH = 3.5


def events(rec):
    from cassvla.planning import tools as T
    from cassvla.planning.hypotheses import hypotheses, occluded_points
    from cassvla.scenarios.signals import GREEN
    base = T.base_observation(rec)
    h = hypotheses(rec, base)
    seen = {id(a) for a in rec["actors"] if T.in_camera(rec, a)}
    hidden = [a for a in rec["actors"] if id(a) not in seen]
    out = {}
    pts = [np.asarray(p, float) for p, _ in occluded_points(rec, base)]

    def near(kind_ped):
        return any((a["type"] == "Pedestrian") == kind_ped and min(np.linalg.norm(np.asarray(a["position"], float) - q) for q in pts) <= T.ROI_MARGIN
                   for a in hidden)
    if h["occl_static"]:
        out["occl_static"], out["occl_ped"] = near(False), near(True)
    if h["light"]:
        out["light"] = rec["signals"].get("ego_status") != GREEN
    origin, heading = T._ego(rec)
    fwd, left = np.array([math.cos(heading), math.sin(heading)]), np.array([-math.sin(heading), math.cos(heading)])
    rear = False
    for a in rec["actors"]:
        r = np.asarray(a["position"], float) - origin
        lon, lat = float(r @ fwd), abs(float(r @ left))
        rear |= a["type"] != "Pedestrian" and -REAR_RANGE <= lon < 0 and LANE_WIDTH / 2 <= lat <= 1.5 * LANE_WIDTH
    out["rear"] = bool(rear)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sweep", nargs="+", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    train = set(json.load(open(args.manifest))["splits"]["train"])
    counts = {c: dict(n=0, k=0) for c in ("occl_static", "occl_ped", "light", "rear")}
    n_rec = 0
    for path in sweep_files(args.sweep):
        for line in open(path):
            rec = json.loads(line)
            if not rec.get("retained") or rec["seed"] not in train:
                continue
            n_rec += 1
            for c, hit in events(rec).items():
                counts[c]["n"] += 1
                counts[c]["k"] += int(hit)
    if n_rec == 0:
        raise SystemExit("no train records in the sweep for this manifest")
    priors = dict(null=1.0, depth=1.0, **{c: round(v["k"] / v["n"], 4) if v["n"] else 0.0 for c, v in counts.items()})
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(dict(priors=priors, counts=counts, n_train_decisions=n_rec), open(args.out, "w"), indent=1)
    print(json.dumps(priors))


if __name__ == "__main__":
    main()
