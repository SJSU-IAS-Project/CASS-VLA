"""Ablations of the PlanDiscrim selector, on a dataset from build_dataset.py (and optionally a VLM cache).

    python scripts/ablations.py --data out/dataset --split val --out out/eval/ablations
    python scripts/ablations.py --data out/dataset --split val --out out/eval/ablations --vlm out/vlm --tool-costs roi=3 depth=1 collision=0.5

Every variant trains on the train split and is scored on --split with the same ranker, tools and budgets as
eval_baselines.py, whose functions this script reuses. The score is the mean top-1 accuracy over budgets
0 to 1 tool call per decision (the area under the accuracy-budget curve), with a 95% seed-bootstrap interval,
and the difference from the reference variant (full geometry features, logistic heads, exact match) with
its own interval. Writes <out>/<split>.json, which make_figures.py --ablations plots.

Variants:
- feature groups: trajectory-conditioned features removed (scene-only), and each group dropped in turn
- VLM: + embedding, + prompted answers, VLM features only (needs --vlm)
- selector model: gradient-boosted trees instead of logistic heads
- cost model: with --tool-costs, the same selector paying those costs (cost-unaware) and a cost-aware one that
  ranks by gain probability per unit cost, both scored on budgets in cost units. Compare these two with each
  other; their delta against the unit-cost reference mixes the selector with the cost model
- metric: tie-tolerant accuracy instead of exact match
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
_spec = importlib.util.spec_from_file_location("eval_baselines", os.path.join(ROOT, "scripts", "eval_baselines.py"))
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)

GROUPS = {
    "candidate geometry": ("endpoint_spread", "progress_spread", "top_is_change", "top_keep", "top_keep_fast", "top_decelerate", "top_stop",
                           "top_change_left", "top_change_right"),
    "occlusion of candidates": ("occl_top", "occl_mean", "occl_max", "stop_in_reach_light_unknown"),
    "ranker belief": ("frac_pred_safe", "top_clearance", "top_ttc", "n_near_threshold", "range_uncertainty_near_top"),
    "scene and light": ("ego_speed", "n_visible", "n_visible_ped", "nearest_visible", "light_known", "light_green", "light_yellow", "light_red",
                        "has_stop", "stop_dist"),
}


def fit_gbm(X, gain):
    from sklearn.ensemble import HistGradientBoostingClassifier
    models = []
    for j in range(gain.shape[1]):
        y = gain[:, j] > 0
        if y.all() or not y.any():
            models.append(float(y.mean()))
        else:
            models.append(HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0,
                                                         class_weight="balanced", random_state=0).fit(X, y))
    return models


def predict_gbm(models, X):
    return np.stack([np.full(len(X), m) if isinstance(m, float) else m.predict_proba(X)[:, 1] for m in models], axis=1)


def policy_curve(prob, a0, at, rng, costs=None, aware=True):
    """Per-decision accuracy (N, len(BUDGETS)) of querying the most promising decisions first.

    With ``costs`` (one per tool) a budget b allows b * N cost units in total, so a cheap tool lets the
    selector query more decisions. A cost-aware selector ranks by best gain probability per unit cost; a
    cost-unaware one picks as with unit costs but pays the given costs."""
    if costs is None:
        order, tool = ev.rank_desc(prob.max(axis=1), rng), prob.argmax(axis=1)
        return np.stack([ev.apply_policy(order, tool, a0, a0, at, at, b)[0] for b in ev.BUDGETS], axis=1)
    c = np.asarray(costs, float)
    per_cost = prob / c[None, :] if aware else prob
    tool = per_cost.argmax(axis=1)
    order = ev.rank_desc(per_cost.max(axis=1), rng)
    spent = np.cumsum(c[tool[order]])
    idx = np.arange(len(a0))
    out = []
    for b in ev.BUDGETS:
        k = int(np.searchsorted(spent, b * len(a0) + 1e-9, side="right"))
        q = np.zeros(len(a0), bool)
        q[order[:k]] = True
        out.append(np.where(q, at[idx, tool], a0))
    return np.stack(out, axis=1)


def score(per_dec, ref, seeds, rng):
    auc = per_dec.mean(axis=1)
    stats = ev.boot_stats(auc, seeds, rng)
    out = dict(auc=round(float(auc.mean()), 4), ci95=[round(float(np.percentile(stats, q)), 4) for q in (2.5, 97.5)],
               curve=[round(float(v), 4) for v in per_dec.mean(axis=0)])
    if ref is not None:
        d = auc - ref.mean(axis=1)
        ds = ev.boot_stats(d, seeds, rng)
        out.update(delta_vs_ref=round(float(d.mean()), 4), delta_ci95=[round(float(np.percentile(ds, q)), 4) for q in (2.5, 97.5)])
    return out


def run_level(train, test, level, names, agnostic, vlm, costs):
    Xtr = np.array([r["features"] for r in train], float)
    Xte = np.array([r["features"] for r in test], float)
    seeds = np.array([r["seed"] for r in test])
    col = {n: i for i, n in enumerate(names)}
    variants = []

    def add(name, label, Xa, Xb, key="correct", model="logistic", cost=None, aware=True, reference=False):
        a0, _, at, _, _, _ = ev.tables(test, level, key)
        a0_tr, _, at_tr, _, _, _ = ev.tables(train, level, key)
        gain = np.clip(at_tr - a0_tr[:, None], 0, 1)
        if model == "logistic":
            prob = ev.predict(ev.fit_selector(Xa, gain), Xb)
        else:
            prob = predict_gbm(fit_gbm(Xa, gain), Xb)
        per_dec = policy_curve(prob, a0, at, np.random.default_rng(0), cost, aware)
        variants.append(dict(name=name, label=label, per_dec=per_dec, reference=reference))

    add("reference", "Full geometry features (reference)", Xtr, Xte, reference=True)
    agn = [col[n] for n in names if n in agnostic]
    add("scene_only", "Scene-only (no trajectory conditioning)", Xtr[:, agn], Xte[:, agn])
    for g, members in GROUPS.items():
        keep = [i for n, i in col.items() if n not in members]
        add(f"drop_{g.replace(' ', '_')}", f"Drop {g}", Xtr[:, keep], Xte[:, keep])
    if vlm is not None:
        add("plus_vlm_embedding", "+ VLM embedding", np.hstack([Xtr, vlm["Etr"]]), np.hstack([Xte, vlm["Ete"]]))
        add("plus_vlm_prompted", "+ VLM prompted answers", np.hstack([Xtr, vlm["Ptr"]]), np.hstack([Xte, vlm["Pte"]]))
        add("vlm_only", "VLM features only", np.hstack([vlm["Etr"], vlm["Ptr"]]), np.hstack([vlm["Ete"], vlm["Pte"]]))
    try:
        import sklearn  # noqa: F401
        add("gbm", "Gradient-boosted trees selector", Xtr, Xte, model="gbm")
    except ImportError:
        print("scikit-learn not installed: skipping the gradient-boosting variant", flush=True)
    if costs is not None:
        add("unit_cost_aware", "Unit costs, scored in cost units", Xtr, Xte, cost=[1.0, 1.0, 1.0])
        tag = "/".join(f"{c:g}" for c in costs)
        add("weighted_cost_unaware", f"Costs {tag}, cost-unaware", Xtr, Xte, cost=costs, aware=False)
        add("weighted_cost_aware", f"Costs {tag}, cost-aware", Xtr, Xte, cost=costs)

    ref = variants[0]["per_dec"]
    out = []
    rng = np.random.default_rng(0)
    for v in variants:
        out.append(dict(name=v["name"], label=v["label"], reference=v["reference"],
                        **score(v["per_dec"], None if v["reference"] else ref, seeds, rng)))
    # tie-tolerant accuracy is a different metric, so it is reported against its own reference
    a0, _, at, _, _, _ = ev.tables(test, level, "correct_tol")
    a0_tr, _, at_tr, _, _, _ = ev.tables(train, level, "correct_tol")
    prob = ev.predict(ev.fit_selector(Xtr, np.clip(at_tr - a0_tr[:, None], 0, 1)), Xte)
    out.append(dict(name="tie_tolerant", label="Reference, tie-tolerant accuracy", reference=False,
                    **score(policy_curve(prob, a0, at, np.random.default_rng(0)), None, seeds, rng)))
    return out



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--split", default="val")
    p.add_argument("--out", required=True)
    p.add_argument("--vlm", default=None)
    p.add_argument("--vlm-pca", type=int, default=32)
    p.add_argument("--tool-costs", nargs="*", default=None, metavar="TOOL=COST", help="e.g. roi=3 depth=1 collision=0.5")
    p.add_argument("--levels", nargs="*", default=list(ev.LEVELS))
    args = p.parse_args()

    with open(os.path.join(args.data, "manifest.json")) as f:
        man = json.load(f)
    names, agnostic = man["feature_names"], tuple(man["agnostic_features"])
    train, test = ev.load(args.data, "train"), ev.load(args.data, args.split)
    costs = None
    if args.tool_costs:
        given = dict(kv.split("=") for kv in args.tool_costs)
        costs = [float(given.get(t, 1.0)) for t in ev.TOOLS]
    vlm = None
    if args.vlm:
        from cassvla.perception.vlm import load_cache
        from cassvla.perception.vlm_features import VLMFeatures
        vf = VLMFeatures(load_cache(args.vlm), n_pca=args.vlm_pca)
        train = [r for r, ok in zip(train, vf.covered(train)) if ok]
        test = [r for r, ok in zip(test, vf.covered(test)) if ok]
        vf.fit(train)
        k = len(vf.components)
        Ftr, Fte = vf.transform(train), vf.transform(test)
        vlm = dict(Etr=Ftr[:, :k], Ete=Fte[:, :k], Ptr=Ftr[:, k:], Pte=Fte[:, k:])
        print(f"VLM cache covers {len(train)} train and {len(test)} {args.split} rows", flush=True)

    per_level = {lv: run_level(train, test, lv, names, agnostic, vlm, costs) for lv in args.levels}
    ablations = [dict(name=v["name"], label=v["label"], levels={lv: {k: x for k, x in per_level[lv][i].items() if k not in ("name", "label")}
                                                                 for lv in args.levels})
                 for i, v in enumerate(per_level[args.levels[0]])]
    report = dict(split=args.split, n=len(test), n_seeds=len(set(r["seed"] for r in test)), tool_costs=costs, vlm=bool(vlm),
                  budgets=ev.BUDGETS.tolist(), ablations=ablations)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{args.split}.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=1)
    for a in ablations:
        cells = []
        for lv in args.levels:
            r = a["levels"][lv]
            d = f" d={r['delta_vs_ref']:+.3f} {r['delta_ci95']}" if "delta_vs_ref" in r else ""
            cells.append(f"{lv}: {r['auc']:.3f}{d}")
        print(f"{a['label'][:44]:44s} " + " | ".join(cells))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
