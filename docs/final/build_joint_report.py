"""Build the joint final report (docs/final/report/report.md, report.html, report.pdf).

Max's published report (research/2026-11-19_learned_selector/deliverables/report/report.md) is the base and every
paragraph of it is kept word for word: his result files exist only on his machine, so his numbers cannot be rebuilt
here, and his text is his. This script only adds to it:

- a joint title and byline, one abstract paragraph and one contributions paragraph for Contribution 2;
- one related-work paragraph, and Section 7 (Contribution 2), generated from out/voi_eval, out/vlm_yesno and
  out/vlm_probe JSON so that no number is typed by hand;
- Contribution 2 limits and next steps after Max's lists (his lists are unchanged), Appendix B (reproducing
  Contribution 2) and Appendix C (who did what).

His Limitations and Next steps become Sections 8 and 9. The HTML uses Max's own markdown renderer from his build.py.
Run from the repository root:  .venv/bin/python docs/final/build_joint_report.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAXR = os.path.join(ROOT, "research/2026-11-19_learned_selector/deliverables/report")
MAXFIG = os.path.join(ROOT, "research/2026-11-19_learned_selector/deliverables/figures")
FIG = os.path.join(ROOT, "docs/final/figures")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import make_voi_page as M  # noqa: E402  (table helpers shared with docs/voi_selector.md)

LV = ("low", "mid", "high")
TITLE = "# Which perception tool should a driving planner call? A learned selector and a counterfactual value-of-information selector"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


def _opt(p):
    q = os.path.join(ROOT, p)
    return json.load(open(q)) if os.path.exists(q) else None


def _one(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f"Max's report changed; expected one match of: {old[:60]!r}")
    return text.replace(old, new)


def section7(F, V, A, D, Y, VV, P, P16, PR, PF, V4, fig):
    """Contribution 2 as markdown. fig(name) gives the image path relative to the report."""
    H = F["hypotheses"]["final"]
    d = D["levels"]
    pr = PR["priors"]
    ew = M.effective_weights(pr)
    n = F["n_test"]["final"]
    R = lambda lv, m: F["results"][f"final/{lv}"][m]
    pct = lambda x: f"{100 * x:.1f}%"
    cells = lambda h, k="mean_diff", c="ci95": " | ".join(
        f"{H[h]['cells'][lv][k]:+.3f} [{H[h]['cells'][lv][c][0]:+.3f}, {H[h]['cells'][lv][c][1]:+.3f}]" for lv in LV)
    sp = [x for lv in LV for x in d[lv]["spearman_per_tool"]]
    v1 = [-H["V1"]["cells"][lv]["mean_diff"] for lv in LV]
    rep = P["replies"]
    probe = P["variants"]["occluded_pedestrian/100_2.0"]
    yq = Y["questions"]
    md = ["## 7 Contribution 2: counterfactual value-of-information selector", "",
          "*Eshan Chawla. Code: `cassvla/planning/hypotheses.py`, `cassvla/planning/voi.py`, `scripts/voi_*.py`, `scripts/eval_voi.py`; "
          "research notes: `research/2026-11-20_voi_selector/`; full results page: `docs/voi_selector.md`.*", "",
          "Contribution 1 learns which tool to call from oracle outcomes. Contribution 2 asks whether the same choice can be reasoned "
          "out instead, with no trained model: imagine what the hidden state of the scene could be, simulate what each tool would "
          "report in each case, and call the tool whose answer is expected to change the planner's choice for the better. This is "
          "the plug-in value-of-information idea of Best-of-Evidence and of the off-road map-layer paper (2611.06702), applied to "
          "the planner's own candidates and scored on the same budget curve as the learned selector.", "",
          "### 7.1 Method", "",
          "For one decision the selector builds weighted worlds from the base observation only. Every world is a measurement-noise "
          "draw of the visible actors (8 draws, using the base camera's noise model). Some worlds add one hidden event on top: a "
          "stopped vehicle or a pedestrian at an occluded point on a candidate path, an unread traffic light set to red or green, or "
          "a fast car behind. For each world and each tool, the tool is simulated on a pseudo-record in which that world is the "
          "truth, the ranker reranks the candidates on the merged belief, and the tool's value is the expected gain in the ranker's "
          "own utility (its score, minus 200 when the candidate is unsafe) over not calling it. The selector calls the tool with "
          "the largest value, and only if that value is above 0 (λ = 0). It reads no hidden actor, oracle label, `c*` or true "
          "light state; a test enforces this.", "",
          f"The class priors are event rates counted on the {PR['n_train_decisions']:,} training decisions: occluded vehicle "
          f"{pr['occl_static']}, occluded pedestrian {pr['occl_ped']}, unread light not green {pr['light']}, car behind {pr['rear']}. "
          "They enter as weights relative to the no-event component (1.0), so the share of world weight each event receives is "
          f"smaller: occluded road user {ew['occluded_road_user']:.3f}, red light {ew['red_light']:.3f}, car behind "
          f"{ew['car_behind']:.3f}. A variant with uniform priors uses no training data at all.", "",
          "### 7.2 Protocol", "",
          "Max's `out/` bundle was not available on the second machine (an Apple Silicon Mac), so the data were regenerated there "
          "from the same code. The split sizes match his exactly (10,329 / 2,222 / 2,235 decisions, 14,707 extra training rows), "
          "but the learned selector reads 0.010 to 0.016 lower on the regenerated data than in Max's build; the likely cause is a "
          "code change committed together with his results, and it is not resolved (`research/2026-11-20_voi_selector/DATA.md`). "
          "All Contribution 2 comparisons therefore use the regenerated data and the same code for every method, and the learned "
          "selector is retrained on them with Max's harness (`run2/experiments/final.py`).", "",
          "The design (world model, priors, number of draws, noise-aware tools, λ) was frozen on the validation split "
          "(`FROZEN.json`). One change was made there before freezing and is disclosed: the first design treated the noise-free "
          "estimate as a world of its own, scored below the ranker margin on validation, and was replaced by the compositional "
          f"world model above (it is kept as an ablation). `PREREG3.md` was committed before seeds 1160 to 1259 were generated: a "
          f"third fresh test set of {n:,} decisions, evaluated once. Its hypotheses:", "",
          "- **V1 (primary):** VoI is non-inferior to the learned selector on mean accuracy over budgets 0 to 1 (95% CI lower bound "
          "above −0.01 at every noise level).",
          "- **V2:** VoI beats the ranker margin at every level (CI above 0).",
          "- **V3:** at its own call rate (no budget cap), VoI is non-inferior to always-on in accuracy (lower bound > −0.01) and no "
          "less safe (unsafe-rate upper bound < +0.01), at every level.",
          "- **V4 (secondary):** VoI with the VLM's hidden-road-user probability as its occlusion prior beats VoI (CI above 0); run "
          "only if every final decision has a VLM answer.", "",
          "Intervals are paired seed bootstraps (1,000 resamples), as in Contribution 1. No multiple-comparison correction.", "",
          "### 7.3 Results (pre-registered final test, seeds 1160-1259)", "",
          f"All three tested hypotheses fail. VoI is {min(v1):.3f} to {max(v1):.3f} below the learned selector and level with the "
          "ranker margin. V4 was not run, because the VLM answers for these frames were not ready when the final evaluation ran "
          "(`V4_STATUS.md`).", "",
          "| Mean accuracy over budgets 0-1 | Low | Mid | High |", "|---|---|---|---|"]
    md += [f"| {M.NAMES[m]} | {M._row(F, 'final', m)} |" for m in ("signed", "voi", "voi_budget", "uncertainty_margin", "always_on")]
    md += ["", "| Mean unsafe rate over budgets 0-1 | Low | Mid | High |", "|---|---|---|---|"]
    md += [f"| {M.NAMES[m]} | {M._row(F, 'final', m, 'mean_unsafe')} |" for m in ("signed", "voi", "uncertainty_margin", "always_on")]
    v3 = H["V3"]["cells"]
    md += ["", "| Hypothesis [95% CI] | Low | Mid | High | Verdict |", "|---|---|---|---|---|",
           f"| V1: VoI − learned selector | {cells('V1')} | {H['V1']['status']} |",
           f"| V2: VoI − ranker margin | {cells('V2')} | {H['V2']['status']} |",
           "| V3: VoI at its call rate − always-on, accuracy | " +
           " | ".join(f"{v3[lv]['acc_diff']:+.3f} [{v3[lv]['acc_ci95'][0]:+.3f}, {v3[lv]['acc_ci95'][1]:+.3f}]" for lv in LV) +
           f" | {H['V3']['status']} |",
           "| V3: same, unsafe rate | " +
           " | ".join(f"{v3[lv]['unsafe_diff']:+.3f} [{v3[lv]['unsafe_ci95'][0]:+.3f}, {v3[lv]['unsafe_ci95'][1]:+.3f}]" for lv in LV) +
           " | |",
           f"| V4: VoI + VLM prior − VoI | not run | not run | not run | {H['V4']['status']} |", "",
           "VoI's call rate at budget 1 is " + ", ".join(f"{R(lv, 'voi')['at_budget_1.0']['call_rate']:.2f}" for lv in LV) +
           " (low, mid, high). VoI beats the ranker margin only when calls are scarce:", "",
           "| Accuracy at a fixed budget | Low | Mid | High |", "|---|---|---|---|"]
    for b in (0.1, 0.3, 1.0):
        md += [f"| VoI at {b} calls/decision | {M._at(F, 'final', 'voi', b)} |",
               f"| Ranker margin at {b} calls/decision | {M._at(F, 'final', 'uncertainty_margin', b)} |"]
    md += ["", f"![Accuracy against calls per decision, final test of Contribution 2 (seeds 1160-1259). Always-on is the dotted line.]({fig('voi_pareto_acc.png')})", "",
           "*Accuracy against calls per decision, final test of Contribution 2 (seeds 1160-1259). Always-on is the dotted line.*", "",
           "On validation and test seeds (100-399) the ordering is the same, including for the uniform-prior variant:", "",
           "| Mean accuracy | Val low | Val mid | Val high | Test low | Test mid | Test high |", "|---|---|---|---|---|---|---|"]
    md += [f"| {M.NAMES[m]} | {M._row(V, 'val', m)} | {M._row(V, 'test', m)} |" for m in ("signed", "voi", "voi_uniform", "uncertainty_margin", "always_on")]
    md += ["", "### 7.4 Ablations (validation, exploratory)", "",
           "| Variant − reference (uniform priors), mean accuracy [95% CI] | Low | Mid | High |", "|---|---|---|---|"]
    md += [f"| {k.replace('_minus_abl_reference', '').replace('abl_', '').replace('_', ' ')} | {M._cmp(A, 'val', k)} |"
           for k in A["comparisons"]["val/mid"]]
    md += ["", "Fitted priors help most and were frozen. Removing the light hypotheses or the measurement-noise draws hurts. The car "
           "behind never occurs in the data, and removing it helps. The first design (`alternatives uniform`) is no better than the "
           "reference.", "",
           "### 7.5 Why it falls short", "",
           f"- **The ranker is a poor world model.** The label is agreement with the oracle's best candidate, which re-simulates the "
           f"true actors; the base ranker agrees with it on {pct(d['mid']['base_correct_rate'])} of validation decisions. VoI measures "
           "gain in the ranker's own utility, so its world model inherits this mismatch. The learned selector is trained on oracle "
           "outcomes and absorbs it.",
           f"- **Its scores track the true gain weakly.** Per-tool Spearman correlation with the expected-gain label is {min(sp):.2f} "
           f"to {max(sp):.2f}. Its best score separates decisions where some tool helps with AUROC "
           f"{d['low']['auroc_maxvoi_any_gain']:.2f} / {d['mid']['auroc_maxvoi_any_gain']:.2f} / {d['high']['auroc_maxvoi_any_gain']:.2f}, "
           f"against {d['low']['auroc_neg_margin_any_gain']:.2f} / {d['mid']['auroc_neg_margin_any_gain']:.2f} / "
           f"{d['high']['auroc_neg_margin_any_gain']:.2f} for the ranker margin.",
           f"- **It picks the wrong tool more often.** When some tool helps, it picks the best one on "
           f"{pct(d['mid']['tool_optimal_when_gain'])} of validation decisions at mid noise, against "
           f"{pct(V['results']['val/mid']['signed']['tool_optimal'])} for the learned selector.",
           "- **Its calls hurt more often.** On the final test at 0.3 calls per decision, " +
           ", ".join(f"{pct(R(lv, 'voi')['harm']['0.3'])}" for lv in LV) + " of its calls have negative expected gain (low, mid, "
           "high), against " + ", ".join(f"{pct(R(lv, 'signed')['harm']['0.3'])}" for lv in LV) + " for the learned selector.",
           "- **The priors are diluted.** As relative world weights, a red light gets about a third of its fitted rate (Section 7.1).", "",
           "### 7.6 On-device VLM study", "",
           "Qwen2.5-VL-3B-Instruct (4-bit, mlx) runs on the Mac. Asked to choose the tool from one front-camera frame, as a prompted "
           f"selector, it carries no information: {rep['n']:,} frames give {rep['distinct_replies']} distinct replies, all of which "
           f"answer `none` or copy the answer template, and all {P['light']['no_light_families']['n']} frames without a traffic light "
           "were answered \"green\", the first listed option. On the same frame it describes a pedestrian and then denies it "
           "(`docs/vlm_failure_analysis.md`):", "",
           "| Prompt, `occluded_pedestrian/100_2.0` | Reply (start) |", "|---|---|",
           f"| List every vehicle and pedestrian | {re.sub(chr(10) + '+', ' ', probe['describe']).split('. ')[0].strip()} |",
           f"| Is there a pedestrian? | {probe['ped'].strip()} |",
           f"| Original JSON prompt | `{probe['orig']}` |", "",
           f"The float16 vision tower overflowed to NaN on {P16['nan_embeddings']['n']} intersection frames, which produced `!!!!` "
           f"replies; running it in float32 removed them ({P['nan_embeddings']['n']}). Narrow yes/no questions scored by P(Yes) "
           "against P(No) in the first answer token avoid the template problem:", "",
           "| Question vs truth (validation) | AUROC [95% CI] | Positives | Within-family AUROC |", "|---|---|---|---|"]
    fam = lambda v: ", ".join(f"{f} {a:.2f}" for f, a in v["by_family"].items() if a is not None) or "one class per family"
    md += [f"| {q} | {v['auroc']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['positives']} of {Y['n']:,} | {fam(v)} |"
           for q, v in yq.items() if v["auroc"] is not None and v["positives"] >= 30]
    md += ["", "Only the red-light question holds within its family. The pedestrian score tracks the scenario family, and the "
           "hidden-road-user question, the one VoI needs, is close to chance. Used as VoI's occlusion prior on validation it "
           "changes mean accuracy by " + ", ".join(f"{VV['comparisons'][f'val/{lv}']['voi_vlm_minus_voi']['mean_diff']:+.3f}" for lv in LV) +
           " (low, mid, high)."]
    if V4:
        md += ["", "**V4 addendum (exploratory, run after the final evaluation).** On seeds 1160-1259, VoI with the VLM prior minus "
               "VoI: " + " | ".join(f"{lv} {V4['comparisons'][f'final/{lv}']['voi_vlm_minus_voi']['mean_diff']:+.3f} "
                                     f"[{V4['comparisons'][f'final/{lv}']['voi_vlm_minus_voi']['ci95'][0]:+.3f}, "
                                     f"{V4['comparisons'][f'final/{lv}']['voi_vlm_minus_voi']['ci95'][1]:+.3f}]" for lv in LV) +
               " (`out/voi_eval/final_v4_addendum.json`). It is not a confirmatory test."]
    lat = D["latency_s"]
    md += ["", "### 7.7 Cost on the Mac", "", "| Step | Seconds |", "|---|---|"] + [f"| {k} | {v:.3g} |" for k, v in lat.items()]
    md += ["", f"Peak memory of the VLM was {PF['peak_memory_gb']:.1f} GB. VoI needs no training but makes about 100 ranker calls per "
           "decision and noise level; the learned selector is one small forward pass.", "",
           "### 7.8 What Contribution 2 shows", "",
           "A training-free value-of-information selector is only as good as the model it reasons with. Built on a rule-based ranker "
           "that agrees with the oracle on about a quarter of decisions, it ties a generic uncertainty trigger and falls well short "
           "of a selector trained on oracle outcomes, which is the strongest evidence in this project that the value of an extra "
           "perception call has to be learned from outcomes here. A small on-device VLM helps with narrow perception questions such "
           "as the light state, not with choosing the tool.", ""]
    return "\n".join(md)


def joint_markdown(fig, maxfig):
    md = open(os.path.join(MAXR, "report.md")).read()
    md = md.replace("](../figures/", f"]({maxfig}/")  # Max's figures, before Contribution 2 adds its own
    F, V = load("out/voi_eval/final.json"), load("out/voi_eval/valtest.json")
    D, A = load("out/voi_eval/diagnosis.json"), load("out/voi_eval/val_ablations.json")
    Y, VV = load("out/vlm_yesno/eval_val.json"), load("out/voi_eval/val_vlm.json")
    P, P16 = load("out/vlm_probe/report.json"), load("out/vlm_probe/report_fp16.json")
    PR, PF, V4 = load("out/voi/priors_fitted.json"), load("out/vlm_dev_fp32/profile.json"), _opt("out/voi_eval/final_v4_addendum.json")
    H = F["hypotheses"]["final"]
    v1 = [-H["V1"]["cells"][lv]["mean_diff"] for lv in LV]
    first = md.split("\n", 1)[0]
    md = _one(md, first + "\n", TITLE + "\n")
    md = re.sub(r"^\*CMPE 249 project, Fall 2026\..*\*$",
                "*CMPE 249 project, Fall 2026. Max Dokukin and Eshan Chawla. Benchmark and Contribution 1 (learned selector, "
                "Sections 1-6): Max Dokukin. Contribution 2 (counterfactual value-of-information selector and on-device VLM study, "
                "Section 7): Eshan Chawla. Joint report built from Max's report of 2026-11-20 (`docs/final/build_joint_report.py`).*",
                md, count=1, flags=re.M)
    md = _one(md, "\n\nSeveral limits matter.",
              "\n\nA second, training-free selector (Contribution 2) estimates each tool's value of information by simulating what "
              "it would reveal across hypothetical hidden states and rerunning the ranker. Under its own pre-registration, on a third "
              f"set of fresh seeds ({F['n_test']['final']:,} decisions), it fell {min(v1):.3f} to {max(v1):.3f} below the learned "
              "selector and was level with the ranker-margin trigger. The ranker it reasons with agrees with the oracle on only "
              f"{100 * D['levels']['mid']['base_correct_rate']:.0f}% of decisions, which explains most of the gap. A small "
              "on-device VLM could read traffic lights but could not choose the tool.\n\nSeveral limits matter.")
    md = _one(md, "\n\n## 2 Related work",
              "\n\n**Contribution 2 (Eshan Chawla).** Items 1 to 5 are Contribution 1 and the benchmark it runs on. Contribution 2 "
              "adds: (6) a counterfactual value-of-information selector with no trained model, compared with the learned selector "
              "under a third pre-registration on fresh seeds, with ablations and a root-cause diagnosis of why it falls short; and "
              "(7) an on-device study of a 4-bit 3B VLM as tool selector and as yes/no detector, including a float16 overflow fix "
              "(Section 7).\n\n## 2 Related work")
    md = _one(md, "\n\n## 3 Setup",
              "\n\n**Where Contribution 2 fits.** Best-of-Evidence and the off-road paper (2611.06702) estimate the value of a "
              "measurement with a plug-in or rule-based model and no training. Section 7 tests that idea on this benchmark, against "
              "the learned selector, on the same budget curve.\n\n## 3 Setup")
    md = _one(md, "\n## 7 Limitations\n", "\n" + section7(F, V, A, D, Y, VV, P, P16, PR, PF, V4, fig) + "\n## 8 Limitations\n")
    md = _one(md, "\n## 8 Next steps\n",
              "\n**Limits specific to Contribution 2.**\n\n"
              "- **Two data builds.** Contribution 2 regenerated the data on a second machine; the learned selector reads 0.010 to "
              "0.016 lower there, for a reason not yet confirmed. Each contribution is internally consistent, but their headline "
              "numbers come from different builds and different fresh seeds.\n"
              "- **The world model was changed once on validation** before freezing, and V4 was not run on the final seeds.\n"
              "- **The yes/no truth for occlusion** comes from the records, and the pedestrian question cannot be separated from the "
              "scenario family.\n"
              "- **Both selectors share `tools.merge`,** which keys actors by name, so repeated names (the three cones of "
              "`lane_blockage`) collapse into one actor in labels and in VoI alike.\n\n## 9 Next steps\n")
    md = _one(md, "\n## Appendix A Reproducibility\n",
              "\n**Next steps added by Contribution 2.** Item 5's plug-in value-of-information selector is now done (Section 7) and "
              "falls short. The scene-only gate and the counterfactual-rollout selector are still missing. The next VoI steps are to "
              "give it a better world model (for example the learned gain as its utility), to use its score as an input feature of "
              "the learned selector, and to run the V4 addendum and the VLM controls on fresh seeds.\n\n## Appendix A Reproducibility\n")
    md += ("\n## Appendix B Reproducing Contribution 2\n\nRun from the repository root on the Mac (`.venv/bin/python`, 8 processes). "
           "Data: `research/2026-11-20_voi_selector/DATA.md`. Final seeds:\n\n```bash\n"
           "OMP_NUM_THREADS=1 .venv/bin/python scripts/run_sweep.py --out out/v5_sweep --start-seed 1160 --seeds 100 --chunk 5 --procs 8\n"
           ".venv/bin/python scripts/build_dataset.py --sweep out/v5_sweep --out out/v5_final_ds --as-split final --procs 8\n"
           ".venv/bin/python scripts/label_expected_gain.py --sweep out/v5_sweep --out out/v5_final_expgain.jsonl --draws 8 --procs 8\n"
           "OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep out/v5_sweep --out out/voi/v5_final.jsonl --priors out/voi/priors_fitted.json --procs 8\n"
           ".venv/bin/python scripts/eval_voi.py --voi voi=out/voi/v5_final.jsonl --methods voi voi_budget signed uncertainty_margin always_on \\\n"
           "  --test-dir v5_final_ds --test-expgain v5_final_expgain.jsonl --splits final --out out/voi_eval/final.json\n```\n\n"
           "VLM: `scripts/cache_vlm.py --mode yesno`, `scripts/eval_vlm_yesno.py`, `scripts/vlm_probe.py` "
           "(`docs/vlm_failure_analysis.md`). Figures: `scripts/voi_figures.py`. This report: `.venv/bin/python "
           "docs/final/build_joint_report.py`; the deck: `docs/final/build_joint_deck.py`.\n\n"
           "## Appendix C Who did what\n\n"
           "| Part | Owner |\n|---|---|\n"
           "| Scenario suite, candidate generator, oracle, simulated tools, expected-gain labels | Max Dokukin |\n"
           "| Contribution 1: learned selector, two pre-registered finals, exploratory analyses, Qwen3.5-9B features (A100) | Max Dokukin |\n"
           "| Contribution 2: VoI selector, data rebuild on the Mac, third pre-registered final, ablations, diagnosis | Eshan Chawla |\n"
           "| On-device VLM study (Qwen2.5-VL-3B, mlx): rendering, failure analysis, float16 fix, yes/no detectors | Eshan Chawla |\n"
           "| Report Sections 1-6, 8-9 and Appendix A; deck slides on Contribution 1 | Max Dokukin |\n"
           "| Report Section 7 and Appendices B-C; deck slides on Contribution 2 and the conclusion | Eshan Chawla |\n")
    return md


def max_renderer(here):
    """Max's markdown-to-HTML renderer and CSS from his build.py, resolving images relative to `here`."""
    import base64
    import html
    ns = {"os": os, "re": re, "html": html, "base64": base64, "HERE": here}
    src = open(os.path.join(MAXR, "build.py")).read()
    code = src[src.index("# ---------- minimal markdown to html"):src.index("def build():")]
    exec(compile(code, os.path.join(MAXR, "build.py"), "exec"), ns)
    return ns


def build(out_dir=os.path.join(ROOT, "docs/final/report"), pdf=False):
    os.makedirs(out_dir, exist_ok=True)
    rel = lambda p: os.path.relpath(p, out_dir)
    md = joint_markdown(lambda name: rel(os.path.join(FIG, name)), rel(MAXFIG))
    path = os.path.join(out_dir, "report.md")
    open(path, "w").write(md)
    K = max_renderer(out_dir)
    import html
    title = re.search(r"^# (.+)$", md, re.M).group(1)
    doc = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
           f'initial-scale=1"><title>{html.escape(title)}</title><style>{K["font_css"]()}{K["CSS"]}</style></head><body>\n'
           f'{K["md_to_html"](md, embed=True)}\n</body></html>\n').replace("<p>@@PB@@</p>", '<div class="pb"></div>')
    hp = os.path.join(out_dir, "report.html")
    open(hp, "w").write(doc)
    if pdf:
        chrome = shutil.which("chromium") or CHROME
        subprocess.run([chrome, "--headless", "--no-pdf-header-footer", f"--print-to-pdf={os.path.join(out_dir, 'report.pdf')}",
                        "file://" + hp], check=True, capture_output=True)
    print(f"wrote {path} ({len(md.split()):,} words)")
    return path


if __name__ == "__main__":
    build(pdf="--no-pdf" not in sys.argv)
