"""Post hoc analysis of the first final split (out/v3_final_ds). Retrains the frozen MLP and signed_mse_abstain once per level."""
import json
import os
import sys

import numpy as np

ROOT = "/home/user/CASS-VLA"
sys.path.insert(0, ROOT + "/research/2026-11-19_learned_selector/experiments")
import exp as X  # noqa: E402  (also puts scripts/ on the path)

E, T = X.E, X.T
HERE = os.path.dirname(os.path.abspath(__file__))
FINE = np.round(np.arange(0, 1.0001, 0.01), 2)
ref = json.load(open(ROOT + "/out/v3_eval/triggers_final.json"))["results"]

eg, agn, train, splits = X.load(expgain=("v2_expgain.jsonl", "v2_extra_expgain.jsonl", "v3_extra_expgain.jsonl", "v3_final_expgain.jsonl"),
                                train_dirs=("v2_dataset", "v2_extra_ds", "v3_extra_ds"), test_dir="v3_final_ds", split_names=("final",))
test = splits["final"]
print("train", len(train), "test", len(test), flush=True)
man = json.load(open(ROOT + "/out/v2_dataset/manifest.json"))
names = man["feature_names"]
margin = names.index("margin")
Xtr = np.array([r["features"] for r in train], float)
Xte = np.array([r["features"] for r in test], float)
seeds = np.array([r["seed"] for r in test])
n = len(test)


def dec(score_runs, a0, u0, at, ut):
    """score_runs: list of (order, tool, allow or None). Per-decision accuracy, unsafe and call rate on the fine grid, averaged over runs."""
    A = np.zeros((len(FINE), n))
    U = np.zeros_like(A)
    C = np.zeros_like(A)
    idx = np.arange(n)
    for order, tool, allow in score_runs:
        for k, b in enumerate(FINE):
            m = T.mask_for(order, b)
            if allow is not None:
                m = m & allow
            A[k] += np.where(m, at[idx, tool], a0)
            U[k] += np.where(m, ut[idx, tool], u0)
            C[k] += m
    r = len(score_runs)
    return A / r, U / r, C / r


out = {}
for lv in ("low", "mid", "high"):
    a0, u0, at, ut, aa, ua = E.tables(test, lv, "correct")
    a0t = E.tables(train, lv, "correct")[0]
    egt = np.array([[eg[T.key(r)][lv][t] for t in E.TOOLS] for r in train]) - a0t[:, None]
    g = np.clip(egt, 0, 1)
    best = int(np.argmax(g.mean(0)))
    fixed = np.full(n, best)
    R = {}
    rng = np.random.default_rng(0)
    for _ in range(20):  # same rng use as eval_triggers: 20 random runs come first
        rng.permutation(n)
        rng.integers(3, size=n)
    R["uncertainty_margin"] = dec([(E.rank_desc(-Xte[:, margin], rng), fixed, None)], a0, u0, at, ut)
    for name, cols in (("plandiscrim", slice(None)), ("scene_only", agn)):
        Ftr, Fte = Xtr[:, cols], Xte[:, cols]
        runs = []
        for s in range(3):
            pr = E.predict(E.fit_mlp(Ftr, g, seed=s), Fte)
            runs.append((E.rank_desc(pr.max(1), np.random.default_rng(s)), pr.argmax(1), None))
        R[name] = dec(runs, a0, u0, at, ut)
        if name == "plandiscrim":
            runs = []
            for s in range(3):
                pr = X.fit_reg(Xtr, egt, "mse", s)(Xte)
                runs.append((E.rank_desc(pr.max(1), np.random.default_rng(s)), pr.argmax(1), pr.max(1) > 0))
            R["signed_mse_abstain"] = dec(runs, a0, u0, at, ut)
        print(lv, name, flush=True)
    chk = {}
    for k in ("uncertainty_margin", "plandiscrim", "scene_only"):
        c = np.array(ref[f"final/{lv}"][k]["curve"])
        u = np.array(ref[f"final/{lv}"][k]["unsafe_curve"])
        chk[k] = dict(max_abs_acc=float(np.abs(R[k][0][::5].mean(1) - c).max()), max_abs_unsafe=float(np.abs(R[k][1][::5].mean(1) - u).max()))
    arrs = {f"{k}_{t}": v[i] for k, v in R.items() for i, t in enumerate("AUC")}
    np.savez_compressed(f"{HERE}/dec_{lv}.npz", seeds=seeds, aa=aa, ua=ua, **arrs)
    out[lv] = dict(always_on=dict(acc=float(aa.mean()), unsafe=float(ua.mean())), check_vs_triggers_final=chk, fixed_tool=E.TOOLS[best])
json.dump(out, open(f"{HERE}/calc_check.json", "w"), indent=1)
print(json.dumps(out, indent=1))
