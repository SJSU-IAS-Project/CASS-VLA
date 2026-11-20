"""The paper figures are written as vector PDFs (no embedded raster images, fonts embedded as TrueType)."""
import importlib.util
import os
import re

import numpy as np

HERE = os.path.dirname(__file__)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_all_figures_are_vector(tmp_path):
    te = _load("test_eval_helpers", "test_eval.py")
    mf = _load("make_figures", "../scripts/make_figures.py")
    rng = np.random.default_rng(0)
    rows = [te._row(rng, s, i) for s in range(30) for i in range(8)]
    train, test = rows[:160], rows[160:]
    vlm = dict(Xtr=np.ones((160, 1)), Xte=np.ones((80, 1)), tool_te=-np.ones(80, int), cost=1.0)
    report = {lv: te.ev.evaluate(train, test, lv, "correct", {"margin": 3}, te.ALL_COLS, vlm=vlm) for lv in te.ev.LEVELS}
    lv_entry = lambda auc, d: dict(auc=auc, ci95=[auc - 0.01, auc + 0.01], **({} if d is None else dict(delta_vs_ref=d, delta_ci95=[d - 0.01, d + 0.01])))
    abl = dict(ablations=[dict(name="reference", label="Reference", levels={"mid": dict(lv_entry(0.4, None), reference=True)}),
                          dict(name="scene_only", label="Scene-only", levels={"mid": lv_entry(0.38, -0.02)})])
    mf.pareto(report, 0, tmp_path / "a.pdf")
    mf.pareto(report, 1, tmp_path / "u.pdf")
    mf.families(report, tmp_path / "f.pdf")
    mf.ablations(abl, tmp_path / "x.pdf")
    for name in ("a.pdf", "u.pdf", "f.pdf", "x.pdf"):
        data = (tmp_path / name).read_bytes()
        assert data.startswith(b"%PDF")
        assert not re.search(rb"/Subtype\s*/Image", data), name
        assert b"/FontFile2" in data, name                 # TrueType embedded (pdf.fonttype 42)
