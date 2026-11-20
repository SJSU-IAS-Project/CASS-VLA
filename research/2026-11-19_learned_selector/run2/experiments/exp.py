"""Exploratory learner variants for the learned selector (val/test only). Usage: python exp.py name [name...]
Imports from scripts/eval_triggers.py and scripts/eval_baselines.py (not modified)."""
import json
import os
import sys
import time

import numpy as np

ROOT = "/home/user/CASS-VLA"
sys.path.insert(0, ROOT + "/scripts")
import eval_baselines as E  # noqa: E402
import eval_triggers as T  # noqa: E402

OUT = ROOT + "/research/2026-11-19_learned_selector/experiments"
SEEDS = (0, 1, 2)
H, EPOCHS, LR, L2 = 32, 300, 0.01, 1e-3


# ---------- trainers ----------
def adam_fit(Z, nout, gradfn, seed, hidden=H, epochs=EPOCHS, lr=LR, l2=L2):
    """Same architecture/init/optimizer as E.fit_mlp; gradfn(out)->dL/dout (already divided by n), linear outputs."""
    rng = np.random.default_rng(seed)
    params = [rng.normal(0, 1 / np.sqrt(Z.shape[1]), (Z.shape[1], hidden)), np.zeros(hidden),
              rng.normal(0, 1 / np.sqrt(hidden), (hidden, nout)), np.zeros(nout)]
    m1, m2 = [np.zeros_like(q) for q in params], [np.zeros_like(q) for q in params]
    for step in range(1, epochs + 1):
        W1, b1, W2, b2 = params
        h = np.maximum(Z @ W1 + b1, 0)
        g = gradfn(h @ W2 + b2)
        gh = (g @ W2.T) * (h > 0)
        grads = [Z.T @ gh + l2 * W1, gh.sum(axis=0), h.T @ g + l2 * W2, g.sum(axis=0)]
        for k, (q, gr) in enumerate(zip(params, grads)):
            m1[k] = 0.9 * m1[k] + 0.1 * gr
            m2[k] = 0.999 * m2[k] + 0.001 * gr * gr
            q -= lr * (m1[k] / (1 - 0.9 ** step)) / (np.sqrt(m2[k] / (1 - 0.999 ** step)) + 1e-8)
    return params


def fwd(params, Z):
    W1, b1, W2, b2 = params
    return np.maximum(Z @ W1 + b1, 0) @ W2 + b2


def std(Xtr):
    return Xtr.mean(axis=0), Xtr.std(axis=0) + 1e-6


def fit_reg(X, y, loss="mse", seed=0, delta=0.2, w=None):
    mu, sd = std(X)
    Z = (X - mu) / sd
    n = len(Z)

    def gf(o):
        r = o - y
        return (r if loss == "mse" else np.clip(r, -delta, delta)) * (1 if w is None else w) / n
    P = adam_fit(Z, y.shape[1], gf, seed)
    return lambda Xn: fwd(P, (Xn - mu) / sd)


def fit_softmax(X, q, seed=0):
    mu, sd = std(X)
    Z = (X - mu) / sd
    n = len(Z)

    def sm(o):
        e = np.exp(o - o.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)
    P = adam_fit(Z, q.shape[1], lambda o: (sm(o) - q) / n, seed)
    return lambda Xn: sm(fwd(P, (Xn - mu) / sd))


def fit_pairwise(X, gdec, seed=0, npairs=8192):
    """Scalar decision score s(x); logistic loss on random pairs with different gdec, fresh pairs every step."""
    mu, sd = std(X)
    Z = (X - mu) / sd
    n = len(Z)
    prng = np.random.default_rng(1000 + seed)
    rng = np.random.default_rng(seed)
    params = [rng.normal(0, 1 / np.sqrt(Z.shape[1]), (Z.shape[1], H)), np.zeros(H), rng.normal(0, 1 / np.sqrt(H), (H, 1)), np.zeros(1)]
    m1, m2 = [np.zeros_like(q) for q in params], [np.zeros_like(q) for q in params]
    for step in range(1, EPOCHS + 1):
        i, j = prng.integers(n, size=npairs), prng.integers(n, size=npairs)
        keep = gdec[i] != gdec[j]
        i, j = i[keep], j[keep]
        sw = np.sign(gdec[i] - gdec[j])
        W1, b1, W2, b2 = params
        hi, hj = np.maximum(Z[i] @ W1 + b1, 0), np.maximum(Z[j] @ W1 + b1, 0)
        d = ((hi - hj) @ W2)[:, 0] * sw
        gd = -sw / (1 + np.exp(d)) / len(i)
        gi = gd[:, None] * W2[:, 0][None, :] * (hi > 0)
        gj = -gd[:, None] * W2[:, 0][None, :] * (hj > 0)
        grads = [Z[i].T @ gi + Z[j].T @ gj + L2 * W1, gi.sum(0) + gj.sum(0),
                 ((hi - hj).T @ gd)[:, None] + L2 * W2, np.zeros(1)]
        for k, (q, gr) in enumerate(zip(params, grads)):
            m1[k] = 0.9 * m1[k] + 0.1 * gr
            m2[k] = 0.999 * m2[k] + 0.001 * gr * gr
            q -= LR * (m1[k] / (1 - 0.9 ** step)) / (np.sqrt(m2[k] / (1 - 0.999 ** step)) + 1e-8)
    return lambda Xn: fwd(params, (Xn - mu) / sd)[:, 0]


def pav(x, y):
    """Isotonic (non-decreasing) fit; returns a step function."""
    o = np.argsort(x, kind="stable")
    xs, ys = x[o], y[o]
    vals, wts, ends = [], [], []
    for k in range(len(ys)):
        vals.append(ys[k]); wts.append(1.0); ends.append(xs[k])
        while len(vals) > 1 and vals[-2] >= vals[-1]:
            w = wts[-2] + wts[-1]
            v = (vals[-2] * wts[-2] + vals[-1] * wts[-1]) / w
            vals[-2:] = [v]; wts[-2:] = [w]; ends[-2:] = [ends[-1]]
    ends, vals = np.array(ends), np.array(vals)
    return lambda q: vals[np.clip(np.searchsorted(ends, q, side="left"), 0, len(vals) - 1)]


def platt(p, y, iters=30):
    """Fit sigmoid(a*logit(p)+b) to soft targets y by Newton."""
    def lg(v):
        v = np.clip(v, 1e-6, 1 - 1e-6)
        return np.log(v / (1 - v))
    z = lg(p)
    a, b = 1.0, 0.0
    for _ in range(iters):
        q = 1 / (1 + np.exp(-(a * z + b)))
        r = q - y
        w = q * (1 - q) + 1e-9
        g = np.array([(r * z).mean(), r.mean()])
        Hm = np.array([[(w * z * z).mean(), (w * z).mean()], [(w * z).mean(), w.mean()]]) + 1e-6 * np.eye(2)
        a, b = np.array([a, b]) - np.linalg.solve(Hm, g)
    return lambda pn: 1 / (1 + np.exp(-(a * lg(pn) + b)))


# ---------- data ----------
def load(expgain=("v2_expgain.jsonl", "v2_extra_expgain.jsonl"), train_dirs=("v2_dataset", "v2_extra_ds"), test_dir="v2_dataset", split_names=("val", "test")):
    """Paths are relative to out/. The defaults are the original val/test setup."""
    D = ROOT + "/out/"
    eg = {}
    for p in expgain:
        eg.update({T.key(r): r for r in map(json.loads, open(os.path.join(D, p)))})
    man = json.load(open(D + "v2_dataset/manifest.json"))
    names = man["feature_names"]
    agn = [names.index(k) for k in man["agnostic_features"]]
    train = [r for d in train_dirs for r in E.load(os.path.join(D, d), "train")]
    train = [r for r in train if T.key(r) in eg]
    splits = {s: [r for r in E.load(os.path.join(D, test_dir), s) if T.key(r) in eg] for s in split_names}
    return eg, agn, train, splits


class Cell:
    def __init__(s, test, lv, eg):
        s.a0, s.u0, s.at, s.ut, s.aa, s.ua = E.tables(test, lv, "correct")
        s.ge = np.array([[eg[T.key(r)][lv][t] for t in E.TOOLS] for r in test]) - s.a0[:, None]
        s.fams = np.array([r["family"] for r in test])
        s.seeds = np.array([r["seed"] for r in test])
        s.X = np.array([r["features"] for r in test], float)


def evaluate(cell, runs):
    """runs: list over init seeds of (score, tool, allow_or_None)."""
    res = []
    for s, (score, tool, allow) in enumerate(runs):
        order = E.rank_desc(score, np.random.default_rng(s))
        masks = [T.mask_for(order, b) & (allow if allow is not None else True) for b in E.BUDGETS]
        res.append(T.summarize(masks, tool, cell.a0, cell.at, cell.ge, cell.fams, cell.u0, cell.ut))
    out = dict(mean_acc=round(float(np.mean([r["mean_acc"] for r in res])), 4), by_seed=[r["mean_acc"] for r in res],
               mean_unsafe=round(float(np.mean([r["mean_unsafe"] for r in res])), 4),
               curve=[round(float(np.mean([r["curve"][i] for r in res])), 4) for i in range(len(E.BUDGETS))],
               by_budget={b: {k: round(float(np.mean([r["by_budget"][b][k] for r in res])), 4) for k in ("acc", "unsafe", "harm_rate", "benefit_captured")}
                          for b in res[0]["by_budget"]})
    out["unsafe_curve"] = [round(float(np.mean([r["unsafe_curve"][i] for r in res])), 4) for i in range(len(E.BUDGETS))]
    out["by_family"] = {f: round(float(np.mean([r["by_family"][f] for r in res])), 4) for f in res[0]["by_family"]}
    pos = cell.ge.max(1) > 0
    out["tool_optimal_rate"] = round(float(np.mean([(r_[1][pos] == cell.ge.argmax(1)[pos]).mean() for r_ in runs])), 4)
    out["tool_share"] = [round(float(np.mean([(r_[1] == j).mean() for r_ in runs])), 3) for j in range(3)]
    out["_dec"] = np.mean([r["_dec"] for r in res], axis=0)
    return out


# ---------- variants: fn(c, Xtr, Xeval, seed) -> (score, tool, allow) ----------
def v_frozen(c, X, Xte, seed):
    pr = E.predict(E.fit_mlp(X, c["g"], seed=seed), Xte)
    return pr.max(1), pr.argmax(1), None


def v_signed(loss, abstain):
    def f(c, X, Xte, seed):
        pr = fit_reg(X, c["gs"], loss, seed)(Xte)
        return pr.max(1), pr.argmax(1), (pr.max(1) > 0) if abstain else None
    return f


def v_signed_toolw(c, X, Xte, seed):
    best = c["gs"].argmax(1)[c["gs"].max(1) > 0]
    fr = np.bincount(best, minlength=3) / len(best)
    w = (1 / fr) / (1 / fr).mean()
    pr = fit_reg(X, c["gs"], "mse", seed, w=w)(Xte)
    return pr.max(1), pr.argmax(1), pr.max(1) > 0


def v_cal(kind):
    def f(c, X, Xte, seed):
        tr, cal = c["fit_idx"], c["cal_idx"]
        m = E.fit_mlp(X[tr], c["g"][tr], seed=seed)
        pt = E.predict(m, Xte)
        if kind == "none":
            pr = pt
        else:
            pc = E.predict(m, X[cal])
            pr = np.zeros_like(pt)
            for j in range(3):
                cf = pav(pc[:, j], c["g"][cal][:, j]) if kind == "iso" else platt(pc[:, j], c["g"][cal][:, j])
                pr[:, j] = cf(pt[:, j])
        return pr.max(1), pr.argmax(1), None
    return f


def v_softmax(c, X, Xte, seed):
    g = c["g"]
    q = np.hstack([g, (1 - g.max(1))[:, None]])
    q = q / np.clip(q.sum(1, keepdims=True), 1e-9, None)
    p = fit_softmax(X, q, seed)(Xte)
    return 1 - p[:, 3], p[:, :3].argmax(1), None


def v_pair(c, X, Xte, seed):
    f = fit_pairwise(X, c["g"].max(1), seed)(Xte)
    pr = E.predict(E.fit_mlp(X, c["g"], seed=seed), Xte)
    return f, pr.argmax(1), None


VARIANTS = {
    "frozen": (v_frozen, ("plandiscrim", "scene_only")),
    "signed_mse_abstain": (v_signed("mse", True), ("plandiscrim", "scene_only")),
    "signed_mse_noabstain": (v_signed("mse", False), ("plandiscrim", "scene_only")),
    "signed_mse_abstain_toolw": (v_signed_toolw, ("plandiscrim", "scene_only")),
    "signed_huber_abstain": (v_signed("huber", True), ("plandiscrim", "scene_only")),
    "cal_control_80pct": (v_cal("none"), ("plandiscrim",)),
    "cal_isotonic": (v_cal("iso"), ("plandiscrim",)),
    "cal_platt": (v_cal("platt"), ("plandiscrim",)),
    "softmax_none": (v_softmax, ("plandiscrim", "scene_only")),
    "pairwise_rank": (v_pair, ("plandiscrim",)),
}


def run(names, out_path=None, featsets=None, **loadkw):
    """out_path: write one combined json there instead of the res_<variant>.json files. featsets: restrict feature sets."""
    eg, agn, train, splits = load(**loadkw)
    sp_names = list(splits)
    print("n_train", len(train), {k: len(v) for k, v in splits.items()}, flush=True)
    X = np.array([r["features"] for r in train], float)
    F = dict(plandiscrim=(X, lambda A: A), scene_only=(X[:, agn], lambda A: A[:, agn]))
    tseeds = np.array([r["seed"] for r in train])
    u = np.unique(tseeds)
    cal_seeds = set(np.random.default_rng(123).choice(u, size=int(0.2 * len(u)), replace=False).tolist())
    cal_mask = np.array([s in cal_seeds for s in tseeds])
    cells = {(sp, lv): Cell(splits[sp], lv, eg) for sp in splits for lv in ("low", "mid", "high")}
    out = {n: {} for n in names}
    out.setdefault("frozen", {})
    frozen_dec = {}
    for lv in ("low", "mid", "high"):
        a0t = E.tables(train, lv, "correct")[0]
        egt = np.array([[eg[T.key(r)][lv][t] for t in E.TOOLS] for r in train]) - a0t[:, None]
        c = dict(g=np.clip(egt, 0, 1), gs=egt, fit_idx=np.where(~cal_mask)[0], cal_idx=np.where(cal_mask)[0])
        for n in dict.fromkeys(["frozen"] + names):
            fn, fsets = VARIANTS[n]
            for fs in fsets:
                if featsets and fs not in featsets:
                    continue
                Xtr, sel = F[fs]
                t0 = time.time()
                preds = {(sp, lv): [] for sp in sp_names}
                Xall = np.vstack([sel(cells[(sp, lv)].X) for sp in sp_names])
                bounds = np.cumsum([0] + [len(cells[(sp, lv)].X) for sp in sp_names])
                for sd in SEEDS:
                    sc, tl, al = fn(c, Xtr, Xall, sd)
                    for i, sp in enumerate(sp_names):
                        sl = slice(bounds[i], bounds[i + 1])
                        preds[(sp, lv)].append((sc[sl], tl[sl], None if al is None else al[sl]))
                for k, runs in preds.items():
                    r = evaluate(cells[k], runs)
                    r["drop_after_peak"] = round(max(r["curve"]) - r["curve"][-1], 4)
                    tag = f"{k[0]}/{lv}/{fs}"
                    if n == "frozen":
                        frozen_dec[tag] = r["_dec"]
                    else:
                        d = r["_dec"] - frozen_dec[tag]
                        r["diff_vs_frozen"] = dict(mean=round(float(d.mean()), 4), ci95=E.seed_boot(d, cells[k].seeds, np.random.default_rng(0)))
                        cu = r["curve"]
                        r["peak_budget"] = float(E.BUDGETS[int(np.argmax(cu))])
                        r["acc_at_peak"] = max(cu)
                        r["acc_at_1.0"] = cu[-1]
                        r["drop_after_0.65"] = round(max(cu[13:]) - cu[-1], 4)
                    r.pop("_dec")
                    out[n][tag] = r
                print(lv, n, fs, f"{time.time() - t0:.0f}s", flush=True)
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        json.dump(dict(n_train=len(train), n_test={k: len(v) for k, v in splits.items()}, seeds=list(SEEDS), results=out), open(out_path, "w"), indent=1)
        for n in out:
            for tag, r in out[n].items():
                print(n, tag, r["mean_acc"], r.get("diff_vs_frozen", ""), flush=True)
        return
    for n in out:
        json.dump(out[n], open(f"{OUT}/res_{n}.json", "w"), indent=1)
    ref = json.load(open(ROOT + "/out/v3_eval/triggers.json"))["results"]
    for n in out:
        for tag, r in out[n].items():
            sp, lv, fs = tag.split("/")
            if n == "frozen":
                print(n, tag, r["mean_acc"], "triggers.json", ref[f"{sp}/{lv}"]["plandiscrim" if fs == "plandiscrim" else "scene_only"]["mean_acc"])
            else:
                print(n, tag, r["mean_acc"], r["diff_vs_frozen"], "peak", r["peak_budget"], "drop>.65", r["drop_after_0.65"])


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Learner variants. With no options: the original val/test run, writing res_<variant>.json.")
    p.add_argument("names", nargs="+", help="variant names")
    p.add_argument("--train-dirs", nargs="+", default=["v2_dataset", "v2_extra_ds"], help="dirs under out/ whose train.jsonl is the training set")
    p.add_argument("--expgain", nargs="+", default=["v2_expgain.jsonl", "v2_extra_expgain.jsonl"], help="files under out/")
    p.add_argument("--test-dir", default="v2_dataset", help="dir under out/ holding the evaluated split files")
    p.add_argument("--splits", nargs="+", default=["val", "test"], help="split file stems, e.g. final for final.jsonl")
    p.add_argument("--featsets", nargs="+", default=None, help="restrict to plandiscrim and/or scene_only")
    p.add_argument("--out", default=None, help="write one combined json here instead of res_<variant>.json")
    a = p.parse_args()
    run(a.names, out_path=a.out, featsets=a.featsets, expgain=tuple(a.expgain), train_dirs=tuple(a.train_dirs), test_dir=a.test_dir, split_names=tuple(a.splits))
