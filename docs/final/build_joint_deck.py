"""Build the joint final deck (docs/final/deck/joint_deck.pptx and .pdf).

Max's published deck (research/2026-11-19_learned_selector/deliverables/deck/deck.pptx) is the base: every one of his
slides is kept with its text and numbers unchanged, because his result files (out/v4_eval, out/v3_eval) exist only on
his machine. The only edit to his slides is the title-slide subtitle, so that it names both contributions. This script:

- reorders his slides into the agreed sections (intro Max, background Eshan, contribution 1 Max, contribution 2 Eshan,
  limitations Max, conclusion Eshan);
- adds Eshan's contribution-2 slides, the joint conclusion and Eshan's backups. They are drawn with Max's own renderer
  and helpers (his build_pptx.py and common.py are executed, not copied), and every number is read from out/voi_eval,
  out/vlm_yesno and out/vlm_probe JSON;
- names the speaker on every slide in the notes, renumbers the footers, and writes SOURCES.md.

Run from the repository root:  .venv/bin/python docs/final/build_joint_deck.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAXD = os.path.join(ROOT, "research/2026-11-19_learned_selector/deliverables/deck")
FIG = os.path.join(ROOT, "docs/final/figures")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
LV = ("low", "mid", "high")


def _exec_slice(path, ns, start=None, end=None, drop=()):
    src = open(path).read()
    i = src.index(start) if start else 0
    j = src.index(end) if end else len(src)
    code = "\n".join(l for l in src[i:j].split("\n") if not l.startswith(drop))
    exec(compile(code, path, "exec"), ns)


def max_toolkit():
    """Max's slide helpers (common.py) and renderer (build_pptx.py), minus the lines that read his result files."""
    ns = {"__file__": os.path.join(MAXD, "common.py"), "__name__": "max_common"}
    _exec_slice(ns["__file__"], ns, drop=("G = ", "R = ", "H = "))
    _exec_slice(os.path.join(MAXD, "build_pptx.py"), ns, end="mi = bi = 0", drop=("from common import", "import slides"))
    return ns


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


def data():
    d = dict(F=load("out/voi_eval/final.json"), V=load("out/voi_eval/valtest.json"), D=load("out/voi_eval/diagnosis.json"),
             A=load("out/voi_eval/val_ablations.json"), Y=load("out/vlm_yesno/eval_val.json"), VV=load("out/voi_eval/val_vlm.json"),
             P=load("out/vlm_probe/report.json"), P16=load("out/vlm_probe/report_fp16.json"), PR=load("out/voi/priors_fitted.json"),
             PF=load("out/vlm_dev_fp32/profile.json"))
    add = os.path.join(ROOT, "out/voi_eval/final_v4_addendum.json")
    d["V4"] = json.load(open(add)) if os.path.exists(add) else None
    yf = os.path.join(ROOT, "out/vlm_yesno/eval_final.json")
    d["YF"] = json.load(open(yf)) if os.path.exists(yf) else None
    return d


def eshan_slides(K, d):
    """Contribution 2, the joint conclusion and Eshan's backups, as Max-style slide dicts: (key, slide)."""
    T, RECT, TABLE, frame, bullets, stat = K["T"], K["RECT"], K["TABLE"], K["frame"], K["bullets"], K["stat"]
    INK, GREY, TEAL, RUST, PANEL = K["INK"], K["GREY"], K["TEAL"], K["RUST"], K["PANEL"]
    F, V, D, Y, P = d["F"], d["V"], d["D"], d["Y"], d["P"]
    R = lambda lv, m: F["results"][f"final/{lv}"][m]
    H = F["hypotheses"]["final"]
    f3 = lambda x: f"{x:.3f}".replace("-", "−")
    sg = lambda x: f"{x:+.3f}".replace("-", "−")
    ci = lambda c: "[" + ", ".join(f"{v:.3f}".replace("-", "−") for v in c) + "]"
    pct = lambda x: f"{100 * x:.1f}%"
    cell = lambda h, lv: f"{sg(H[h]['cells'][lv]['mean_diff'])} {ci(H[h]['cells'][lv]['ci95'])}"
    n_final = F["n_test"]["final"]
    FJ = "out/voi_eval/final.json"
    out = []

    def img(x, y, w, h, name):
        return dict(k="img", x=x, y=y, w=w, h=h, name=name, path=os.path.join(FIG, name))

    def slide(key, title, eyebrow, els, src, backup=False):
        out.append((key, dict(title=title, eyebrow=eyebrow, els=frame(title, eyebrow) + els, src=src, backup=backup, notes="")))

    # C2.1 method
    flow = []
    boxes = [("What the car sees", "visible actors, occluders and the light as observed; nothing privileged"),
             ("Imagined worlds", "8 noise redraws of what is visible, some with one hidden event on top"),
             ("Simulate each tool", "what ROI, depth and collision would report if that world were true"),
             ("Rerun the ranker", "on the belief after each simulated tool answer"),
             ("Call or abstain", "call the tool with the highest expected gain, only if it is above 0")]
    for i, (a, b) in enumerate(boxes):
        x = 100 + i * 352
        flow += [RECT(x, 250, 310, 300, PANEL if i != 4 else "D9EFEC"),
                 T(x + 22, 270, 266, 70, [a], size=32, bold=True, color=TEAL if i == 4 else INK),
                 T(x + 22, 355, 266, 190, [b], size=28)]
        if i < 4:
            flow.append(T(x + 310, 360, 42, 60, ["→"], size=42, color=GREY, align="c"))
    pr = d["PR"]
    slide("c2_method", "Contribution 2: reason out the tool instead of learning it",
          "Contribution 2 · counterfactual value-of-information (VoI) selector", flow + [
              T(100, 610, 840, 400, [{"t": "No learned model", "bold": True, "color": GREY, "size": 34, "gap": 12},
                                     {"t": "Hidden events: a road user behind an occluder, an unread light, a car behind. Their priors are "
                                           f"event rates counted on the {pr['n_train_decisions']:,} training decisions.", "gap": 12},
                                     {"t": "VoI(tool) = expected gain in the ranker’s own utility from calling it. There are no trained weights."}],
                size=30, fill=PANEL, pad=32),
              T(980, 610, 840, 400, [{"t": "Pre-registered, run once", "bold": True, "color": TEAL, "size": 34, "gap": 12},
                                     {"t": "PREREG3.md was committed before seeds 1160 to 1259 existed: a third fresh test set, "
                                           f"{n_final:,} decisions.", "gap": 12},
                                     {"t": "V1: no worse than the learned selector (margin 0.01). V2: beats the ranker margin. "
                                           "V3: no worse than always-on at its own call rate."}], size=30, fill="D9EFEC", pad=32)],
          "Method: cassvla/planning/voi.py, cassvla/planning/hypotheses.py, docs/voi_selector.md (Method). Priors and "
          "n_train_decisions: out/voi/priors_fitted.json. Hypotheses: research/2026-11-20_voi_selector/PREREG3.md. "
          f"Decisions: {FJ} n_test.final.")

    # C2.2 result
    rows = [["Mean accuracy over budgets 0 to 1", "Low noise", "Mid noise", "High noise"]]
    for name, m in (("Learned selector (signed)", "signed"), ("VoI (Contribution 2)", "voi"), ("Ranker margin", "uncertainty_margin"),
                    ("Always-on (3 calls)", "always_on")):
        rows.append([name] + [f3(R(lv, m)["mean_acc"]) for lv in LV])
    v3 = H["V3"]["cells"]
    hyp = [["Pre-registered test (95% CI)", "Low noise", "Mid noise", "High noise", "Verdict"],
           ["V1: VoI − learned selector"] + [cell("V1", lv) for lv in LV] + [H["V1"]["status"]],
           ["V2: VoI − ranker margin"] + [cell("V2", lv) for lv in LV] + [H["V2"]["status"]],
           ["V3: VoI at its own call rate − always-on"] +
           [f"acc {sg(v3[lv]['acc_diff'])}, unsafe {sg(v3[lv]['unsafe_diff'])}" for lv in LV] + [H["V3"]["status"]]]
    slide("c2_result", "Result: VoI ties the uncertainty trigger and trails the learned selector",
          f"Contribution 2 result · pre-registered final test · seeds 1160 to 1259, {n_final:,} decisions", [
              TABLE(100, 235, 1720, [4.3, 2.2, 2.2, 2.2], rows, size=28, rowh=64, hl=[], bold_rows=[2]),
              TABLE(100, 580, 1720, [4.3, 2.8, 2.8, 2.8, 1.3], hyp, size=26, rowh=72, hl=[4]),
              T(100, 885, 1720, 150, ["All three hypotheses fail; V4 (VLM prior) was not run in this test (a later exploratory run is on the "
                                      "VLM slide). The learned selector here "
                                      "is retrained on Eshan’s rebuild of the data, which reads 0.010 to 0.016 lower than Max’s build "
                                      "(cause not confirmed). All methods are scored on the same rows."], size=26, color=GREY)],
          f"{FJ} results.final/<level>.<method>.mean_acc; hypotheses.final.V1/V2 cells (mean_diff, ci95), V3 cells (acc_diff, "
          "unsafe_diff), status. Rebuild gap: research/2026-11-20_voi_selector/DATA.md. V4: V4_STATUS.md.")

    # C2.3 curve
    cv = lambda lv, m, b: R(lv, m)["curve"][int(round(b / 0.05))]
    slide("c2_curve", "VoI helps only when calls are scarce", "Accuracy against calls per decision · final test, seeds 1160 to 1259", [
        img(100, 230, 1720, 552, "voi_pareto_acc.png"),
        T(100, 800, 1720, 230, bullets([
            "At 0.1 calls per decision VoI beats the ranker margin: " +
            ", ".join(f"{f3(cv(lv, 'voi', 0.1))} vs {f3(cv(lv, 'uncertainty_margin', 0.1))}" for lv in LV) +
            " (low, mid, high). By 0.4 to 0.6 calls they are level.",
            "The learned selector is ahead of VoI at every budget, and only it reaches always-on (dotted line)."], size=30, gap=12))],
        f"Figure: paper/figures/voi_pareto_acc.pdf (scripts/voi_figures.py from {FJ}). Values at 0.1: {FJ} "
        "results.final/<level>.<method>.curve[2] (0.05 grid). 'Level by 0.4 to 0.6': read from the same curves.")

    # C2.4 why
    dl = D["levels"]
    sp = [x for lv in LV for x in dl[lv]["spearman_per_tool"]]
    vh = lambda lv, m: R(lv, m)["harm"]["0.3"]
    slide("c2_why", "Why it falls short: it reasons with the ranker, but the label is the oracle’s",
          "Contribution 2 diagnosis · validation (diagnosis, ablations) and final test (harm)", [
              T(100, 240, 960, 790, bullets([
                  f"**The ranker is a poor world model.** It agrees with the oracle on {pct(dl['mid']['base_correct_rate'])} of decisions. "
                  "VoI measures gain in the ranker’s own utility, so it inherits that mismatch. The learned selector is trained on oracle "
                  "outcomes and absorbs it.",
                  f"**Its scores track the true gain weakly.** Per-tool rank correlation {min(sp):.2f} to {max(sp):.2f}.",
                  f"**It picks the wrong tool more often.** When some tool helps (mid noise): {pct(dl['mid']['tool_optimal_when_gain'])} best "
                  f"tool, against {pct(V['results']['val/mid']['signed']['tool_optimal'])} for the learned selector.",
                  "**Its calls hurt more often.** Harmful calls at 0.3 calls per decision: " +
                  ", ".join(f"{pct(vh(lv, 'voi'))} vs {pct(vh(lv, 'signed'))}" for lv in LV) + " (low, mid, high; learned second)."],
                  size=30, gap=20)),
              img(1100, 240, 720, 478, "voi_ablations.png"),
              T(1100, 730, 720, 300, ["Ablations on validation, change in mean accuracy. Fitted priors help most; removing the light "
                                      "hypotheses or the depth noise draws hurts; the car behind never happens, so removing it helps."],
                size=24, color=GREY)],
          "out/voi_eval/diagnosis.json levels.<level> (base_correct_rate, spearman_per_tool, tool_optimal_when_gain; val split); "
          "out/voi_eval/valtest.json results.val/mid.signed.tool_optimal; " + FJ + " results.final/<level>.{voi,signed}.harm['0.3']. "
          "Figure: paper/figures/voi_ablations.pdf from out/voi_eval/val_ablations.json.")

    # C2.5 VLM
    probe = P["variants"]["occluded_pedestrian/100_2.0"]
    first = lambda s: re.sub(r"\s+", " ", s.strip()).split(". ")[0].strip("`*# ").rstrip(".") + "."
    orig = json.loads(probe["orig"])
    rep = P["replies"]
    yq = Y["questions"]
    red_in = yq["red_light vs red_light"]["by_family"]["ambiguous_light"]
    vv = d["VV"]["comparisons"]
    v4 = d["V4"]
    if v4:
        vlm_prior = ("**No help as VoI’s occlusion prior** (final seeds, exploratory addendum): " +
                     ", ".join(sg(v4["comparisons"][f"final/{lv}"]["voi_vlm_minus_voi"]["mean_diff"]) for lv in LV) + ".")
    else:
        vlm_prior = "**No help as VoI’s occlusion prior** (validation): " + ", ".join(sg(vv[f"val/{lv}"]["voi_vlm_minus_voi"]["mean_diff"]) for lv in LV) + "."
    slide("c2_vlm", "On-device VLM: it sees the pedestrian, then ignores it",
          "Contribution 2 · Qwen2.5-VL-3B, 4-bit, mlx on a MacBook", [
              img(100, 235, 800, 450, "vlm_pedestrian_frame.png"),
              TABLE(100, 700, 800, [2.2, 4], [["Prompt (same frame)", "Reply"],
                                              ["List vehicles and pedestrians", first(probe["describe"])],
                                              ["Is there a pedestrian?", first(probe["ped"])],
                                              ["Choose a tool (JSON)", f"query: {orig['query']}, occlusion: {str(orig['occlusion']).lower()}"]],
                    size=22, rowh=72, hl=[]),
              T(960, 235, 860, 800, bullets([
                  f"**Tool choice carries no information:** {rep['distinct_replies']} distinct replies over {rep['n']:,} frames; every one "
                  "answers “none” or copies the template.",
                  f"**Bug found and fixed:** the float16 vision tower overflowed to NaN on {d['P16']['nan_embeddings']['n']} frames; "
                  f"with float32, {P['nan_embeddings']['n']}.",
                  f"**Narrow yes/no questions work for lights:** red-light AUROC {red_in:.2f} within its family. "
                  f"“Is a road user hidden?” is near chance ({yq['hidden vs hidden']['auroc']:.2f}).",
                  vlm_prior,
                  f"**Cost:** {d['PF']['embed']['mean_s']:.2f} s per embedding, {d['PF']['peak_memory_gb']:.1f} GB peak memory."],
                  size=26, gap=14))],
          "out/vlm_probe/report.json (variants.occluded_pedestrian/100_2.0: describe, ped, orig; replies; nan_embeddings), "
          "report_fp16.json nan_embeddings; out/vlm_yesno/eval_val.json questions (auroc, by_family); "
          + ("out/voi_eval/final_v4_addendum.json comparisons.final/<level>.voi_vlm_minus_voi" if v4 else
             "out/voi_eval/val_vlm.json comparisons.val/<level>.voi_vlm_minus_voi") +
          "; out/vlm_dev_fp32/profile.json. Analysis: docs/vlm_failure_analysis.md. Frame: out/frames_dev/occluded_pedestrian/100_2.0.png.")

    # Conclusion (joint)
    v1 = [-H["V1"]["cells"][lv]["mean_diff"] for lv in LV]
    slide("conclusion", "Conclusion: learn when to look from outcomes", "Conclusion · both contributions", [
        T(100, 240, 840, 420, [{"t": "Contribution 1 · learned selector", "bold": True, "color": TEAL, "size": 34, "gap": 14},
                               {"t": "Learning from oracle outcomes works. A small selector that sees the candidates is within the "
                                     "0.01 accuracy margin of always-on at 0.6 calls per decision (20% of its calls) and safer at all "
                                     "three noise levels (second final test).", "gap": 14},
                               {"t": "Open question: whether it holds closed loop."}], size=30, fill="D9EFEC", pad=32),
        T(980, 240, 840, 420, [{"t": "Contribution 2 · counterfactual VoI", "bold": True, "color": RUST, "size": 34, "gap": 14},
                               {"t": f"Reasoning with the planner’s own model does not, here. VoI trails the learned selector by "
                                     f"{min(v1):.3f} to {max(v1):.3f} and ties the uncertainty trigger, because its ranker agrees with the "
                                     f"oracle on {pct(dl['mid']['base_correct_rate'])} of decisions.", "gap": 14},
                               {"t": "A small on-device VLM answers narrow questions (light state), not tool choice."}], size=30, fill=PANEL, pad=32),
        T(100, 720, 1720, 280, bullets([
            "**Together:** in this benchmark, the value of an extra look was better learned from real outcomes than inferred from the planner’s own beliefs.",
            "**Next:** closed-loop collisions; VoI as an input feature to the learned selector; VLM controls."], size=34, gap=18))],
        "Contribution 1 statements: Max's slides 9 and 17 (out/v4_eval/final_geom.json). Contribution 2: " + FJ +
        " hypotheses.final.V1.cells.<level>.mean_diff, V2; out/voi_eval/diagnosis.json levels.mid.base_correct_rate; "
        "out/vlm_yesno/eval_val.json; out/vlm_probe/report.json.")

    # Backups
    slide("b_unsafe", "Backup: VoI unsafe rate against calls", "Backup · Contribution 2 · final test", [
        img(100, 240, 1720, 552, "voi_pareto_unsafe.png"),
        T(100, 820, 1720, 150, ["Unsafe rate of the chosen candidate (oracle label), lower is better. At its own call rate VoI is less "
                                "safe than always-on at every level (V3)."], size=28)],
        f"Figure: paper/figures/voi_pareto_unsafe.pdf from {FJ} results.final/<level>.<method>.unsafe_curve; V3 cells.", backup=True)
    vt = [["Mean accuracy", "Val low", "Val mid", "Val high", "Test low", "Test mid", "Test high"]]
    for name, m in (("Learned selector (signed)", "signed"), ("VoI", "voi"), ("VoI, uniform priors", "voi_uniform"),
                    ("Ranker margin", "uncertainty_margin"), ("Always-on (3 calls)", "always_on")):
        vt.append([name] + [f3(V["results"][f"{s}/{lv}"][m]["mean_acc"]) for s in ("val", "test") for lv in LV])
    slide("b_valtest", "Backup: VoI on validation and test seeds", "Backup · Contribution 2 · seeds 100 to 399", [
        TABLE(100, 240, 1720, [3.6, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4], vt, size=28, rowh=80, hl=[]),
        T(100, 760, 1720, 200, ["The same ordering as the final test. Uniform priors use no training data at all and were evaluated only "
                                "here."], size=28, color=GREY)],
        "out/voi_eval/valtest.json results.<split>/<level>.<method>.mean_acc.", backup=True)
    lat = D["latency_s"]
    slide("b_cost", "Backup: cost on the MacBook", "Backup · Contribution 2", [
        TABLE(100, 240, 1000, [3.4, 1.4], [["Step", "Seconds"]] + [[k, f"{v:.3g}"] for k, v in lat.items()], size=28, rowh=80, hl=[1]),
        img(1160, 240, 660, 377, "latency.png"),
        T(100, 700, 1000, 200, ["VoI makes about 100 ranker calls per decision and noise level; the learned selector is one small "
                                "forward pass."], size=28, color=GREY)],
        "out/voi_eval/diagnosis.json latency_s; figure paper/figures/latency.pdf.", backup=True)
    yrows = [["Question vs truth (validation)", "AUROC", "95% CI", "Positives"]]
    for q, v in yq.items():
        if v["auroc"] is not None and v["positives"] >= 30:
            yrows.append([q, f"{v['auroc']:.3f}", ci(v["ci95"]), f"{v['positives']} of {Y['n']:,}"])
    slide("b_yesno", "Backup: VLM yes/no detectors", "Backup · Contribution 2 · P(Yes) against P(No) in the first answer token", [
        TABLE(100, 240, 1100, [4, 1.4, 2.2, 2], yrows, size=26, rowh=76, hl=[1]),
        img(1240, 240, 580, 398, "vlm_yesno_auroc.png"),
        T(100, 760, 1720, 220, ["The pedestrian score tracks the scenario family: only occluded_pedestrian has pedestrians, so it cannot "
                                f"be tested within a family. Red light holds within its family ({red_in:.2f})."], size=28, color=GREY)],
        "out/vlm_yesno/eval_val.json questions.<q> (auroc, ci95, positives, by_family); figure paper/figures/vlm_yesno_auroc.pdf.",
        backup=True)
    return out


# Joint order. Keys of Max's slides are matched on the start of his slide titles.
MAX_KEYS = [("problem", "The question:"), ("setup", "Setup:"), ("method", "Method:"), ("baselines", "Baselines:"),
            ("tested", "How we tested"), ("res1", "First final test:"), ("res2", "Second final test:"), ("headline", "At 0.6 calls"),
            ("pareto", "Accuracy against calls:"), ("safety", "Safety:"), ("drives", "What drives it"), ("wrong", "Where it goes wrong"),
            ("vlm", "VLM features"), ("limits", "Limits:"), ("next", "Next steps"), ("summary", "Summary")]
ORDER = [("title", "Max"), ("problem", "Max"),
         ("setup", "Eshan"), ("baselines", "Eshan"), ("tested", "Eshan"),
         ("method", "Max"), ("res1", "Max"), ("res2", "Max"), ("headline", "Max"), ("pareto", "Max"), ("safety", "Max"),
         ("drives", "Max"), ("wrong", "Max"), ("vlm", "Max"), ("summary", "Max"),
         ("c2_method", "Eshan"), ("c2_result", "Eshan"), ("c2_curve", "Eshan"), ("c2_why", "Eshan"), ("c2_vlm", "Eshan"),
         ("limits", "Max"), ("next", "Max"),
         ("conclusion", "Eshan")]
SECTION = {"title": "Intro", "problem": "Intro", "setup": "Background", "baselines": "Background", "tested": "Background",
           "limits": "Limitations", "next": "Limitations", "conclusion": "Conclusion"}
SUBTITLE_OLD = "A learned selector that looks at the candidate trajectories, tested on fresh seeds"
SUBTITLE_NEW = "A learned selector and a counterfactual value-of-information selector"


def _title(K, slide):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.top == K["Emu"](86 * K["PX"]):
            return sh.text_frame.text
    return ""


def _set_footer(K, slide, label):
    pat = re.compile(r"^CMPE 249 · CASS-VLA · B?\d+$")
    for sh in slide.shapes:
        if sh.has_text_frame and pat.match(sh.text_frame.text):
            runs = sh.text_frame.paragraphs[0].runs
            runs[0].text = f"CMPE 249 · CASS-VLA · {label}"
            for r in runs[1:]:
                r.text = ""
            return
    Emu, PX = K["Emu"], K["PX"]
    tb = slide.shapes.add_textbox(Emu(1300 * PX), Emu(1020 * PX), Emu(520 * PX), Emu(40 * PX))
    p = tb.text_frame.paragraphs[0]
    p.alignment = K["PP_ALIGN"].RIGHT
    K["add_runs"](p, f"CMPE 249 · CASS-VLA · {label}", 24, K["GREY"], False)


def build(out_dir=os.path.join(ROOT, "docs/final/deck"), pdf=False):
    K = max_toolkit()
    prs = K["Presentation"](os.path.join(MAXD, "deck.pptx"))
    K["prs"], K["blank"] = prs, prs.slide_layouts[6]
    theirs = list(prs.slides)
    keyed, backups = {"title": theirs[0]}, []
    for s in theirs[1:]:
        t = _title(K, s)
        key = next((k for k, start in MAX_KEYS if t.startswith(start)), None)
        if key:
            keyed[key] = s
        elif t.startswith("Backup:"):
            backups.append(s)
        else:
            raise SystemExit(f"unexpected slide in Max's deck: {t!r}")
    missing = [k for k, _ in MAX_KEYS if k not in keyed]
    if missing:
        raise SystemExit(f"Max's deck changed; slides not found: {missing}")
    srcs = {k: s.notes_slide.notes_text_frame.text for k, s in keyed.items()}
    mine_b = []
    for key, spec in eshan_slides(K, data()):
        sl = K["add_slide"](spec)
        srcs[key] = "Sources: " + spec["src"]
        if spec["backup"]:
            mine_b.append(sl)
        else:
            keyed[key] = sl
    # title subtitle names both contributions
    for sh in keyed["title"].shapes:
        if sh.has_text_frame and sh.text_frame.text == SUBTITLE_OLD:
            runs = sh.text_frame.paragraphs[0].runs
            runs[0].text = SUBTITLE_NEW
            for r in runs[1:]:
                r.text = ""
    order = [(keyed[k], who, SECTION.get(k, "Contribution 1" if who == "Max" else "Contribution 2")) for k, who in ORDER]
    order += [(s, "Max", "Backup, Contribution 1") for s in backups] + [(s, "Eshan", "Backup, Contribution 2") for s in mine_b]
    assert len(order) == len(prs.slides), (len(order), len(prs.slides))
    lst = prs.slides._sldIdLst
    ids = {e.get("id"): e for e in lst}
    want = [str(s.slide_id) for s, _, _ in order]
    for e in list(lst):
        lst.remove(e)
    for i in want:
        lst.append(ids[i])
    rows, mi, bi = [], 0, 0
    for s, who, section in order:
        backup = section.startswith("Backup")
        if backup:
            bi += 1
            label = f"B{bi}"
        else:
            mi += 1
            label = str(mi)
        if mi > 1 or backup:
            _set_footer(K, s, label)
        src = s.notes_slide.notes_text_frame.text
        s.notes_slide.notes_text_frame.text = f"Speaker: {'Max Dokukin' if who == 'Max' else 'Eshan Chawla'} ({section}).\n{src}"
        title = _title(K, s) or "Title"
        rows += [f"## {'Backup ' if backup else 'Slide '}{label}: {title}", "", f"Speaker: {who} ({section}).", "",
                 src.removeprefix("Sources: "), ""]
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "joint_deck.pptx")
    prs.save(path)
    head = ["# Joint deck: speakers and sources", "",
            "Built by `docs/final/build_joint_deck.py` from Max's published `deck.pptx` (his slides and numbers unchanged; "
            "only the title subtitle names both contributions) plus Eshan's slides. Paths of Max's sources are relative to "
            "`research/2026-11-19_learned_selector/` unless they start with `out/`, `docs/` or `deliverables/`; his result files "
            "are on his machine. Eshan's numbers are read from the JSON files named below when the deck is built.", ""]
    open(os.path.join(out_dir, "SOURCES.md"), "w").write("\n".join(head + rows))
    if pdf:
        soffice = shutil.which("soffice") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", out_dir, path], check=True, capture_output=True)
    print(f"saved {path}: {mi} main slides, {bi} backups")
    return path


if __name__ == "__main__":
    build(pdf="--no-pdf" not in sys.argv)
