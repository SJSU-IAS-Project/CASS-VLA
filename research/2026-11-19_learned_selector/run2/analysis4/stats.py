"""Post hoc stats on dec_<level>.npz written by calc.py. Writes h3_posthoc.json."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FINE = np.round(np.arange(0, 1.0001, 0.01), 2)
METHODS = ("plandiscrim", "signed_mse_abstain", "scene_only", "uncertainty_margin")
FIXED = (0.3, 0.5, 0.7)
LEVELS = ("low", "mid", "high")
ORIG = {"low": 0.60, "mid": 0.50, "high": 0.35}  # out/v3_eval/triggers_final.json h3_always_on.plandiscrim.budget
NB = 1000


def idx(b):
    return int(round(b * 100))


def boot_idx(seeds):
    uniq = np.unique(seeds)
    rng = np.random.default_rng(0)  # same draws as eval_baselines.seed_boot
    return uniq, np.array([rng.integers(len(uniq), size=len(uniq)) for _ in range(NB)])


def ci(diff, seeds, uniq, bi):
    per = np.array([diff[seeds == s].sum() for s in uniq])
    cnt = np.array([(seeds == s).sum() for s in uniq])
    st = per[bi].sum(1) / cnt[bi].sum(1)
    return [round(float(np.percentile(st, 2.5)), 4), round(float(np.percentile(st, 97.5)), 4)]


def first(ok):
    w = np.where(ok)[0]
    return int(w[0]) if len(w) else None


def sustained(ok):
    """first index from which ok holds at every later index"""
    bad = np.where(~ok)[0]
    k = 0 if len(bad) == 0 else int(bad[-1]) + 1
    return k if k < len(ok) else None


out = {}
for lv in LEVELS:
    z = np.load(f"{HERE}/dec_{lv}.npz")
    seeds = z["seeds"]
    aa, ua = z["aa"], z["ua"]
    A0, U0 = aa.mean(), ua.mean()
    uniq, bi = boot_idx(seeds)
    L = dict(always_on=dict(acc=round(float(A0), 4), unsafe=round(float(U0), 4)), n=int(len(seeds)), n_seeds=int(len(uniq)), methods={})
    for m in METHODS:
        A, U, C = z[f"{m}_A"], z[f"{m}_U"], z[f"{m}_C"]
        ac, un, cl = A.mean(1), U.mean(1), C.mean(1)
        # fine grid and the 0.05 grid (every 5th point)
        res = {}
        for gname, step in (("grid0.05", 5), ("grid0.01", 1)):
            sel = np.arange(0, len(FINE), step)
            oka, oku = ac[sel] >= A0, un[sel] <= U0
            row = {}
            for tag, ok in (("accuracy", oka), ("unsafe", oku), ("both", oka & oku)):
                k = first(ok)
                s = sustained(ok)
                row[tag] = dict(first_budget=None if k is None else float(FINE[sel][k]),
                                calls_per_decision=None if k is None else round(float(cl[sel][k]), 4),
                                sustained_budget=None if s is None else float(FINE[sel][s]))
            res[gname] = row
        res["max_acc"] = round(float(ac.max()), 4)
        res["min_unsafe"] = round(float(un.min()), 4)
        res["max_call_rate"] = round(float(cl.max()), 4)
        # unsafe and accuracy differences against always_on, with CIs, at chosen budgets
        pts = {}
        bl = {"orig_match": ORIG[lv]}
        bl.update({f"fixed_{b}": b for b in FIXED})
        for tag, b in bl.items():
            k = idx(b)
            pts[tag] = dict(budget=b, calls_per_decision=round(float(cl[k]), 4),
                            acc=round(float(ac[k]), 4), acc_minus_always=round(float(ac[k] - A0), 4), acc_diff_ci95=ci(A[k] - aa, seeds, uniq, bi),
                            unsafe=round(float(un[k]), 4), unsafe_minus_always=round(float(un[k] - U0), 4), unsafe_diff_ci95=ci(U[k] - ua, seeds, uniq, bi))
        res["points"] = pts
        # at the method's own first unsafe match and first accuracy match (0.01 grid)
        own = {}
        for tag in ("accuracy", "unsafe", "both"):
            b = res["grid0.01"][tag]["first_budget"]
            if b is not None:
                k = idx(b)
                own[tag] = dict(budget=b, calls_per_decision=round(float(cl[k]), 4),
                                acc_minus_always=round(float(ac[k] - A0), 4), acc_diff_ci95=ci(A[k] - aa, seeds, uniq, bi),
                                unsafe_minus_always=round(float(un[k] - U0), 4), unsafe_diff_ci95=ci(U[k] - ua, seeds, uniq, bi))
        res["at_own_first_match_0.01"] = own
        # curves of differences with CIs on the 0.05 grid for the figure
        res["curve05"] = dict(budget=[float(b) for b in FINE[::5]], calls=[round(float(c), 4) for c in cl[::5]],
                              acc_diff=[round(float(ac[k] - A0), 4) for k in range(0, 101, 5)],
                              unsafe_diff=[round(float(un[k] - U0), 4) for k in range(0, 101, 5)],
                              unsafe_diff_ci=[ci(U[k] - ua, seeds, uniq, bi) for k in range(0, 101, 5)])
        # bootstrap of the first accuracy-match budget (0.01 grid), over scenario seeds
        if m == "plandiscrim":
            per = np.array([[(A[k] - aa)[seeds == s].sum() for k in range(len(FINE))] for s in uniq])
            cnt = np.array([(seeds == s).sum() for s in uniq])
            fb, fu = [], []
            perU = np.array([[(U[k] - ua)[seeds == s].sum() for k in range(len(FINE))] for s in uniq])
            for i in bi:
                dA = per[i].sum(0) / cnt[i].sum()
                k = first(dA >= 0)
                fb.append(np.nan if k is None else FINE[k])
                dU = perU[i].sum(0) / cnt[i].sum()
                k = first(dU <= 0)
                fu.append(np.nan if k is None else FINE[k])
            for tag, v in (("first_acc_match_budget_boot", fb), ("first_unsafe_match_budget_boot", fu)):
                v = np.array(v)
                res[tag] = dict(never_share=round(float(np.isnan(v).mean()), 3),
                                pct2_5_50_97_5=[None if np.isnan(v).all() else round(float(np.nanpercentile(v, q)), 3) for q in (2.5, 50, 97.5)])
            # budget range where accuracy diff is >= 0
            res["acc_ge_always_budgets_0.01"] = [float(FINE[k]) for k in np.where(ac >= A0)[0]]
        L["methods"][m] = res
    out[lv] = L
json.dump(out, open(f"{HERE}/h3_posthoc.json", "w"), indent=1)
for lv in LEVELS:
    print(lv, out[lv]["always_on"])
    for m in METHODS:
        r = out[lv]["methods"][m]
        print(" ", m, "max_acc", r["max_acc"], "min_uns", r["min_unsafe"], {g: {t: (r[g][t]["first_budget"], r[g][t]["calls_per_decision"], r[g][t]["sustained_budget"]) for t in r[g]} for g in ("grid0.05", "grid0.01")})
