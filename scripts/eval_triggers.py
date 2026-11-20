"""Simple triggers against the learned selectors, with the harm and benefit split per budget.

    python scripts/eval_triggers.py --data out/v2_dataset --expgain out/v2_expgain.jsonl --out out/v3_eval/triggers.json
    python scripts/eval_triggers.py --data out/v2_dataset --extra-train out/v2_extra_ds --expgain out/v2_expgain.jsonl out/v2_extra_expgain.jsonl --flip out/v3_flip/*.jsonl --out out/v3_eval/triggers_flip.json

Triggers fixed on 2026-11-07 before evaluation. Simple triggers use the tool that is best on train. ego_speed calls
the fastest scenes first, candidate_spread the scenes whose candidate endpoints spread widest, and fixed_schedule
calls evenly spaced decisions within each episode. knowno calls when the margin falls below a threshold
calibrated on train so that the uncalled top-1 is correct at rate 1 - alpha; with only the top-two margin stored,
this is a point on the margin curve. Learned selectors are the fixed MLP on expected-gain targets, averaged over
3 init seeds: scene_only (scene features and margin), candidate_only (candidate features and margin), plandiscrim
(all features) and, with --flip, plandiscrim_flip (all features plus the flip features).

A harmful call is one whose chosen tool has a negative expected gain; benefit captured is the expected gain of
the calls made, over the best expected gain summed over every decision.

With --flip the script exits if any train or test row lacks flip features, unless --allow-missing-flip.

Also written per split/level: unsafe rate per policy (mean_unsafe over budgets, unsafe per budget), the always_on
reference, H3 (smallest budget where a learned curve reaches always_on accuracy, its unsafe rate there against
always_on's, else the gap at budget 0.3), paired seed-bootstrap 95% CIs (1000 resamples, grouped by scenario seed,
on per-decision accuracy averaged over budgets and init seeds) under comparisons, and a top-level hypotheses summary
(H1, H2, S1 of PREREG.md). --levels runs a subset of levels (parallel processes); merge_trigger_runs.py combines them. The final test: --test-data out/v3_final_ds --splits final --expgain <train labels...>
out/v3_final_expgain.jsonl.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eval_baselines as E  # noqa: E402

REPORT_BUDGETS = (0.1, 0.2, 0.3, 0.5)
ALPHAS = (0.05, 0.1, 0.2)
SPLITS = ("val", "test")
LEVELS = ("low", "mid", "high")


def key(r):
    return r["family"], int(r["seed"]), round(float(r["t_dec"]), 1)


def hypotheses(results, splits, levels):
    hyp = {}
    for split in splits:
        c = [results[f"{split}/{lv}"]["comparisons"] for lv in levels]
        hyp[split] = {h: all(x[k]["ci_lower_above_0"] for x in c) for h, k in (("H1", "plandiscrim_vs_uncertainty_margin"), ("H2", "plandiscrim_vs_scene_only"),
                                                                              ("S1", "plandiscrim_flip_vs_plandiscrim")) if all(k in x for x in c)}
    return hyp


def check_flip(flip, rows, name, allow):
    miss = sum(key(r) not in flip for r in rows) if flip else 0
    print(f"{name}: {len(rows)} rows, {miss} without flip features", flush=True)
    if miss and not allow:
        sys.exit(f"error: {miss} of {len(rows)} {name} rows lack flip features; finish flip_features.py or pass --allow-missing-flip")


def episode_schedule(rows, budget):
    """Call the decisions at evenly spaced positions within each episode, at the given rate."""
    q = np.zeros(len(rows), bool)
    episodes = {}
    for i, r in enumerate(rows):
        episodes.setdefault((r["family"], r["seed"]), []).append(i)
    for idx in episodes.values():
        idx = sorted(idx, key=lambda i: rows[i]["t_dec"])
        pos = np.arange(len(idx))
        q[np.array(idx)[np.floor((pos + 1) * budget) > np.floor(pos * budget)]] = True
    return q


def from_mask(mask, tool, a0, at):
    idx = np.arange(len(a0))
    return np.where(mask, at[idx, tool], a0)


def mask_for(order, budget):
    q = np.zeros(len(order), bool)
    q[order[:int(round(budget * len(order)))]] = True
    return q


def summarize(masks, tool, a0, at, ge, fams, u0, ut):
    accs = [from_mask(m, tool, a0, at) for m in masks]
    unss = [from_mask(m, tool, u0, ut) for m in masks]
    idx = np.arange(len(a0))
    gsel = ge[idx, tool]
    total = np.clip(ge, 0, None).max(axis=1).sum()
    split = {}
    for b in REPORT_BUDGETS:
        m = masks[int(round(b / 0.05))]
        split[str(b)] = dict(acc=round(float(accs[int(round(b / 0.05))].mean()), 4),
                             unsafe=round(float(unss[int(round(b / 0.05))].mean()), 4),
                             harm_rate=round(float((gsel[m] < 0).mean()), 4) if m.any() else None,
                             benefit_captured=round(float(np.clip(gsel[m], 0, None).sum() / max(total, 1e-9)), 4))
    fam = {f: round(float(np.mean([a[fams == f].mean() for a in accs])), 4) for f in sorted(set(fams))}
    return dict(mean_acc=round(float(np.mean([a.mean() for a in accs])), 4), curve=[round(float(a.mean()), 4) for a in accs],
                mean_unsafe=round(float(np.mean([u.mean() for u in unss])), 4), unsafe_curve=[round(float(u.mean()), 4) for u in unss],
                by_budget=split, by_family=fam, _dec=np.mean(accs, axis=0))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--expgain", required=True, nargs="+")
    p.add_argument("--extra-train", default=[], nargs="*")
    p.add_argument("--flip", default=None, nargs="*", help="jsonl files from flip_features.py")
    p.add_argument("--allow-missing-flip", action="store_true", help="drop rows without flip features instead of refusing")
    p.add_argument("--test-data", default=None, help="read the evaluated splits from here instead of --data")
    p.add_argument("--splits", default=list(SPLITS), nargs="+")
    p.add_argument("--levels", default=list(LEVELS), nargs="+", help="noise levels to run; merge per-level files with merge_trigger_runs.py")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    eg = {}
    for path in args.expgain:
        eg.update({key(r): r for r in map(json.loads, open(path))})
    flip = {}
    for path in args.flip or []:
        lines = open(path)
        next(lines)
        flip.update({key(r): r["flip"] for r in map(json.loads, lines)})
    man = json.load(open(os.path.join(args.data, "manifest.json")))
    names = man["feature_names"]
    agn = [names.index(k) for k in man["agnostic_features"]]
    cand = [i for i, k in enumerate(names) if k not in man["agnostic_features"] or k == "margin"]
    margin, speed, spread = names.index("margin"), names.index("ego_speed"), names.index("endpoint_spread")

    train = E.load(args.data, "train") + [r for d in args.extra_train for r in E.load(d, "train")]
    train = [r for r in train if key(r) in eg]
    check_flip(flip, train, "train", args.allow_missing_flip)
    train = [r for r in train if not flip or key(r) in flip]

    def feats(rows):
        X = np.array([r["features"] for r in rows], float)
        out = dict(scene_only=X[:, agn], candidate_only=X[:, cand], plandiscrim=X)
        if flip:
            out["plandiscrim_flip"] = np.hstack([X, np.array([flip[key(r)] for r in rows])])
        return out

    Ftr = feats(train)
    out = dict(n_train=len(train), report_budgets=REPORT_BUDGETS, results={})
    for split in args.splits:
        test = [r for r in E.load(args.test_data or args.data, split) if key(r) in eg]
        check_flip(flip, test, split, args.allow_missing_flip)
        test = [r for r in test if not flip or key(r) in flip]
        Fte = feats(test)
        Xte = Fte["plandiscrim"]
        fams = np.array([r["family"] for r in test])
        seeds = np.array([r["seed"] for r in test])
        for lv in args.levels:
            a0, u0, at, ut, aa, ua = E.tables(test, lv, "correct")
            a0t, _, att, _, _, _ = E.tables(train, lv, "correct")
            ge = np.array([[eg[key(r)][lv][t] for t in E.TOOLS] for r in test]) - a0[:, None]
            g = np.clip(np.array([[eg[key(r)][lv][t] for t in E.TOOLS] for r in train]) - a0t[:, None], 0, 1)
            best = int(np.argmax(g.mean(axis=0)))
            fixed = np.full(len(a0), best)
            rng = np.random.default_rng(0)
            res = {}

            def by_order(order, tool):
                return summarize([mask_for(order, b) for b in E.BUDGETS], tool, a0, at, ge, fams, u0, ut)

            rand = [by_order(rng.permutation(len(a0)), rng.integers(3, size=len(a0))) for _ in range(20)]
            res["random"] = dict(mean_acc=round(float(np.mean([r["mean_acc"] for r in rand])), 4),
                                 mean_unsafe=round(float(np.mean([r["mean_unsafe"] for r in rand])), 4), _dec=np.mean([r["_dec"] for r in rand], axis=0),
                                 by_budget={b: {k: round(float(np.mean([r["by_budget"][b][k] for r in rand])), 4) for k in ("acc", "unsafe", "harm_rate", "benefit_captured")}
                                            for b in rand[0]["by_budget"]})
            res["uncertainty_margin"] = by_order(E.rank_desc(-Xte[:, margin], rng), fixed)
            res["ego_speed"] = by_order(E.rank_desc(Xte[:, speed], rng), fixed)
            res["candidate_spread"] = by_order(E.rank_desc(Xte[:, spread], rng), fixed)
            res["fixed_schedule"] = summarize([episode_schedule(test, b) for b in E.BUDGETS], fixed, a0, at, ge, fams, u0, ut)
            for name in Ftr:
                runs = []
                for s in range(3):
                    pr = E.predict(E.fit_mlp(Ftr[name], g, seed=s), Fte[name])
                    runs.append(by_order(E.rank_desc(pr.max(axis=1), np.random.default_rng(s)), pr.argmax(axis=1)))
                res[name] = runs[0]
                res[name]["mean_acc"] = round(float(np.mean([r["mean_acc"] for r in runs])), 4)
                res[name]["by_seed"] = [r["mean_acc"] for r in runs]
                res[name]["mean_unsafe"] = round(float(np.mean([r["mean_unsafe"] for r in runs])), 4)
                res[name]["unsafe_curve"] = [round(float(np.mean([r["unsafe_curve"][i] for r in runs])), 4) for i in range(len(E.BUDGETS))]
                res[name]["_dec"] = np.mean([r["_dec"] for r in runs], axis=0)
                res[name]["curve"] = [round(float(np.mean([r["curve"][i] for r in runs])), 4) for i in range(len(E.BUDGETS))]
                res[name]["by_family"] = {f: round(float(np.mean([r["by_family"][f] for r in runs])), 4) for f in runs[0]["by_family"]}
                for b in res[name]["by_budget"]:
                    res[name]["by_budget"][b] = {k: round(float(np.mean([r["by_budget"][b][k] for r in runs])), 4) for k in ("acc", "unsafe", "harm_rate", "benefit_captured")}
            mtr = np.array([r["features"][margin] for r in train])
            ok = a0t.astype(bool)
            knowno = {}
            for alpha in ALPHAS:
                thr = next((t for t in np.unique(mtr) if ok[mtr >= t].mean() >= 1 - alpha), np.inf)
                call = Xte[:, margin] < thr
                rate = float(call.mean())
                i = int(np.clip(np.round(rate / 0.05), 0, len(E.BUDGETS) - 1))
                knowno[str(alpha)] = dict(threshold=round(float(thr), 4), call_rate=round(rate, 4), acc=round(float(from_mask(call, fixed, a0, at).mean()), 4),
                                          plandiscrim_at_nearest_budget=res["plandiscrim"]["curve"][i], nearest_budget=float(E.BUDGETS[i]))
            res["knowno"] = knowno
            gmax = ge.max(axis=1)
            o, npos = E.rank_desc(gmax, np.random.default_rng(0)), int((gmax > 0).sum())
            ceil = [E.apply_policy(o[:npos], ge.argmax(axis=1), a0, u0, at, ut, min(b, npos / len(a0))) for b in E.BUDGETS]
            res["fair_ceiling"] = dict(mean_acc=round(float(np.mean([c[0].mean() for c in ceil])), 4), mean_unsafe=round(float(np.mean([c[1].mean() for c in ceil])), 4))
            res["always_on"] = dict(acc=round(float(aa.mean()), 4), unsafe=round(float(ua.mean()), 4))
            learned = [n for n in ("scene_only", "candidate_only", "plandiscrim", "plandiscrim_flip") if n in res]
            h3 = {}
            for n in learned:
                reach = [i for i, a in enumerate(res[n]["curve"]) if a >= res["always_on"]["acc"]]
                h3[n] = (dict(reached=True, budget=float(E.BUDGETS[reach[0]]), acc=res[n]["curve"][reach[0]], unsafe=res[n]["unsafe_curve"][reach[0]],
                              always_on_unsafe=res["always_on"]["unsafe"]) if reach else
                         {"reached": False, "gap_at_0.3": round(res["always_on"]["acc"] - res[n]["curve"][6], 4)})
            res["h3_always_on"] = h3
            cmp = {}
            for name, (a, b) in dict(plandiscrim_vs_uncertainty_margin=("plandiscrim", "uncertainty_margin"), plandiscrim_vs_scene_only=("plandiscrim", "scene_only"),
                                     plandiscrim_flip_vs_plandiscrim=("plandiscrim_flip", "plandiscrim")).items():
                if a in res and b in res:
                    d = res[a]["_dec"] - res[b]["_dec"]
                    ci = E.seed_boot(d, seeds, np.random.default_rng(0))
                    cmp[name] = dict(mean_diff=round(float(d.mean()), 4), ci95_by_seed=ci, ci_lower_above_0=bool(ci[0] > 0))
            res["comparisons"] = cmp
            for v in res.values():
                if isinstance(v, dict):
                    v.pop("_dec", None)
            out["results"][f"{split}/{lv}"] = res
            print(f"{split:5s} {lv:4s} n={len(test)}  " + "  ".join(f"{k} {v['mean_acc']:.4f}" for k, v in res.items() if "mean_acc" in v), flush=True)
    hyp = hypotheses(out["results"], args.splits, args.levels)
    out["hypotheses"] = hyp
    print(json.dumps(hyp), flush=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()
