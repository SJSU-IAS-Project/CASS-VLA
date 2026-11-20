"""Run-2 exploratory experiments A-D against signed_mse_abstain (val/test of out/v2_dataset only).
Usage: python exp2.py {AC,B,D}   Imports exp.py (a copy of the run-1 harness, method code unchanged)."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp as X  # noqa: E402
E, T = X.E, X.T
ROOT = X.ROOT
LEVELS = ("low", "mid", "high")
OFFS = np.round(np.arange(-0.10, 0.1001, 0.02), 3)
EPS = [0.0, 0.01, 0.02, 0.03, 0.05, 0.08]


def rid(r):
    return r["family"], int(r["seed"]), round(float(r["t_dec"]), 1)


def load_vlm_field(paths, wanted):
    emb = {}
    for p in paths:
        z = np.load(p)
        fam, sd, td = z["family"], z["seed"], z["t_dec"]
        v = z["image_mid"].astype(np.float32)
        for f, s, t, e in zip(fam, sd, td, v):
            k = (str(f), int(s), round(float(t), 1))
            if k in wanted:
                emb[k] = e.copy()
        del v, z
    return emb


def holdout_split(train):
    ts = np.array([r["seed"] for r in train])
    u = np.unique(ts)
    hs = set(np.random.default_rng(123).choice(u, size=int(0.2 * len(u)), replace=False).tolist())
    m = np.array([s in hs for s in ts])
    return np.where(~m)[0], np.where(m)[0]


class Ctx:
    def __init__(s, train_dirs, expgain, vlm=None, test_dir="v2_dataset", split_names=("val", "test"), strict_vlm=False):
        s.eg, s.agn, s.train, s.splits = X.load(expgain=expgain, train_dirs=train_dirs, test_dir=test_dir, split_names=split_names)
        if vlm:
            wanted = {rid(r) for r in s.train} | {rid(r) for sp in s.splits.values() for r in sp}
            emb = load_vlm_field(vlm, wanted)
            if strict_vlm and len(emb) < len(wanted):
                miss = wanted - set(emb)
                print(f"REFUSING to run signed_vlm: {len(miss)} of {len(wanted)} train/test rows have no embedding in {vlm} (e.g. {sorted(miss)[:3]})", file=sys.stderr)
                sys.exit(2)
            s.train = [r for r in s.train if rid(r) in emb]
            s.splits = {k: [r for r in v if rid(r) in emb] for k, v in s.splits.items()}
            Etr = np.array([emb[rid(r)] for r in s.train])
            mu = Etr.mean(axis=0)
            C = np.zeros((Etr.shape[1],) * 2)
            for i in range(0, len(Etr), 2000):
                B = (Etr[i:i + 2000] - mu).astype(np.float64)
                C += B.T @ B
            w, vecs = np.linalg.eigh(C)
            proj = vecs[:, ::-1][:, :32].astype(np.float32)  # top-32 PCA directions via the covariance (same subspace as SVD, lower memory)
            del C
            s.V = lambda rows: (np.array([emb[rid(r)] for r in rows]) - mu) @ proj
            del Etr
        s.sp = list(s.splits)
        s.fit_idx, s.cal_idx = holdout_split(s.train)
        s.Xtr = np.array([r["features"] for r in s.train], float)
        s.cells = {(sp, lv): X.Cell(s.splits[sp], lv, s.eg) for sp in s.sp for lv in LEVELS}
        s.hold = {lv: X.Cell([s.train[i] for i in s.cal_idx], lv, s.eg) for lv in LEVELS}
        print("n_train", len(s.train), {k: len(v) for k, v in s.splits.items()}, "hold", len(s.cal_idx), flush=True)

    def feats(s, fs):
        if fs == "plandiscrim":
            return s.Xtr, {sp: s.cells[(sp, "mid")].X for sp in s.sp}
        if fs == "scene_only":
            return s.Xtr[:, s.agn], {sp: s.cells[(sp, "mid")].X[:, s.agn] for sp in s.sp}
        if fs == "geom_vlm":
            if not hasattr(s, "_gv"):
                s._gv = (np.hstack([s.Xtr, s.V(s.train)]),
                    {sp: np.hstack([s.cells[(sp, "mid")].X, s.V(s.splits[sp])]) for sp in s.sp})
            return s._gv
        raise KeyError(fs)

    def gains(s, lv):
        a0 = E.tables(s.train, lv, "correct")[0]
        return np.array([[s.eg[T.key(r)][lv][t] for t in E.TOOLS] for r in s.train]) - a0[:, None]


def summarize(r):
    return dict(mean_acc=r["mean_acc"], mean_unsafe=r["mean_unsafe"], drop_after_peak=round(max(r["curve"]) - r["curve"][-1], 4),
                peak_budget=float(E.BUDGETS[int(np.argmax(r["curve"]))]), acc_at_1=r["curve"][-1], tool_optimal=r["tool_optimal_rate"],
                tool_share=r["tool_share"], curve=r["curve"], unsafe_curve=r.get("unsafe_curve"), by_family=r.get("by_family"),
                harm={b: r["by_budget"][b]["harm_rate"] for b in ("0.1", "0.2", "0.3", "0.5")},
                benefit={b: r["by_budget"][b]["benefit_captured"] for b in ("0.1", "0.2", "0.3", "0.5")})


def run_variants(ctx, variants, out_path, levels=LEVELS):
    """variants: {name: fn(ctx, lv, g, seed, cache) -> ({split: (score, tool, allow)}, info)}; 'base' is the comparator."""
    res = {n: {} for n in variants}
    extra = {}
    for lv in levels:
        egt = ctx.gains(lv)
        cache = {}
        for n, fn in variants.items():
            t0 = time.time()
            runs = {sp: [] for sp in ctx.sp}
            info = []
            for sd in X.SEEDS:
                o, inf = fn(ctx, lv, egt, sd, cache)
                info.append(inf)
                for sp in ctx.sp:
                    runs[sp].append(o[sp])
            extra[f"{n}/{lv}"] = info
            for sp in ctx.sp:
                res[n][f"{sp}/{lv}"] = X.evaluate(ctx.cells[(sp, lv)], runs[sp])
            print(lv, n, f"{time.time() - t0:.0f}s", {sp: res[n][f"{sp}/{lv}"]["mean_acc"] for sp in ctx.sp}, flush=True)
    out = {}
    for n in res:
        out[n] = {}
        for tag, r in res[n].items():
            sp, lv = tag.split("/")
            s = summarize(r)
            if n != "base":
                dd = r["_dec"] - res["base"][tag]["_dec"]
                s["diff_vs_base"] = dict(mean=round(float(dd.mean()), 4), ci95=E.seed_boot(dd, ctx.cells[(sp, lv)].seeds, np.random.default_rng(0)))
            out[n][tag] = s
    json.dump(dict(n_train=len(ctx.train), results=out, info=extra), open(out_path, "w"), indent=1,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    return out


def signed(ctx, lv, g, seed, cache, fs, sub=None):
    k = ("s", fs, seed, sub)
    if k not in cache:
        Xtr, Xev = ctx.feats(fs)
        idx = np.arange(len(Xtr)) if sub is None else ctx.fit_idx
        m = X.fit_reg(Xtr[idx], g[idx], "mse", seed)
        cache[k] = dict(ev={sp: m(Xev[sp]) for sp in ctx.sp}, hold=m(Xtr[ctx.cal_idx]))
    return cache[k]


def frozen_tool(ctx, lv, g, seed, cache, fs):
    k = ("f", fs, seed)
    if k not in cache:
        Xtr, Xev = ctx.feats(fs)
        m = E.fit_mlp(Xtr, np.clip(g, 0, 1), seed=seed)
        cache[k] = {sp: E.predict(m, Xev[sp]) for sp in ctx.sp}
    return cache[k]


def mk_signed(fs, sub=None):
    def f(ctx, lv, g, seed, cache):
        p = signed(ctx, lv, g, seed, cache, fs, sub)["ev"]
        return {sp: (p[sp].max(1), p[sp].argmax(1), p[sp].max(1) > 0) for sp in ctx.sp}, None
    return f


def best_offsets(pred, ge, objective):
    """Grid over additive offsets of tools 1 and 2 (tool 0 fixed at 0); ties go to the smaller offset."""
    call = pred.max(1) > 0
    pos = ge.max(1) > 0
    best, bo = -1e9, (0.0, 0.0, 0.0)
    for o1 in OFFS:
        for o2 in OFFS:
            off = np.array([0.0, o1, o2])
            tl = (pred + off).argmax(1)
            if objective == "optimal":
                v = (tl[pos] == ge.argmax(1)[pos]).mean()
            else:
                v = ge[np.arange(len(ge)), tl][call].sum() / len(ge)
            if v > best + 1e-12 or (abs(v - best) <= 1e-12 and abs(o1) + abs(o2) < abs(bo[1]) + abs(bo[2])):
                best, bo = v, (0.0, float(o1), float(o2))
    return np.array(bo), best


def mk_offset(objective, use80):
    def f(ctx, lv, g, seed, cache):
        m80 = signed(ctx, lv, g, seed, cache, "plandiscrim", "80")
        off, v = best_offsets(m80["hold"], g[ctx.cal_idx], objective)
        p = (m80 if use80 else signed(ctx, lv, g, seed, cache, "plandiscrim"))["ev"]
        return {sp: (p[sp].max(1), (p[sp] + off).argmax(1), p[sp].max(1) > 0) for sp in ctx.sp}, dict(offsets=off.tolist(), holdout_value=v)
    return f


def hybrid(ctx, lv, g, seed, cache):
    p = signed(ctx, lv, g, seed, cache, "plandiscrim")["ev"]
    fr = frozen_tool(ctx, lv, g, seed, cache, "plandiscrim")
    return {sp: (p[sp].max(1), fr[sp].argmax(1), p[sp].max(1) > 0) for sp in ctx.sp}, None


def mk_eps(fixed=None):
    def f(ctx, lv, g, seed, cache):
        sc = signed(ctx, lv, g, seed, cache, "plandiscrim", "80")["hold"]
        best, be, tab = -1, 0.0, {}
        for e in EPS:
            r = X.evaluate(ctx.hold[lv], [(sc.max(1), sc.argmax(1), sc.max(1) > e)])
            tab[e] = r["mean_acc"]
            if r["mean_acc"] > best + 1e-9:
                best, be = r["mean_acc"], e
        e = be if fixed is None else fixed
        p = signed(ctx, lv, g, seed, cache, "plandiscrim")["ev"]
        return {sp: (p[sp].max(1), p[sp].argmax(1), p[sp].max(1) > e) for sp in ctx.sp}, dict(eps=e, holdout_curve=tab)
    return f


if __name__ == "__main__":
    which = sys.argv[1]
    D = ("v2_dataset", "v2_extra_ds", "v3_extra_ds")
    G = ("v2_expgain.jsonl", "v2_extra_expgain.jsonl", "v3_extra_expgain.jsonl")
    if which == "AC":
        ctx = Ctx(D, G)
        run_variants(ctx, {"base": mk_signed("plandiscrim"), "A_offset_optimal": mk_offset("optimal", False), "A_offset_gain": mk_offset("gain", False),
                           "A_ctrl80": mk_signed("plandiscrim", "80"), "A_offset_optimal_80": mk_offset("optimal", True), "A_offset_gain_80": mk_offset("gain", True),
                           "A_hybrid": hybrid, "C_scene_signed": mk_signed("scene_only")}, HERE + "/res2_AC.json")
    elif which == "D":
        ctx = Ctx(D, G)
        run_variants(ctx, {"base": mk_signed("plandiscrim"), "D_eps_heldout": mk_eps(), "D_eps_0.02": mk_eps(0.02), "D_eps_0.05": mk_eps(0.05)}, HERE + "/res2_D.json")
    elif which == "B":
        ctx = Ctx(D[:2], G[:2], vlm=[ROOT + "/out/vlm_main/embed.npz", ROOT + "/out/vlm_extra/embed.npz"])
        run_variants(ctx, {"base": mk_signed("plandiscrim"), "B_signed_vlm": mk_signed("geom_vlm"), "B_scene_signed": mk_signed("scene_only")}, HERE + "/res2_B.json")
