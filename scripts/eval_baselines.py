"""Accuracy against query cost for the selection policies, on a dataset from build_dataset.py.

    python scripts/eval_baselines.py --data out/dataset --split test --out out/eval
    python scripts/eval_baselines.py --data out/dataset --split val --out out/eval --vlm out/vlm   # + VLM selectors

Every policy shares the same ranker and tools. Without --vlm the selectors use geometry features only.
With --vlm (a cache from scripts/cache_vlm.py) every method is restricted to the decisions that have a
cached frame, and three VLM selectors are added: VLM features only, geometry + VLM features, and the
VLM's own prompted query choice. A VLM selector calls the VLM on every decision, so its curves carry a
``cost_offset`` of --vlm-cost calls per decision on top of the tool budget.

Each comparison reports a 95% seed-bootstrap interval, a two-sided bootstrap p-value and a Holm-adjusted
p-value over all comparisons at the same noise level and metric.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOOLS = ("roi", "depth", "collision")
BUDGETS = np.round(np.arange(0.0, 1.0001, 0.05), 2)
LEVELS = ("low", "mid", "high")
N_RANDOM, N_BOOT = 50, 1000


def load(data, split):
    with open(os.path.join(data, f"{split}.jsonl")) as f:
        return [json.loads(line) for line in f]


def tables(rows, level, key):
    a0 = np.array([r["no_tool"][key] for r in rows], float)
    u0 = np.array([r["no_tool"]["unsafe"] for r in rows], float)
    at = np.array([[r["levels"][level]["tools"][t][key] for t in TOOLS] for r in rows], float)
    ut = np.array([[r["levels"][level]["tools"][t]["unsafe"] for t in TOOLS] for r in rows], float)
    aa = np.array([r["levels"][level]["always_on"][key] for r in rows], float)
    ua = np.array([r["levels"][level]["always_on"]["unsafe"] for r in rows], float)
    return a0, u0, at, ut, aa, ua


def fit_logistic(X, y, l2=1.0, steps=800, lr=0.2):
    w, b = np.zeros(X.shape[1]), 0.0
    pos = max(y.mean(), 1e-3)
    weight = np.where(y > 0, 0.5 / pos, 0.5 / max(1 - pos, 1e-3))
    for _ in range(steps):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        g = weight * (p - y)
        w -= lr * (X.T @ g / len(y) + l2 * w / len(y))
        b -= lr * g.mean()
    return w, b


def fit_selector(Xtr, gain):
    mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0) + 1e-6
    models = [fit_logistic((Xtr - mu) / sd, gain[:, j]) for j in range(gain.shape[1])]
    return mu, sd, models


def predict(model, X):
    mu, sd, models = model
    Z = (X - mu) / sd
    return np.stack([1 / (1 + np.exp(-(Z @ w + b))) for w, b in models], axis=1)


def rank_desc(values, rng):
    """Indices from highest to lowest value, with ties in random order instead of file order."""
    perm = rng.permutation(len(values))
    return perm[np.argsort(-values[perm], kind="stable")]


def gain_ci(a_order, a_tool, b_order, b_tool, a0, u0, at, ut, seeds, rng):
    diffs = []
    for b in BUDGETS[1:]:
        diffs.append(apply_policy(a_order, a_tool, a0, u0, at, ut, b)[0] - apply_policy(b_order, b_tool, a0, u0, at, ut, b)[0])
    mean = np.mean(diffs, axis=0)
    stats = boot_stats(mean, seeds, rng)
    # two-sided bootstrap p-value; it cannot resolve below 1 / N_BOOT, so it is floored there
    p = max(2 * min(float(np.mean(stats <= 0)), float(np.mean(stats >= 0))), 1.0 / N_BOOT)
    return dict(mean_acc_gain=round(float(mean.mean()), 4), ci95_by_seed=[round(float(np.percentile(stats, q)), 4) for q in (2.5, 97.5)],
                p_boot=round(min(p, 1.0), 4))


def holm(comparisons):
    """Add a Holm-adjusted ``p_holm`` to each comparison dict, in place."""
    names = sorted(comparisons, key=lambda k: comparisons[k]["p_boot"])
    running = 0.0
    for i, k in enumerate(names):
        running = max(running, min(1.0, (len(names) - i) * comparisons[k]["p_boot"]))
        comparisons[k]["p_holm"] = round(running, 4)
    return comparisons


def apply_policy(order, tool, a0, u0, at, ut, budget):
    """Query the ``budget`` fraction of scenes that rank first in ``order``, using ``tool`` per scene."""
    k = int(round(budget * len(a0)))
    q = np.zeros(len(a0), bool)
    q[order[:k]] = True
    idx = np.arange(len(a0))
    acc = np.where(q, at[idx, tool], a0)
    uns = np.where(q, ut[idx, tool], u0)
    return acc, uns


def curve(order, tool, a0, u0, at, ut):
    return [tuple(x.mean() for x in apply_policy(order, tool, a0, u0, at, ut, b)) for b in BUDGETS]


def boot_stats(diff, seeds, rng):
    """Mean of ``diff`` over N_BOOT resamples of whole seeds (decisions of one seed are not independent)."""
    uniq = np.unique(seeds)
    per = np.array([diff[seeds == s].sum() for s in uniq])
    cnt = np.array([(seeds == s).sum() for s in uniq])
    stats = []
    for _ in range(N_BOOT):
        i = rng.integers(len(uniq), size=len(uniq))
        stats.append(per[i].sum() / max(cnt[i].sum(), 1))
    return np.array(stats)


def seed_boot(diff, seeds, rng):
    return [round(float(np.percentile(boot_stats(diff, seeds, rng), q)), 4) for q in (2.5, 97.5)]


def evaluate(train, test, level, key, agnostic_idx, vlm=None):
    a0, u0, at, ut, aa, ua = tables(test, level, key)
    a0_tr, _, at_tr, _, _, _ = tables(train, level, key)
    Xtr = np.array([r["features"] for r in train], float)
    Xte = np.array([r["features"] for r in test], float)
    seeds = np.array([r["seed"] for r in test])
    margin_col = agnostic_idx["margin"]
    idx = np.arange(len(a0))
    rng = np.random.default_rng(0)

    gain_tr = np.clip(at_tr - a0_tr[:, None], 0, 1)
    best_tool = int(np.argmax(at_tr.mean(axis=0)))
    margin_order = rank_desc(-Xte[:, margin_col], rng)

    results = {}
    results["uncertainty_margin"] = curve(margin_order, np.full(len(a0), best_tool), a0, u0, at, ut)

    runs = []
    for _ in range(N_RANDOM):
        runs.append(curve(rng.permutation(len(a0)), rng.integers(3, size=len(a0)), a0, u0, at, ut))
    results["random"] = [tuple(x) for x in np.mean(runs, axis=0)]

    model = fit_selector(Xtr, gain_tr)
    prob = predict(model, Xte)
    pd_order, pd_tool = rank_desc(prob.max(axis=1), rng), prob.argmax(axis=1)
    results["plandiscrim_geometry"] = curve(pd_order, pd_tool, a0, u0, at, ut)

    agn_cols = list(agnostic_idx.values())
    model_a = fit_selector(Xtr[:, agn_cols], gain_tr)
    prob_a = predict(model_a, Xte[:, agn_cols])
    scene_order, scene_tool = rank_desc(prob_a.max(axis=1), rng), prob_a.argmax(axis=1)
    results["scene_only_learned"] = curve(scene_order, scene_tool, a0, u0, at, ut)

    gain = at - a0[:, None]
    fixes = gain.max(axis=1) > 0
    best = gain.argmax(axis=1)
    oracle_order = rank_desc(fixes.astype(float), rng)
    oracle_acc = np.where(fixes, at[idx, best], a0)
    assert np.all(oracle_acc >= a0) and np.all(oracle_acc >= at.max(axis=1))
    n_fix = int(fixes.sum())
    results["oracle"] = [tuple(x.mean() for x in apply_policy(oracle_order[:n_fix], best, a0, u0, at, ut, min(b, n_fix / len(a0)))) for b in BUDGETS]
    accs = [pt[0] for pt in results["oracle"]]
    assert all(y >= x - 1e-9 for x, y in zip(accs, accs[1:]))

    fixed = np.full(len(a0), best_tool)
    vs_margin = gain_ci(pd_order, pd_tool, margin_order, fixed, a0, u0, at, ut, seeds, rng)
    vs_scene = gain_ci(pd_order, pd_tool, scene_order, scene_tool, a0, u0, at, ut, seeds, rng)

    comparisons = dict(plandiscrim_minus_uncertainty=vs_margin, plandiscrim_minus_scene_only=vs_scene)
    cost_offset, vlm_report = {}, None
    if vlm is not None:
        # separate generator, so adding VLM methods never changes the numbers of the methods above
        vrng = np.random.default_rng(1)
        for name, Xa, Xb in (("plandiscrim_vlm_only", vlm["Xtr"], vlm["Xte"]),
                             ("plandiscrim_geom_vlm", np.hstack([Xtr, vlm["Xtr"]]), np.hstack([Xte, vlm["Xte"]]))):
            pv = predict(fit_selector(Xa, gain_tr), Xb)
            o, t = rank_desc(pv.max(axis=1), vrng), pv.argmax(axis=1)
            results[name] = curve(o, t, a0, u0, at, ut)
            cost_offset[name] = vlm["cost"]
            if name == "plandiscrim_geom_vlm":
                comparisons["geom_vlm_minus_geometry"] = gain_ci(o, t, pd_order, pd_tool, a0, u0, at, ut, seeds, vrng)
                comparisons["geom_vlm_minus_uncertainty"] = gain_ci(o, t, margin_order, fixed, a0, u0, at, ut, seeds, vrng)
        asked = vlm["tool_te"] >= 0
        v_order = rank_desc(asked.astype(float), vrng)
        v_tool = np.where(asked, vlm["tool_te"], best_tool)
        results["vlm_prompted"] = curve(v_order, v_tool, a0, u0, at, ut)
        cost_offset["vlm_prompted"] = vlm["cost"]
        comparisons["vlm_prompted_minus_uncertainty"] = gain_ci(v_order, v_tool, margin_order, fixed, a0, u0, at, ut, seeds, vrng)
        vlm_report = dict(asked_rate=round(float(asked.mean()), 3),
                          asked_tool_rate={t: round(float((vlm["tool_te"] == j).mean()), 3) for j, t in enumerate(TOOLS)},
                          asked_precision=round(float((at[idx, v_tool] > a0)[asked].mean()), 3) if asked.any() else None,
                          abstain_precision=round(float((~fixes)[~asked].mean()), 3) if (~asked).any() else None)
    holm(comparisons)

    pred_q = prob.max(axis=1) >= 0.5
    abstain_truth = ~fixes
    tp = int(np.sum(~pred_q & abstain_truth))
    prec = tp / max(int(np.sum(~pred_q)), 1)
    rec_ab = tp / max(int(abstain_truth.sum()), 1)

    fam = {}
    famkeys = sorted({r["family"] for r in test})
    fams = np.array([r["family"] for r in test])
    for f in famkeys:
        m = fams == f
        o_p = pd_order
        acc_p, _ = apply_policy(o_p, pd_tool, a0, u0, at, ut, 0.5)
        acc_u, _ = apply_policy(margin_order, np.full(len(a0), best_tool), a0, u0, at, ut, 0.5)
        fam[f] = dict(n=int(m.sum()), no_tool=round(float(a0[m].mean()), 3), always_on=round(float(aa[m].mean()), 3), oracle=round(float(oracle_acc[m].mean()), 3),
                      plandiscrim_b50=round(float(acc_p[m].mean()), 3), uncertainty_b50=round(float(acc_u[m].mean()), 3),
                      tool_rate={t: round(float((pred_q & (pd_tool == j))[m].mean()), 3) for j, t in enumerate(TOOLS)},
                      best_single={t: round(float(at[m, j].mean()), 3) for j, t in enumerate(TOOLS)})
    return dict(
        n=len(test), n_seeds=len(np.unique(seeds)), budgets=BUDGETS.tolist(), best_agnostic_tool=TOOLS[best_tool],
        no_tool=dict(acc=round(float(a0.mean()), 4), unsafe=round(float(u0.mean()), 4), cost=0.0),
        always_on=dict(acc=round(float(aa.mean()), 4), unsafe=round(float(ua.mean()), 4), cost=3.0),
        oracle_selector=dict(acc=round(float(oracle_acc.mean()), 4), cost=round(float(fixes.mean()), 4)),
        spearman=dict(no_tool=round(float(np.mean([r["no_tool"]["spearman"] for r in test])), 3),
                      always_on=round(float(np.mean([r["levels"][level]["always_on"]["spearman"] for r in test])), 3)),
        tool_precision={t: round(float((at[:, j] > a0)[pred_q & (pd_tool == j)].mean()), 3) if (pred_q & (pd_tool == j)).any() else None for j, t in enumerate(TOOLS)},
        tool_acc={t: round(float(at[:, j].mean()), 4) for j, t in enumerate(TOOLS)},
        curves={k: [[round(float(x), 4) for x in pt] for pt in v] for k, v in results.items()},
        auc={k: round(float(np.mean([pt[0] for pt in v])), 4) for k, v in results.items()},
        plandiscrim_minus_uncertainty=vs_margin, plandiscrim_minus_scene_only=vs_scene,
        comparisons=comparisons, cost_offset=cost_offset, vlm=vlm_report,
        abstention=dict(precision=round(prec, 3), recall=round(rec_ab, 3), base_rate=round(float(abstain_truth.mean()), 3)),
        families=fam)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--split", default="val")
    p.add_argument("--out", required=True)
    p.add_argument("--vlm", default=None, help="VLM cache from scripts/cache_vlm.py; adds the VLM selectors")
    p.add_argument("--vlm-pca", type=int, default=32)
    p.add_argument("--vlm-cost", type=float, default=1.0, help="cost of one VLM call, in tool-call units")
    args = p.parse_args()
    with open(os.path.join(args.data, "manifest.json")) as f:
        man = json.load(f)
    names = man["feature_names"]
    agnostic_idx = {k: names.index(k) for k in man["agnostic_features"]}
    train, test = load(args.data, "train"), load(args.data, args.split)
    vlm, suffix = None, ""
    if args.vlm:
        from cassvla.perception.vlm import load_cache
        from cassvla.perception.vlm_features import VLMFeatures
        vf = VLMFeatures(load_cache(args.vlm), n_pca=args.vlm_pca)
        n_tr, n_te = len(train), len(test)
        train = [r for r, ok in zip(train, vf.covered(train)) if ok]
        test = [r for r, ok in zip(test, vf.covered(test)) if ok]
        if not train or not test:
            raise SystemExit(f"no cached VLM frames for the train or {args.split} rows in {args.vlm}")
        vf.fit(train)
        vlm = dict(Xtr=vf.transform(train), Xte=vf.transform(test), tool_te=vf.prompted_tool(test), cost=args.vlm_cost)
        suffix = "_vlm"
        print(f"VLM cache covers {len(train)}/{n_tr} train and {len(test)}/{n_te} {args.split} rows; "
              f"PCA({len(vf.components)}) explains {vf.explained:.3f} of embedding variance", flush=True)
    os.makedirs(args.out, exist_ok=True)
    report = {}
    for key in ("correct", "correct_tol"):
        report[key] = {lv: evaluate(train, test, lv, key, agnostic_idx, vlm) for lv in LEVELS}
    path = os.path.join(args.out, f"{args.split}{suffix}.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=1)
    for key, per in report.items():
        for lv, r in per.items():
            d, e = r["plandiscrim_minus_uncertainty"], r["plandiscrim_minus_scene_only"]
            print(f"{key:12s} {lv:5s} n={r['n']} none={r['no_tool']['acc']:.3f} always={r['always_on']['acc']:.3f} oracle={r['oracle_selector']['acc']:.3f}@{r['oracle_selector']['cost']:.2f} "
                  f"auc rand={r['auc']['random']:.3f} unc={r['auc']['uncertainty_margin']:.3f} scene={r['auc']['scene_only_learned']:.3f} pd={r['auc']['plandiscrim_geometry']:.3f} "
                  f"vs_unc={d['mean_acc_gain']:+.3f} {d['ci95_by_seed']} vs_scene={e['mean_acc_gain']:+.3f} {e['ci95_by_seed']} agn_tool={r['best_agnostic_tool']} abst p={r['abstention']['precision']} r={r['abstention']['recall']} base={r['abstention']['base_rate']}")
            if r["vlm"]:
                print(" " * 19 + "vlm: " + " ".join(f"{m}={r['auc'][m]:.3f}" for m in r["cost_offset"]) +
                      " | " + " ".join(f"{c}={v['mean_acc_gain']:+.3f} p_holm={v['p_holm']}" for c, v in r["comparisons"].items() if "vlm" in c))


if __name__ == "__main__":
    main()
