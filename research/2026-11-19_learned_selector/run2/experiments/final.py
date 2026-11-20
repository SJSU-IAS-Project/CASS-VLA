"""Final-run harness for PREREG2.md. Extends exp2.py; method code is unchanged (it reuses exp2/exp trainers).

Geometry run (P1-P4):
  python final.py --methods signed frozen signed_scene uncertainty_margin always_on --out out/v4_eval/final_geom.json ...
VLM run (Q1):
  python final.py --methods signed signed_vlm --embed <npz...> ...   (exits 2 if any train or test row lacks an embedding)
Paths for --train-dirs, --test-dir, --*-expgain, --out are relative to out/ unless absolute.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp2 as M  # noqa: E402

X, E, T, ROOT = M.X, M.E, M.T, M.ROOT
BUD06 = int(np.where(np.isclose(E.BUDGETS, 0.6))[0][0])
LEVELS = M.LEVELS


def ci(d, seeds):
    return E.seed_boot(d, seeds, np.random.default_rng(0))


def run_method(name, ctx, lv, g, cache, tr_best):
    """-> {split: [(score, tool, allow), ...per init seed]}"""
    out = {sp: [] for sp in ctx.sp}
    if name == "always_on":
        return None
    if name == "uncertainty_margin":
        mi = ctx.margin
        for sp in ctx.sp:
            m = ctx.cells[(sp, lv)].X[:, mi]
            out[sp].append((-m, np.full(len(m), tr_best), None))  # one run, ties broken with rng(0) as in eval_triggers
        return out
    for sd in X.SEEDS:
        if name == "signed":
            o, _ = M.mk_signed("plandiscrim")(ctx, lv, g, sd, cache)
        elif name == "signed_scene":
            o, _ = M.mk_signed("scene_only")(ctx, lv, g, sd, cache)
        elif name == "signed_vlm":
            o, _ = M.mk_signed("geom_vlm")(ctx, lv, g, sd, cache)
        elif name == "frozen":
            fr = M.frozen_tool(ctx, lv, g, sd, cache, "plandiscrim")
            o = {sp: (fr[sp].max(1), fr[sp].argmax(1), None) for sp in ctx.sp}
        else:
            raise SystemExit(f"unknown method {name}")
        for sp in ctx.sp:
            out[sp].append(o[sp])
    return out


def at_budget(cell, runs, b_idx):
    """per-decision accuracy and unsafe at one budget, averaged over init seeds."""
    acc, uns, rate = [], [], []
    for s, (score, tool, allow) in enumerate(runs):
        order = E.rank_desc(score, np.random.default_rng(s))
        m = T.mask_for(order, E.BUDGETS[b_idx])
        if allow is not None:
            m = m & allow
        acc.append(T.from_mask(m, tool, cell.a0, cell.at))
        uns.append(T.from_mask(m, tool, cell.u0, cell.ut))
        rate.append(m.mean())
    return np.mean(acc, 0), np.mean(uns, 0), float(np.mean(rate))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--methods", nargs="+", required=True, choices=["signed", "frozen", "signed_scene", "uncertainty_margin", "always_on", "signed_vlm"])
    p.add_argument("--train-dirs", nargs="+", default=["v2_dataset", "v2_extra_ds", "v3_extra_ds"])
    p.add_argument("--train-expgain", nargs="+", default=["v2_expgain.jsonl", "v2_extra_expgain.jsonl", "v3_extra_expgain.jsonl"])
    p.add_argument("--test-dir", default="v4_final_ds")
    p.add_argument("--test-expgain", nargs="+", default=["v4_final_expgain.jsonl"])
    p.add_argument("--splits", nargs="+", default=["final"])
    p.add_argument("--embed", nargs="*", default=[], help="npz files with image_mid (required for signed_vlm)")
    p.add_argument("--levels", nargs="+", default=list(LEVELS))
    p.add_argument("--expect-train", type=int, default=None, help="abort if the number of usable train rows differs")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    D = ROOT + "/out/"
    outp = a.out if os.path.isabs(a.out) else D + a.out
    for f in a.embed:
        if not os.path.exists(f):
            print(f"embedding file missing: {f}", file=sys.stderr)
            sys.exit(2)
    vlm = "signed_vlm" in a.methods
    if vlm and not a.embed:
        print("REFUSING to run signed_vlm: no --embed given", file=sys.stderr)
        sys.exit(2)
    for sp in a.splits:  # every test row must have labels
        n = sum(1 for _ in open(os.path.join(D, a.test_dir, sp + ".jsonl")))
        print(sp, "rows in file", n, flush=True)
    ctx = M.Ctx(tuple(a.train_dirs), tuple(a.train_expgain) + tuple(a.test_expgain), vlm=a.embed if vlm else None,
                test_dir=a.test_dir, split_names=tuple(a.splits), strict_vlm=vlm)
    for sp in a.splits:
        n = sum(1 for _ in open(os.path.join(D, a.test_dir, sp + ".jsonl")))
        if len(ctx.splits[sp]) != n:
            print(f"ABORT: {n - len(ctx.splits[sp])} {sp} rows have no expected-gain labels", file=sys.stderr)
            sys.exit(3)
    if a.expect_train and len(ctx.train) != a.expect_train:
        print(f"ABORT: n_train {len(ctx.train)} != expected {a.expect_train}", file=sys.stderr)
        sys.exit(3)
    man = json.load(open(D + "v2_dataset/manifest.json"))
    ctx.margin = man["feature_names"].index("margin")

    res, dec = {}, {}
    for lv in a.levels:
        egt = ctx.gains(lv)
        a0t = E.tables(ctx.train, lv, "correct")[0]
        tr_best = int(np.argmax(np.clip(egt, 0, 1).mean(axis=0)))
        cache = {}
        for name in a.methods:
            runs = run_method(name, ctx, lv, egt, cache, tr_best)
            for sp in a.splits:
                cell = ctx.cells[(sp, lv)]
                tag = f"{sp}/{lv}"
                if name == "always_on":
                    aa_, ua_ = E.tables(ctx.splits[sp], lv, "correct")[4:6]
                    res.setdefault(tag, {})[name] = dict(mean_acc=round(float(aa_.mean()), 4), mean_unsafe=round(float(ua_.mean()), 4), calls_per_decision=3)
                    dec[(tag, name)] = dict(acc=aa_, uns=ua_)
                    continue
                r = X.evaluate(cell, runs[sp])
                d = M.summarize(r)
                cu = r["curve"]
                d["drop_after_0.65"] = round(max(cu[13:]) - cu[-1], 4)
                acc6, uns6, rate6 = at_budget(cell, runs[sp], BUD06)
                d["at_budget_0.6"] = dict(acc=round(float(acc6.mean()), 4), unsafe=round(float(uns6.mean()), 4), call_rate=round(rate6, 4))
                dec[(tag, name)] = dict(mean=r.pop("_dec"), acc6=acc6, uns6=uns6)
                res.setdefault(tag, {})[name] = d
            print(lv, name, {sp: res[f"{sp}/{lv}"][name].get("mean_acc") for sp in a.splits}, flush=True)

    def diff(tag, m1, m2, sp, lv):
        seeds = ctx.cells[(sp, lv)].seeds
        d = dec[(tag, m1)]["mean"] - dec[(tag, m2)]["mean"]
        c = ci(d, seeds)
        return dict(mean_diff=round(float(d.mean()), 4), ci95=c, ci_lower_above_0=bool(c[0] > 0))

    hyp = {}
    for sp in a.splits:
        h = {}
        have = set(a.methods)

        def pair(m1, m2, lvs):
            cells = {lv: diff(f"{sp}/{lv}", m1, m2, sp, lv) for lv in lvs if lv in a.levels}
            return cells, bool(len(cells) == len(lvs) and all(c["ci_lower_above_0"] for c in cells.values()))
        for hn, m2, lvs, text in (("P1", "frozen", ("mid", "high"), "signed beats frozen at mid and high, CI above 0"),
                                  ("P2", "signed_scene", LEVELS, "signed beats signed_scene at all levels, CI above 0"),
                                  ("P3", "uncertainty_margin", LEVELS, "signed beats uncertainty_margin at all levels, CI above 0"),
                                  ("Q1", "signed_vlm", LEVELS, "signed_vlm beats signed at all levels, CI above 0")):
            m1, mb = ("signed_vlm", "signed") if hn == "Q1" else ("signed", m2)
            if m1 not in have or mb not in have:
                h[hn] = dict(rule=text, status="not run")
                continue
            cells, ok = pair(m1, mb, lvs)
            h[hn] = dict(rule=text, status="pass" if ok else "fail", **{"pass": ok}, cells=cells)
        if {"signed", "always_on"} <= have:
            cells = {}
            for lv in a.levels:
                tag = f"{sp}/{lv}"
                seeds = ctx.cells[(sp, lv)].seeds
                da = dec[(tag, "signed")]["acc6"] - dec[(tag, "always_on")]["acc"]
                du = dec[(tag, "signed")]["uns6"] - dec[(tag, "always_on")]["uns"]
                ca, cuu = ci(da, seeds), ci(du, seeds)
                cells[lv] = {"acc_diff": round(float(da.mean()), 4), "acc_diff_ci95": ca, "acc_lower_above_minus_0.01": bool(ca[0] > -0.01),
                             "unsafe_diff": round(float(du.mean()), 4), "unsafe_diff_ci95": cuu, "unsafe_upper_below_plus_0.01": bool(cuu[1] < 0.01)}
            ok = len(cells) == 3 and all(c["acc_lower_above_minus_0.01"] and c["unsafe_upper_below_plus_0.01"] for c in cells.values())
            h["P4"] = dict(rule="at budget 0.6, signed acc diff vs always_on CI lower > -0.01 and unsafe diff CI upper < +0.01, all levels",
                           status="pass" if ok else "fail", **{"pass": ok}, cells=cells)
        else:
            h["P4"] = dict(rule="P4", status="not run")
        hyp[sp] = h
    for sp, h in hyp.items():
        print(sp, {k: v["status"] for k, v in h.items()}, flush=True)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    json.dump(dict(n_train=len(ctx.train), n_test={k: len(v) for k, v in ctx.splits.items()}, train_dirs=a.train_dirs, test_dir=a.test_dir,
                   methods=a.methods, seeds=list(X.SEEDS), hypotheses=hyp, results=res), open(outp, "w"), indent=1,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print("wrote", outp)


if __name__ == "__main__":
    main()
