"""Failure analysis of the frozen plandiscrim MLP on val and test (never out/v3_final*).

    cd /home/user/CASS-VLA && OMP_NUM_THREADS=1 .venv/bin/python research/2026-11-19_learned_selector/analysis2/run.py

Training set, labels and MLP settings are those of scripts/eval_triggers.py. Writes results.json next to this file.
"""
import json, os, sys
import numpy as np

ROOT = "/home/user/CASS-VLA"
sys.path.insert(0, f"{ROOT}/scripts"); sys.path.insert(0, ROOT)
import eval_baselines as E
from cassvla.planning.features import FEATURE_NAMES

OUT = os.path.dirname(os.path.abspath(__file__))
D = f"{ROOT}/out/v2_dataset"; X2 = f"{ROOT}/out/v2_extra_ds"
TOOLS = E.TOOLS
LEVELS = ("low", "mid", "high")
SPLITS = ("val", "test")
BUD = E.BUDGETS
EPS = 1e-9
NREP = 10


def key(r):
    return r["family"], int(r["seed"]), round(float(r["t_dec"]), 1)


def main():
    eg = {}
    for p in ("out/v2_expgain.jsonl", "out/v2_extra_expgain.jsonl"):
        eg.update({key(r): r for r in map(json.loads, open(f"{ROOT}/{p}"))})
    man = json.load(open(f"{D}/manifest.json"))
    names = man["feature_names"]
    assert tuple(names) == FEATURE_NAMES
    agn = [names.index(k) for k in man["agnostic_features"]]
    margin = names.index("margin")
    train = [r for r in E.load(D, "train") + E.load(X2, "train") if key(r) in eg]
    Xtr = np.array([r["features"] for r in train], float)
    ref = json.load(open(f"{ROOT}/out/v3_eval/triggers.json"))
    res = dict(n_train=len(train), feature_names=names, cells={})
    fam_order = None
    for split in SPLITS:
        test = [r for r in E.load(D, split) if key(r) in eg]
        X = np.array([r["features"] for r in test], float)
        fams = np.array([r["family"] for r in test]); seeds = np.array([r["seed"] for r in test])
        n = len(test)
        for lv in LEVELS:
            cell = f"{split}/{lv}"
            a0, u0, at, ut, aa, ua = E.tables(test, lv, "correct")
            a0t, _, _, _, _, _ = E.tables(train, lv, "correct")
            ge = np.array([[eg[key(r)][lv][t] for t in TOOLS] for r in test]) - a0[:, None]
            g = np.clip(np.array([[eg[key(r)][lv][t] for t in TOOLS] for r in train]) - a0t[:, None], 0, 1)
            fixed = np.full(n, int(np.argmax(g.mean(axis=0))))
            idx = np.arange(n)

            def dec(order, tool):  # per-decision accuracy averaged over budgets (realised draw)
                accs = []
                for b in BUD:
                    q = np.zeros(n, bool); q[order[:int(round(b * n))]] = True
                    accs.append(np.where(q, at[idx, tool], a0))
                return np.array(accs)

            rng = np.random.default_rng(0)
            for _ in range(20):
                rng.permutation(n); rng.integers(3, size=n)
            unc = dec(E.rank_desc(-X[:, margin], rng), fixed)
            models, preds, decs = {}, {}, {}
            for name, cols in (("scene_only", agn), ("plandiscrim", list(range(X.shape[1])))):
                decs[name], preds[name], models[name] = [], [], []
                for s in range(3):
                    m = E.fit_mlp(Xtr[:, cols], g, seed=s)
                    pr = E.predict(m, X[:, cols])
                    decs[name].append(dec(E.rank_desc(pr.max(axis=1), np.random.default_rng(s)), pr.argmax(axis=1)))
                    preds[name].append(pr); models[name].append(m)
            chk = {nm: (round(float(np.mean([d.mean() for d in decs[nm]])), 4), ref["results"][cell][nm]["mean_acc"]) for nm in decs}
            chk["uncertainty_margin"] = (round(float(unc.mean()), 4), ref["results"][cell]["uncertainty_margin"]["mean_acc"])
            c = dict(n=n, check_vs_triggers_json=chk, per_family_n={f: int((fams == f).sum()) for f in sorted(set(fams))})
            print(cell, chk, flush=True)

            # ---- Q5 bootstrap
            dpl = np.mean(decs["plandiscrim"], axis=0).mean(axis=0)
            dsc = np.mean(decs["scene_only"], axis=0).mean(axis=0)
            dun = unc.mean(axis=0)
            q5 = {}
            for nm, d in (("plandiscrim_minus_scene_only", dpl - dsc), ("plandiscrim_minus_uncertainty_margin", dpl - dun)):
                ci = E.seed_boot(d, seeds, np.random.default_rng(0))
                q5[nm] = dict(mean_diff=round(float(d.mean()), 4), ci95=ci)
                q5[nm]["by_family"] = {}
                for f in sorted(set(fams)):
                    m_ = fams == f
                    ci_f = E.seed_boot(d[m_], seeds[m_], np.random.default_rng(0))
                    q5[nm]["by_family"][f] = dict(mean_diff=round(float(d[m_].mean()), 4), ci95=ci_f)
            q5["n_scenario_seeds"] = int(len(np.unique(seeds)))
            c["q5"] = q5

            # ---- Q1 / Q2 / Q4 on seed 0 plandiscrim
            pr = preds["plandiscrim"][0]
            score = pr.max(axis=1); tool = pr.argmax(axis=1)
            order = E.rank_desc(score, np.random.default_rng(0))
            rank_frac = np.empty(n); rank_frac[order] = (np.arange(n) + 1) / n
            gsel = ge[idx, tool]; gmax = ge.max(axis=1); best = ge.argmax(axis=1)
            real = at[idx, tool] - a0
            bins = [(0, .2), (.2, .4), (.4, .65), (.65, .8), (.8, 1.0000001)]
            q1 = []
            for lo, hi in bins + [(0, .65), (.65, 1.0000001)]:
                m_ = (rank_frac > lo) & (rank_frac <= hi)
                q1.append(dict(rank_from=lo, rank_to=min(hi, 1.0), n=int(m_.sum()), mean_pred_score=round(float(score[m_].mean()), 4),
                               mean_ge_chosen=round(float(gsel[m_].mean()), 4), mean_ge_best=round(float(gmax[m_].mean()), 4),
                               mean_ge_per_tool={t: round(float(ge[m_, j].mean()), 4) for j, t in enumerate(TOOLS)},
                               mean_realised_gain_chosen=round(float(real[m_].mean()), 4),
                               frac_chosen_negative=round(float((gsel[m_] < -EPS).mean()), 4), frac_chosen_zero=round(float((np.abs(gsel[m_]) <= EPS).mean()), 4),
                               frac_chosen_positive=round(float((gsel[m_] > EPS).mean()), 4), frac_no_tool_helps=round(float((gmax[m_] <= EPS).mean()), 4),
                               frac_notool_correct=round(float(a0[m_].mean()), 4),
                               chosen_tool_share={t: round(float((tool[m_] == j).mean()), 4) for j, t in enumerate(TOOLS)}))
            c["q1_by_rank"] = q1
            late = rank_frac > 0.65
            c["q1_late_by_family"] = {f: dict(n=int((late & (fams == f)).sum()), share_of_family_in_late=round(float((late & (fams == f)).sum() / (fams == f).sum()), 4),
                                              frac_neg=round(float((gsel[late & (fams == f)] < -EPS).mean()), 4), mean_ge_chosen=round(float(gsel[late & (fams == f)].mean()), 4),
                                              frac_no_tool_helps=round(float((gmax[late & (fams == f)] <= EPS).mean()), 4),
                                              mean_pred=round(float(score[late & (fams == f)].mean()), 4))
                                      for f in sorted(set(fams)) if (late & (fams == f)).any()}
            c["q1_late_by_tool"] = {t: dict(n=int((late & (tool == j)).sum()), frac_neg=round(float((gsel[late & (tool == j)] < -EPS).mean()), 4),
                                            mean_ge_chosen=round(float(gsel[late & (tool == j)].mean()), 4)) for j, t in enumerate(TOOLS) if (late & (tool == j)).any()}
            c["q1_early_by_family"] = {f: dict(n=int(((~late) & (fams == f)).sum()), frac_neg=round(float((gsel[(~late) & (fams == f)] < -EPS).mean()), 4),
                                               mean_ge_chosen=round(float(gsel[(~late) & (fams == f)].mean()), 4)) for f in sorted(set(fams)) if ((~late) & (fams == f)).any()}
            # share of positive-gain mass (gmax>0) that lies in early vs late ranks
            c["q1_share_of_total_best_gain_in_late"] = round(float(np.clip(gmax[late], 0, None).sum() / np.clip(gmax, 0, None).sum()), 4)
            c["q1_share_of_chosen_gain_in_late"] = round(float(gsel[late].sum() / gsel.sum()), 4)

            # Q2
            npos = int((gmax > EPS).sum())
            oc = E.rank_desc(gmax, np.random.default_rng(0))
            q2 = {}
            for nm in ("plandiscrim", "scene_only"):
                p_ = preds[nm][0]; o_ = E.rank_desc(p_.max(axis=1), np.random.default_rng(0)); t_ = p_.argmax(axis=1)
                rows = []
                for b in BUD[1:]:
                    k = int(round(b * n)); S = o_[:k]
                    gceil = gmax[oc[:min(k, npos)]].sum()
                    gpol = ge[S, t_[S]].sum()
                    a1 = gceil - np.clip(gmax[S], 0, None).sum()
                    a2 = -np.minimum(gmax[S], 0).sum()
                    bb = (gmax[S] - ge[S, t_[S]]).sum()
                    inter = len(set(S.tolist()) & set(oc[:min(k, npos)].tolist()))
                    rows.append(dict(budget=float(b), gap_exp_acc=round(float((gceil - gpol) / n), 5), a_missed_positive_mass=round(float(a1 / n), 5),
                                     a_calls_where_no_tool_helps=round(float(a2 / n), 5), b_wrong_tool=round(float(bb / n), 5),
                                     frac_calls_in_ceiling_set=round(inter / max(k, 1), 4), frac_calls_gmax_nonpos=round(float((gmax[S] <= EPS).mean()), 4),
                                     frac_calls_wrong_tool=round(float((ge[S, t_[S]] < gmax[S] - EPS).mean()), 4),
                                     frac_calls_neg_chosen=round(float((ge[S, t_[S]] < -EPS).mean()), 4)))
                q2[nm] = rows
            c["q2"] = q2

            # Q4
            bestlab = np.where(gmax > EPS, best, 3)
            conf = {}
            for f in sorted(set(fams)):
                m_ = fams == f
                M = np.zeros((4, 3), int)
                for bl, pl in zip(bestlab[m_], tool[m_]): M[bl, pl] += 1
                pos = m_ & (gmax > EPS)
                called = m_ & (rank_frac <= 0.5)
                conf[f] = dict(matrix_rows_best_roi_depth_collision_none_cols_pred_roi_depth_collision=M.tolist(), n=int(m_.sum()),
                               frac_best_is_none=round(float((gmax[m_] <= EPS).mean()), 4),
                               tool_optimal_rate_among_positive=round(float((ge[pos, tool[pos]] >= gmax[pos] - EPS).mean()), 4) if pos.any() else None,
                               mean_regret_among_positive=round(float((gmax[pos] - ge[pos, tool[pos]]).mean()), 4) if pos.any() else None,
                               pred_tool_share={t: round(float((tool[m_] == j).mean()), 4) for j, t in enumerate(TOOLS)},
                               best_tool_share_among_positive={t: round(float((best[pos] == j).mean()), 4) for j, t in enumerate(TOOLS)} if pos.any() else None,
                               frac_called_at_0p5=round(float(called.sum() / m_.sum()), 4),
                               frac_neg_among_called_0p5=round(float((gsel[called] < -EPS).mean()), 4) if called.any() else None,
                               share_positive_decisions_called_0p5=round(float((called & pos).sum() / max(pos.sum(), 1)), 4))
            c["q4"] = conf
            tl = {}
            for j, t in enumerate(TOOLS):
                pos = gmax > EPS
                m_ = pos & (best == j)
                tl[t] = dict(n_best=int(m_.sum()), pred_when_best=[round(float((tool[m_] == k_).mean()), 4) for k_ in range(3)] if m_.any() else None,
                             n_pred=int((tool == j).sum()), precision_tool_optimal=round(float((ge[tool == j, j] >= gmax[tool == j] - EPS).mean()), 4))
            c["q4_by_tool"] = tl

            # ---- Q3 permutation importance
            grp = {"candidate_divergence": [k for k in FEATURE_NAMES if k.startswith("div_") or k.startswith("runner_") or k == "light_splits_top2"],
                   "top_candidate_identity": [k for k in FEATURE_NAMES if k.startswith("top_") and k not in ("top_clearance", "top_ttc")],
                   "top_candidate_safety": ["frac_pred_safe", "top_clearance", "top_ttc", "n_near_threshold", "range_uncertainty_near_top"],
                   "occlusion": ["occl_top", "occl_mean", "occl_max", "stop_in_reach_light_unknown"],
                   "candidate_spread": ["endpoint_spread", "progress_spread"],
                   "scene_agnostic_incl_margin": [names[i] for i in agn]}
            perm = {}
            for nm, cols in (("plandiscrim", list(range(X.shape[1]))), ("scene_only", agn)):
                mdl = models[nm][0]
                def score_acc(Xm):
                    pr_ = E.predict(mdl, Xm[:, cols])
                    return dec(E.rank_desc(pr_.max(axis=1), np.random.default_rng(0)), pr_.argmax(axis=1)).mean()
                base = score_acc(X)
                units = {k: [names.index(k)] for k in (names[i] for i in cols)}
                units.update({"GROUP:" + gname: [names.index(k) for k in ks if names.index(k) in cols] for gname, ks in grp.items() if any(names.index(k) in cols for k in ks)})
                out = {}
                prng = np.random.default_rng(1)
                for u, ci_ in units.items():
                    drops = []
                    for _ in range(NREP):
                        p_ = prng.permutation(n); Xp = X.copy(); Xp[:, ci_] = X[p_][:, ci_]
                        drops.append(base - score_acc(Xp))
                    out[u] = dict(drop=round(float(np.mean(drops)), 5), sd=round(float(np.std(drops)), 5))
                perm[nm] = dict(base_mean_acc=round(float(base), 4), importance=out)
            c["q3"] = perm
            res["cells"][cell] = c
            json.dump(res, open(f"{OUT}/results.json", "w"), indent=1)


if __name__ == "__main__":
    main()
