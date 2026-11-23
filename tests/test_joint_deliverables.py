"""The joint deck and report must keep Max's published slides and report text unchanged and add Eshan's part."""
import importlib.util
import os
import re

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAX_DECK = os.path.join(ROOT, "research/2026-11-19_learned_selector/deliverables/deck/deck.pptx")
MAX_REPORT = os.path.join(ROOT, "research/2026-11-19_learned_selector/deliverables/report/report.md")
NEEDS = [os.path.join(ROOT, p) for p in ("out/voi_eval/final.json", "out/voi_eval/valtest.json", "out/voi_eval/diagnosis.json",
                                         "out/vlm_yesno/eval_val.json", "out/vlm_probe/report.json")]
pytestmark = pytest.mark.skipif(not all(os.path.exists(p) for p in NEEDS), reason="VoI result files in out/ are not on this machine")
pptx = pytest.importorskip("pptx")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "docs/final", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _texts(slide):
    out = []
    for sh in slide.shapes:
        if sh.has_text_frame:
            out += [p.text for p in sh.text_frame.paragraphs if p.text.strip()]
        if sh.has_table:
            out += [c.text for r in sh.table.rows for c in r.cells if c.text.strip()]
    return out


FOOTER = re.compile(r"^CMPE 249 · CASS-VLA · B?\d+$")


def test_joint_deck_keeps_every_max_slide_unchanged(tmp_path):
    path = _load("build_joint_deck").build(str(tmp_path))
    joint = pptx.Presentation(path)
    theirs = pptx.Presentation(MAX_DECK)
    joint_texts = [[t for t in _texts(s) if not FOOTER.match(t)] for s in joint.slides]
    for i, s in enumerate(theirs.slides):
        want = [t for t in _texts(s) if not FOOTER.match(t)]
        if i == 0:  # title slide: only the subtitle changes, to name both contributions
            want = [t for t in want if not t.startswith("A learned selector that looks at")]
        assert any(all(t in got for t in want) for got in joint_texts), f"Max's slide {i + 1} lost text: {want[:2]}"
    assert len(joint.slides) > len(theirs.slides)


def test_joint_deck_names_a_speaker_on_every_slide_and_renumbers_footers(tmp_path):
    joint = pptx.Presentation(_load("build_joint_deck").build(str(tmp_path)))
    feet = []
    for s in joint.slides:
        assert s.notes_slide.notes_text_frame.text.startswith("Speaker: "), _texts(s)[:1]
        feet += [t for t in _texts(s) if FOOTER.match(t)]
    main = [int(f.rsplit(" ", 1)[1]) for f in feet if not f.endswith(tuple(f"B{i}" for i in range(100)))]
    assert main == list(range(2, 2 + len(main))), main


def test_joint_report_keeps_max_text_and_adds_contribution_2(tmp_path):
    md = open(_load("build_joint_report").build(str(tmp_path))).read()
    theirs = open(MAX_REPORT).read()
    kept = [p for p in theirs.split("\n\n") if p.strip() and not p.startswith(("# ", "*CMPE 249", "## 7 ", "## 8 ", "5. **Add the missing"))
            and "](../figures/" not in p]
    missing = [p[:80] for p in kept if p not in md]
    assert not missing, missing
    assert "## 7 Contribution 2: counterfactual value-of-information selector" in md
    assert "## 8 Limitations" in md and "## 9 Next steps" in md
    prose = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", md, flags=re.S))  # code may quote JSON replies
    assert "{" not in prose, "unfilled template field"
