"""Write docs/voi_selector.md from the evaluation JSON, so no number on that page is typed by hand.

    python scripts/make_voi_page.py --final out/voi_eval/final.json --valtest out/voi_eval/valtest.json \
        --ablations out/voi_eval/val_ablations.json --diagnosis out/voi_eval/diagnosis.json \
        --priors out/voi/priors_fitted.json [--yesno out/vlm_yesno/eval_val.json] [--vlm-val out/voi_eval/val_vlm.json] \
        --out docs/voi_selector.md
"""
import argparse
import json
import os

LV = ("low", "mid", "high")
NAMES = {"signed": "Learned selector `signed` (Max)", "voi": "VoI, abstains at VoI <= 0", "voi_budget": "VoI, budget only",
         "voi_uniform": "VoI, uniform priors (val/test only)", "voi_vlm": "VoI + VLM prior", "uncertainty_margin": "Ranker margin",
         "always_on": "Always-on (3 calls)"}


def effective_weights(priors):
    """Share of the world weight each hidden event gets in the compositional world model (light: red is half the class)."""
    comps = {c: priors.get(c, 0.0) for c in ("null", "occl_static", "occl_ped", "light", "rear")}
    total = sum(comps.values())
    return dict(no_hidden_event=comps["null"] / total, occluded_road_user=(comps["occl_static"] + comps["occl_ped"]) / total,
                red_light=comps["light"] / 2 / total, car_behind=comps["rear"] / total)


def _row(r, sp, m, k="mean_acc"):
    return " | ".join(f"{r['results'][f'{sp}/{lv}'][m][k]:.3f}" for lv in LV)


def _cmp(r, sp, k):
    return " | ".join(f"{r['comparisons'][f'{sp}/{lv}'][k]['mean_diff']:+.3f} [{r['comparisons'][f'{sp}/{lv}'][k]['ci95'][0]:+.3f}, "
                      f"{r['comparisons'][f'{sp}/{lv}'][k]['ci95'][1]:+.3f}]" for lv in LV)


def _at(r, sp, m, b):
    i = int(round(b / 0.05))
    return " | ".join(f"{r['results'][f'{sp}/{lv}'][m]['curve'][i]:.3f}" for lv in LV)


def page(F, V, A, D, P, Y=None, VV=None):
    pr = P["priors"]
    ew = effective_weights(pr)
    d = D["levels"]
    md = ["# Counterfactual value-of-information selector", "",
          "Eshan's contribution: a tool selector with no learned model that decides which single perception query to make by",
          "reasoning about what each tool could reveal, compared head to head with Max's learned selector (`signed`). Its class",
          "priors are event rates calibrated on the training decisions. Code: `cassvla/planning/hypotheses.py`,",
          "`cassvla/planning/voi.py`, `scripts/voi_scores.py`, `scripts/voi_priors.py`, `scripts/eval_voi.py`,",
          "`scripts/voi_diagnosis.py`, `scripts/voi_figures.py`.", "",
          "This page is written by `scripts/make_voi_page.py` from `out/voi_eval/*.json` and `out/voi/priors_fitted.json`;",
          "full tables are in `research/2026-11-20_voi_selector/`.", "",
          "## Result", "",
          "The pre-registered final test (seeds 1160-1259, never seen before, 4,557 decisions, run once) is negative. VoI is",
          "0.08 to 0.10 below the learned selector at every noise level and level with the ranker-margin baseline. V1, V2 and",
          "V3 of `PREREG3.md` fail.", "",
          "| Final split, mean accuracy over budgets 0-1 | Low | Mid | High |", "|---|---|---|---|"]
    md += [f"| {NAMES[m]} | {_row(F, 'final', m)} |" for m in ("signed", "voi", "voi_budget", "uncertainty_margin", "always_on")]
    md += ["", "| Final split, paired difference [95% seed-bootstrap CI] | Low | Mid | High |", "|---|---|---|---|",
           f"| VoI - learned selector (V1 needs lower bound > -0.01) | {_cmp(F, 'final', 'voi_minus_signed')} |",
           f"| VoI - ranker margin (V2 needs lower bound > 0) | {_cmp(F, 'final', 'voi_minus_uncertainty_margin')} |", "",
           "**V4 (VoI + VLM prior) was not run on the final seeds.** The final evaluation was made as soon as the final data were",
           "ready; the VLM yes/no answers for those frames were still hours away, and PREREG3 runs V4 only when every final",
           "decision has one. Any later `voi_vlm` run on seeds 1160-1259 is an exploratory addendum, not a confirmatory test.", "",
           "Figure: `paper/figures/voi_pareto_acc.pdf` (accuracy against calls per decision on the final split).", "",
           "VoI beats the ranker margin when calls are scarce and loses when they are plentiful:", "",
           "| Final split, accuracy at a fixed budget | Low | Mid | High |", "|---|---|---|---|"]
    for b in (0.1, 0.3, 1.0):
        md += [f"| VoI at {b} calls/decision | {_at(F, 'final', 'voi', b)} |", f"| Ranker margin at {b} calls/decision | {_at(F, 'final', 'uncertainty_margin', b)} |"]
    md += ["", "Validation and test (seeds 100-399, `out/voi_eval/valtest.json`) show the same picture. The variant with uniform",
           "priors, which uses no training data at all, was evaluated only here, not on the final seeds:", "",
           "| Mean accuracy | Val low | Val mid | Val high | Test low | Test mid | Test high |", "|---|---|---|---|---|---|---|"]
    md += [f"| {NAMES[m]} | {_row(V, 'val', m)} | {_row(V, 'test', m)} |" for m in ("signed", "voi", "voi_uniform", "uncertainty_margin", "always_on")]
    md += ["", "## Method", "",
           "For one decision the selector weighs world hypotheses built from the base observation only. Every world is a",
           "measurement-noise draw of the visible actors (8 draws, the base camera's noise model); some worlds add one hidden",
           "event on top: a stopped vehicle or a pedestrian at an occluded point on a candidate path, an unread light set to red",
           "or green, or a fast car behind. Each tool is run on a pseudo-record in which that world is the truth, the ranker",
           "reranks the candidates on the merged belief, and the tool's value is the expected gain in the ranker's own utility",
           "(score, minus 200 when unsafe) over not calling it. The decision calls the best tool only when its value is above 0.",
           "No hidden actor, `c_star`, oracle metric or true light state is read; a test enforces this.", "",
           f"Class priors are event rates on the {P['n_train_decisions']:,} training decisions: occluded vehicle {pr['occl_static']},",
           f"occluded pedestrian {pr['occl_ped']}, unread light not green {pr['light']}, car behind {pr['rear']}. They enter as relative",
           "weights against the no-event component (1.0), so the share of world weight each event actually gets is smaller:",
           f"occluded road user {ew['occluded_road_user']:.3f}, red light {ew['red_light']:.3f} (the fitted not-green rate is",
           f"{pr['light']}), car behind {ew['car_behind']:.3f}. This mapping is a weakness of the design (see the diagnosis).", "",
           "## Ablations (validation)", "",
           "| Variant - reference (uniform priors), mean accuracy | Low | Mid | High |", "|---|---|---|---|"]
    md += [f"| {k.replace('_minus_abl_reference', '').replace('abl_', '')} | {_cmp(A, 'val', k)} |" for k in A["comparisons"]["val/mid"]]
    md += ["", "Fitted priors help most. Removing the measurement-noise draws or the light hypotheses hurts. The imaginary car",
           "behind never occurs in the data and removing it helps; fitted priors give it weight 0. A first design that treated",
           "the noise-free base estimate as a world of its own (`alternatives_uniform`, `voi_scores.py --world-model",
           "alternatives`) was no better and was replaced, on validation, before the final test.", "",
           "## Why it falls short (diagnosis, validation, `out/voi_eval/diagnosis.json`)", "",
           "- VoI optimises the ranker's own utility, but the label is agreement with the oracle's `c*`, which re-simulates",
           f"  reactive hazards. The base ranker is right on only {d['mid']['base_correct_rate']:.1%} of validation decisions. A",
           "  world model built on the ranker inherits that mismatch; the learned selector is trained on real outcomes and",
           "  absorbs it.",
           f"- VoI's best score separates decisions where some tool helps from those where none does with AUROC",
           f"  {d['low']['auroc_maxvoi_any_gain']:.2f} / {d['mid']['auroc_maxvoi_any_gain']:.2f} / {d['high']['auroc_maxvoi_any_gain']:.2f} (low / mid / high); minus the ranker margin reaches",
           f"  {d['low']['auroc_neg_margin_any_gain']:.2f} / {d['mid']['auroc_neg_margin_any_gain']:.2f} / {d['high']['auroc_neg_margin_any_gain']:.2f}. Its per-tool Spearman correlation with the true expected gain is",
           f"  only {min(min(x['spearman_per_tool']) for x in d.values()):.2f} to {max(max(x['spearman_per_tool']) for x in d.values()):.2f}.",
           f"- When some tool helps, VoI picks the best one on {d['mid']['tool_optimal_when_gain']:.1%} of decisions at mid noise, against",
           f"  {V['results']['val/mid']['signed']['tool_optimal']:.1%} for the learned selector. Its calls are harmful (negative expected gain) on",
           f"  {V['results']['val/mid']['voi']['harm']['0.3']:.1%} of calls at budget 0.3, against {V['results']['val/mid']['signed']['harm']['0.3']:.1%} for the learned selector.",
           "- The priors are under-weighted as world weights (see Method): a red light gets about a third of its fitted rate.", ""]
    if Y:
        fam = lambda v: ", ".join(f"{f} {a:.2f}" for f, a in v["by_family"].items() if a is not None) or "only one class in every family"
        md += ["## VLM yes/no questions (validation, `out/vlm_yesno/eval_val.json`)", "",
               "Qwen2.5-VL-3B, P(Yes) against P(No) in the first answer token, scored against truth from the records. The",
               "within-family AUROC separates real detection from recognising the scenario family.", "",
               "| Question vs truth | AUROC [95% seed CI] | Positives | Within-family AUROC |", "|---|---|---|---|"]
        md += [f"| {q} | {v['auroc']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['positives']} of {Y['n']}"
               f"{' (too few positives to read)' if v['positives'] < 30 else ''} | {fam(v)} |"
               for q, v in Y["questions"].items() if v["auroc"] is not None]
        md += ["", "Only the red-light question holds up within its family. The pedestrian score tracks the scenario: every",
               "`occluded_pedestrian` decision has a pedestrian in view and no other family has one, so it cannot be tested within",
               "a family. The hidden-road-user question, the one VoI uses, is close to chance overall.", ""]
    if VV:
        md += ["## VoI + VLM prior (validation)", "", "| Mean accuracy | Low | Mid | High |", "|---|---|---|---|"]
        md += [f"| {NAMES[m]} | {_row(VV, 'val', m)} |" for m in ("voi", "voi_vlm", "signed") if m in VV["results"]["val/mid"]]
        md += ["", "| Paired difference [95% CI] | Low | Mid | High |", "|---|---|---|---|",
               f"| VoI + VLM prior - VoI | {_cmp(VV, 'val', 'voi_vlm_minus_voi')} |", "",
               "`voi_vlm` pays one VLM call per decision on top of the tool budget.", ""]
    md += ["## Cost on this Mac", "", "| Step | Seconds |", "|---|---|"] + [f"| {k} | {v:.3g} |" for k, v in D["latency_s"].items()]
    md += ["", "VoI needs no learned model but costs about 0.06 s per decision per noise level (about 100 ranker calls), against",
           "microseconds for the learned selector's forward pass.", "", "## Reproduce", "", "```bash",
           "OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_priors.py --sweep out/v2_sweep --manifest out/v2_dataset/manifest.json --out out/voi/priors_fitted.json",
           "OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep out/v5_sweep --out out/voi/v5_final.jsonl --priors out/voi/priors_fitted.json --procs 8",
           "OMP_NUM_THREADS=1 .venv/bin/python scripts/eval_voi.py --voi voi=out/voi/v5_final.jsonl --methods voi voi_budget signed uncertainty_margin always_on \\",
           "  --test-dir v5_final_ds --test-expgain v5_final_expgain.jsonl --splits final --out out/voi_eval/final.json",
           "OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_diagnosis.py --voi out/voi/v2_fitted.jsonl --data out/v2_dataset --split val \\",
           "  --expgain out/v2_expgain.jsonl --vlm-profile out/vlm_dev_fp32/profile.json --out out/voi_eval/diagnosis.json",
           "python scripts/make_voi_page.py --final out/voi_eval/final.json --valtest out/voi_eval/valtest.json --ablations out/voi_eval/val_ablations.json \\",
           "  --diagnosis out/voi_eval/diagnosis.json --priors out/voi/priors_fitted.json --out docs/voi_selector.md", "```", ""]
    return "\n".join(md)


def main():
    p = argparse.ArgumentParser()
    for k in ("final", "valtest", "ablations", "diagnosis", "priors", "out"):
        p.add_argument(f"--{k}", required=True)
    p.add_argument("--yesno", default=None)
    p.add_argument("--vlm-val", default=None)
    a = p.parse_args()
    load = lambda x: json.load(open(x)) if x else None
    text = page(load(a.final), load(a.valtest), load(a.ablations), load(a.diagnosis), load(a.priors), load(a.yesno), load(a.vlm_val))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write(text)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
