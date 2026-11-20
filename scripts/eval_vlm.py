"""Phase 5 evaluation: do cached VLM features improve the tool selector?

    python scripts/eval_vlm.py --data out/v2_dataset --embed out/vlm_main/embed.npz --expgain out/v2_expgain.jsonl --out out/v2_eval/vlm.json

Question and decision rule, fixed on 2026-11-06 before any VLM feature existed: the VLM features help if the
MLP selector that sees geometry plus VLM features beats the geometry-only selector on both val and test at all of
low, mid and high noise, averaged over 3 init seeds. Training uses expected-gain targets (DECISIONS.md,
2026-11-06). The VLM features are a PCA of the mean image-token state at the middle layer, fitted on train only.
The final split is not used here.

Rows: geometry selector, scene-only MLP (ranker margin plus scene features), VLM-only MLP (VLM features plus ranker
margin), geometry plus VLM, and the fair ceiling. With --prompt, the prompted VLM's tool choice is scored as a
fixed policy at its own call rate, next to the selectors at that budget.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eval_baselines as E  # noqa: E402

PCA_DIM = 32


def key(r):
    return r["family"], int(r["seed"]), round(float(r["t_dec"]), 1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--embed", required=True, nargs="+")
    p.add_argument("--expgain", required=True, nargs="+")
    p.add_argument("--extra-train", default=None, help="dataset dir whose train split is added to training")
    p.add_argument("--prompt", default=None, nargs="*", help="prompt_<split>.jsonl files from vlm_encode.py")
    p.add_argument("--field", default="image_mid")
    p.add_argument("--control", default="none", choices=("none", "shuffle", "shuffle_family", "family"),
                   help="shuffle VLM features across rows, within family, or swap them for a family one-hot")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    emb = {}
    for path in args.embed:
        z = np.load(path)
        for f, s, t, v in zip(z["family"], z["seed"], z["t_dec"], z[args.field]):
            emb[str(f), int(s), round(float(t), 1)] = v.astype(np.float32)
    eg = {}
    for path in args.expgain:
        eg.update({key(r): r for r in map(json.loads, open(path))})
    prompt = {}
    for path in args.prompt or []:
        prompt.update({key(r): r["tool"] for r in map(json.loads, open(path))})

    man = json.load(open(os.path.join(args.data, "manifest.json")))
    agn = [man["feature_names"].index(k) for k in man["agnostic_features"]]
    margin = [man["feature_names"].index("margin")]
    train = E.load(args.data, "train") + (E.load(args.extra_train, "train") if args.extra_train else [])
    train = [r for r in train if key(r) in emb]
    Etr = np.array([emb[key(r)] for r in train])
    mu = Etr.mean(axis=0)
    _, _, vt = np.linalg.svd(Etr - mu, full_matrices=False)
    proj = vt[:PCA_DIM].T

    families = sorted({r["family"] for r in train})

    def feats(rows):
        X = np.array([r["features"] for r in rows], float)
        V = (np.array([emb[key(r)] for r in rows]) - mu) @ proj
        fam = np.array([r["family"] for r in rows])
        rng = np.random.default_rng(len(rows))
        if args.control == "shuffle":
            V = V[rng.permutation(len(V))]
        elif args.control == "shuffle_family":
            for f in families:
                i = np.flatnonzero(fam == f)
                V[i] = V[rng.permutation(i)]
        elif args.control == "family":
            V = (fam[:, None] == np.array(families)[None, :]).astype(float)
        return dict(geometry=X, scene_only=X[:, agn], vlm_only=np.hstack([V, X[:, margin]]), geometry_vlm=np.hstack([X, V]))

    Ftr = feats(train)
    out = dict(n_train=len(train), pca_dim=PCA_DIM, field=args.field, control=args.control, results={})
    for split in ("val", "test"):
        test = [r for r in E.load(args.data, split) if key(r) in emb]
        Fte = feats(test)
        for lv in ("low", "mid", "high"):
            a0, u0, at, ut, _, _ = E.tables(test, lv, "correct")
            a0t, _, _, _, _, _ = E.tables(train, lv, "correct")
            g = np.clip(np.array([[eg[key(r)][lv][t] for t in E.TOOLS] for r in train]) - a0t[:, None], 0, 1)
            res = {}
            for name in Ftr:
                curves = []
                for s in range(3):
                    pr = E.predict(E.fit_mlp(Ftr[name], g, seed=s), Fte[name])
                    curves.append(E.curve(E.rank_desc(pr.max(axis=1), np.random.default_rng(s)), pr.argmax(axis=1), a0, u0, at, ut))
                res[name] = dict(mean_acc=round(float(np.mean([[pt[0] for pt in c] for c in curves])), 4),
                                 by_seed=[round(float(np.mean([pt[0] for pt in c])), 4) for c in curves],
                                 curve=[round(float(np.mean([c[i][0] for c in curves])), 4) for i in range(len(E.BUDGETS))])
            ge = np.array([[eg[key(r)][lv][t] for t in E.TOOLS] for r in test]) - a0[:, None]
            gmax = ge.max(axis=1)
            o, npos = E.rank_desc(gmax, np.random.default_rng(0)), int((gmax > 0).sum())
            res["fair_ceiling"] = dict(mean_acc=round(float(np.mean([E.apply_policy(o[:npos], ge.argmax(axis=1), a0, u0, at, ut, min(b, npos / len(a0)))[0].mean()
                                                                    for b in E.BUDGETS])), 4))
            if prompt:
                tool = np.array([prompt.get(key(r)) for r in test], dtype=object)
                have = np.array([t is not None for t in tool])
                call = np.array([t in E.TOOLS for t in tool])
                idx = np.array([E.TOOLS.index(t) if t in E.TOOLS else 0 for t in tool])
                acc = np.where(call, at[np.arange(len(a0)), idx], a0)
                res["prompted"] = dict(n=int(have.sum()), call_rate=round(float(call[have].mean()), 4) if have.any() else None,
                                       acc=round(float(acc[have].mean()), 4) if have.any() else None,
                                       no_tool_acc=round(float(a0[have].mean()), 4) if have.any() else None)
            out["results"][f"{split}/{lv}"] = res
            line = "  ".join(f"{k} {v['mean_acc']:.4f}" for k, v in res.items() if "mean_acc" in v)
            print(f"{split:4s} {lv:4s} n={len(test)}  {line}", flush=True)
    wins = [out["results"][c]["geometry_vlm"]["mean_acc"] > out["results"][c]["geometry"]["mean_acc"] for c in out["results"]]
    out["decision_rule_met"] = bool(all(wins))
    print(f"geometry+VLM beats geometry in {sum(wins)} of {len(wins)} cells; rule met: {out['decision_rule_met']}")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()
