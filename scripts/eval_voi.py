"""The VoI selector against the learned selector, in Max's final-run harness (research/.../run2/experiments/final.py).

    OMP_NUM_THREADS=1 python scripts/eval_voi.py --voi voi=out/voi/v2_uniform.jsonl voi_fitted=out/voi/v2_fitted.jsonl \
        --methods voi voi_budget voi_fitted signed uncertainty_margin always_on --test-dir v2_dataset --test-expgain v2_expgain.jsonl \
        --splits val --out out/voi_eval/val.json
    python scripts/eval_voi.py --report out/voi_eval/val.json --md research/2026-11-20_voi_selector/VAL_RESULTS.md
    python scripts/eval_voi.py --print-ablation-commands out/v2_sweep out/v2_dataset/manifest.json val   # then score with
    python scripts/eval_voi.py --voi abl_reference=out/voi/abl_reference.jsonl ... --methods abl_reference ... --compare-to abl_reference

Every VoI file given as NAME=FILE is a method NAME (call the best tool only when its VoI > 0) and NAME_budget (no
abstention, budget only). signed, frozen, signed_scene, uncertainty_margin and always_on come from the harness
unchanged, so all methods share rows, budgets, tie-breaking and the seed bootstrap. VoI is deterministic, so it has
one run where the learned selectors average 3 init seeds. A method whose name contains "vlm" gets a cost_offset of
--vlm-cost per decision (the VLM call). Hypotheses V1-V4 are the ones in research/2026-11-20_voi_selector/PREREG3.md.
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
HARNESS = os.path.join(ROOT, "research", "2026-11-19_learned_selector", "run2", "experiments", "final.py")
HARNESS_METHODS = ("signed", "frozen", "signed_scene", "uncertainty_margin", "always_on")
TOOLS = ("roi", "depth", "collision")
LEVELS = ("low", "mid", "high")


# VoI ablations on validation: (name, extra voi_scores.py arguments). Each writes out/voi/<name>.jsonl and is scored
# against abl_reference (uniform priors, 8 draws, every class, tool answers simulated at the true noise level).
ABLATIONS = (
    ("abl_reference", ""),
    ("abl_draws4", "--draws 4"),
    ("abl_draws16", "--draws 16"),
    ("abl_no_depth", "--classes null occl_static occl_ped light rear"),
    ("abl_no_occl_static", "--classes null depth occl_ped light rear"),
    ("abl_no_occl_ped", "--classes null depth occl_static light rear"),
    ("abl_no_light", "--classes null depth occl_static occl_ped rear"),
    ("abl_no_rear", "--classes null depth occl_static occl_ped light"),
    ("abl_fitted_priors", "--priors out/voi/priors_fitted.json"),
    ("abl_noise_unaware", "--sim-level mid"),
)


def ablation_commands(sweep, manifest, split):
    base = f"OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep {sweep} --manifest {manifest} --splits {split} --procs 8"
    return [f"{base} --out out/voi/{name}.jsonl {extra}".strip() for name, extra in ABLATIONS]


def key(r):
    return r["family"], int(r["seed"]), round(float(r["t_dec"]), 1)


def load_voi(path):
    with open(path) as f:
        rows = [json.loads(line) for line in f]
    if rows and "config" in rows[0]:
        rows = rows[1:]
    return rows


def align(voi_rows, split_rows, level, lam):
    """(score, tool, allow) in split_rows order. lam=None: no abstention. Aborts if any split row has no VoI."""
    idx = {key(r): r for r in voi_rows}
    miss = [key(r) for r in split_rows if key(r) not in idx]
    if miss:
        raise SystemExit(f"{len(miss)} of {len(split_rows)} rows have no VoI score (e.g. {miss[:3]})")
    v = np.array([[idx[key(r)]["levels"][level]["voi"][t] for t in TOOLS] for r in split_rows], float)
    score, tool = v.max(axis=1), v.argmax(axis=1)
    return score, tool, (None if lam is None else score > lam)


def _harness():
    spec = importlib.util.spec_from_file_location("final_harness", HARNESS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hypotheses(F, ctx, dec, levels, splits, have):
    """V1-V4 of PREREG3.md, from per-decision results."""
    out = {}
    for sp in splits:
        h = {}

        def diff(m1, m2, lv, field="mean"):
            seeds = ctx.cells[(sp, lv)].seeds
            d = dec[(f"{sp}/{lv}", m1)][field] - dec[(f"{sp}/{lv}", m2)][field]
            c = F.ci(d, seeds)
            return dict(mean_diff=round(float(d.mean()), 4), ci95=c)

        def rule(name, m1, m2, test, text):
            if m1 not in have or m2 not in have:
                h[name] = dict(rule=text, status="not run")
                return
            cells = {lv: diff(m1, m2, lv) for lv in levels}
            ok = len(cells) == 3 and all(test(c) for c in cells.values())
            h[name] = dict(rule=text, status="pass" if ok else "fail", cells=cells)
        rule("V1", "voi", "signed", lambda c: c["ci95"][0] > -0.01, "voi - signed mean accuracy over budgets: CI lower > -0.01 at all levels")
        rule("V2", "voi", "uncertainty_margin", lambda c: c["ci95"][0] > 0, "voi beats uncertainty_margin at all levels, CI above 0")
        rule("V4", "voi_vlm", "voi", lambda c: c["ci95"][0] > 0, "voi_vlm beats voi at all levels, CI above 0 (equal tool budget)")
        if {"voi", "always_on"} <= have:
            cells = {}
            for lv in levels:
                seeds, tag = ctx.cells[(sp, lv)].seeds, f"{sp}/{lv}"
                da, du = dec[(tag, "voi")]["acc_all"] - dec[(tag, "always_on")]["acc"], dec[(tag, "voi")]["uns_all"] - dec[(tag, "always_on")]["uns"]
                ca, cu = F.ci(da, seeds), F.ci(du, seeds)
                cells[lv] = dict(call_rate=dec[(tag, "voi")]["rate_all"], acc_diff=round(float(da.mean()), 4), acc_ci95=ca,
                                 unsafe_diff=round(float(du.mean()), 4), unsafe_ci95=cu)
            ok = len(cells) == 3 and all(c["acc_ci95"][0] > -0.01 and c["unsafe_ci95"][1] < 0.01 for c in cells.values())
            h["V3"] = dict(rule="at its own call rate (lambda=0, no budget cap), voi vs always_on: acc CI lower > -0.01 and unsafe CI upper < +0.01, all levels",
                           status="pass" if ok else "fail", cells=cells)
        else:
            h["V3"] = dict(rule="V3", status="not run")
        out[sp] = h
    return out


def run(args):
    F = _harness()
    M, X, E = F.M, F.X, F.E
    D = os.path.join(ROOT, "out")
    voi_files = dict(kv.split("=", 1) for kv in args.voi)
    voi_rows = {n: load_voi(p if os.path.isabs(p) else os.path.join(ROOT, p)) for n, p in voi_files.items()}
    ctx = M.Ctx(tuple(args.train_dirs), tuple(args.train_expgain) + tuple(args.test_expgain), test_dir=args.test_dir, split_names=tuple(args.splits))
    man = json.load(open(os.path.join(D, "v2_dataset", "manifest.json")))
    ctx.margin = man["feature_names"].index("margin")
    for sp in args.splits:
        n = sum(1 for _ in open(os.path.join(D, args.test_dir, sp + ".jsonl")))
        if len(ctx.splits[sp]) != n:
            raise SystemExit(f"{n - len(ctx.splits[sp])} {sp} rows have no expected-gain labels")
    last = len(E.BUDGETS) - 1
    res, dec = {}, {}
    for lv in args.levels:
        egt = ctx.gains(lv)
        tr_best = int(np.argmax(np.clip(egt, 0, 1).mean(axis=0)))
        cache = {}
        for name in args.methods:
            if name in HARNESS_METHODS:
                runs = F.run_method(name, ctx, lv, egt, cache, tr_best)
            else:
                base = name[:-len("_budget")] if name.endswith("_budget") else name
                if base not in voi_rows:
                    raise SystemExit(f"method {name}: no --voi {base}=FILE")
                lam = None if name.endswith("_budget") else args.lam
                runs = {sp: [align(voi_rows[base], ctx.splits[sp], lv, lam)] for sp in args.splits}
            for sp in args.splits:
                cell, tag = ctx.cells[(sp, lv)], f"{sp}/{lv}"
                if name == "always_on":
                    aa, ua = E.tables(ctx.splits[sp], lv, "correct")[4:6]
                    res.setdefault(tag, {})[name] = dict(mean_acc=round(float(aa.mean()), 4), mean_unsafe=round(float(ua.mean()), 4), calls_per_decision=3)
                    dec[(tag, name)] = dict(acc=aa, uns=ua)
                    continue
                r = X.evaluate(cell, runs[sp])
                d = M.summarize(r)
                acc6, uns6, rate6 = F.at_budget(cell, runs[sp], F.BUD06)
                acc1, uns1, rate1 = F.at_budget(cell, runs[sp], last)
                d["at_budget_0.6"] = dict(acc=round(float(acc6.mean()), 4), unsafe=round(float(uns6.mean()), 4), call_rate=round(rate6, 4))
                d["at_budget_1.0"] = dict(acc=round(float(acc1.mean()), 4), unsafe=round(float(uns1.mean()), 4), call_rate=round(rate1, 4))
                if "vlm" in name:
                    d["cost_offset"] = args.vlm_cost
                dec[(tag, name)] = dict(mean=r.pop("_dec"), acc_all=acc1, uns_all=uns1, rate_all=round(rate1, 4))
                res.setdefault(tag, {})[name] = d
            print(lv, name, {sp: res[f"{sp}/{lv}"][name]["mean_acc"] for sp in args.splits}, flush=True)
    comparisons = {}
    for sp in args.splits:
        for lv in args.levels:
            tag = f"{sp}/{lv}"
            for m1 in args.methods:
                for m2 in args.compare_to:
                    if m1 != m2 and m1 not in HARNESS_METHODS and m2 in args.methods and (tag, m1) in dec and (tag, m2) in dec:
                        d = dec[(tag, m1)]["mean"] - dec[(tag, m2)]["mean"]
                        comparisons.setdefault(tag, {})[f"{m1}_minus_{m2}"] = dict(mean_diff=round(float(d.mean()), 4), ci95=F.ci(d, ctx.cells[(sp, lv)].seeds))
    hyp = hypotheses(F, ctx, dec, args.levels, args.splits, set(args.methods))
    out = dict(n_train=len(ctx.train), n_test={k: len(v) for k, v in ctx.splits.items()}, test_dir=args.test_dir, methods=args.methods,
               voi_files=voi_files, voi_configs={n: _config(voi_files[n]) for n in voi_files}, lam=args.lam, results=res,
               comparisons=comparisons, hypotheses=hyp)
    path = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    for sp, h in hyp.items():
        print(sp, {k: v["status"] for k, v in h.items()}, flush=True)
    print("wrote", path)


def _config(path):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with open(p) as f:
        first = json.loads(f.readline())
    return first.get("config")


def report(path, md):
    r = json.load(open(path))
    lines = [f"# VoI selector results: `{os.path.relpath(path, ROOT)}`", "",
             "Generated by `scripts/eval_voi.py --report`. Mean accuracy is averaged over budgets 0 to 1 call per decision.", ""]
    for tag, per in r["results"].items():
        lines += [f"## {tag}", "", "| Method | Mean acc | Mean unsafe | Acc @0.6 | Unsafe @0.6 | Calls @1.0 (cap) | Acc @1.0 |", "|---|---|---|---|---|---|---|"]
        for m, d in per.items():
            if m == "always_on":
                lines.append(f"| always_on | {d['mean_acc']:.4f} | {d['mean_unsafe']:.4f} | | | 3 | {d['mean_acc']:.4f} |")
            else:
                a6, a1 = d["at_budget_0.6"], d["at_budget_1.0"]
                lines.append(f"| {m} | {d['mean_acc']:.4f} | {d['mean_unsafe']:.4f} | {a6['acc']:.4f} | {a6['unsafe']:.4f} | {a1['call_rate']:.3f} | {a1['acc']:.4f} |")
        comp = r["comparisons"].get(tag, {})
        if comp:
            lines += ["", "| Comparison | Mean diff | 95% CI (seed bootstrap) |", "|---|---|---|"]
            lines += [f"| {k} | {v['mean_diff']:+.4f} | [{v['ci95'][0]:+.4f}, {v['ci95'][1]:+.4f}] |" for k, v in comp.items()]
        lines.append("")
    lines += ["## Hypotheses (PREREG3 rules; confirmatory only on the final split)", ""]
    for sp, h in r["hypotheses"].items():
        for k, v in h.items():
            lines.append(f"- **{sp} {k}**: {v['status']}. {v['rule']}")
    os.makedirs(os.path.dirname(os.path.abspath(md)), exist_ok=True)
    open(md, "w").write("\n".join(lines) + "\n")
    print("wrote", md)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report", default=None, help="write a markdown table from this eval JSON instead of evaluating")
    p.add_argument("--md", default=None)
    p.add_argument("--voi", nargs="*", default=[], help="NAME=FILE from voi_scores.py")
    p.add_argument("--methods", nargs="+", default=["voi", "voi_budget", "signed", "uncertainty_margin", "always_on"])
    p.add_argument("--train-dirs", nargs="+", default=["v2_dataset", "v2_extra_ds", "v3_extra_ds"])
    p.add_argument("--train-expgain", nargs="+", default=["v2_expgain.jsonl", "v2_extra_expgain.jsonl", "v3_extra_expgain.jsonl"])
    p.add_argument("--test-dir", default="v2_dataset")
    p.add_argument("--test-expgain", nargs="+", default=[])
    p.add_argument("--splits", nargs="+", default=["val"])
    p.add_argument("--levels", nargs="+", default=list(LEVELS))
    p.add_argument("--compare-to", nargs="+", default=["signed", "uncertainty_margin"], help="paired comparisons of every VoI method against these")
    p.add_argument("--print-ablation-commands", nargs=3, metavar=("SWEEP", "MANIFEST", "SPLIT"), default=None)
    p.add_argument("--lam", type=float, default=0.0)
    p.add_argument("--vlm-cost", type=float, default=1.0)
    p.add_argument("--out", default="out/voi_eval/val.json")
    args = p.parse_args()
    if args.print_ablation_commands:
        print("\n".join(ablation_commands(*args.print_ablation_commands)))
    elif args.report:
        report(args.report, args.md or args.report.replace(".json", ".md"))
    else:
        run(args)


if __name__ == "__main__":
    main()
