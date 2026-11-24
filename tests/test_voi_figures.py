"""VoI and VLM figures must be vector PDFs with embedded TrueType fonts."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
CURVE = [0.2 + 0.01 * i for i in range(21)]


def _method(acc):
    return dict(mean_acc=acc, mean_unsafe=0.5, curve=CURVE, unsafe_curve=[0.6 - 0.01 * i for i in range(21)],
                **{"at_budget_0.6": dict(acc=acc, unsafe=0.5, call_rate=0.6), "at_budget_1.0": dict(acc=acc, unsafe=0.5, call_rate=0.4)})


def _report():
    res = {f"val/{lv}": dict(voi=_method(0.4), voi_budget=_method(0.41), signed=_method(0.43), uncertainty_margin=_method(0.38),
                            always_on=dict(mean_acc=0.45, mean_unsafe=0.4, calls_per_decision=3)) for lv in ("low", "mid", "high")}
    comp = {f"val/{lv}": {"abl_draws4_minus_abl_reference": dict(mean_diff=-0.01, ci95=[-0.02, 0.0]),
                         "abl_no_rear_minus_abl_reference": dict(mean_diff=0.002, ci95=[-0.003, 0.007])} for lv in ("low", "mid", "high")}
    return dict(results=res, comparisons=comp)


def _vector(path):
    data = open(path, "rb").read()
    assert data.startswith(b"%PDF")
    assert not re.search(rb"/Subtype\s*/Image", data), path
    assert b"/FontFile2" in data, path


def test_voi_figures_are_vector(tmp_path):
    import voi_figures as vf
    rep = _report()
    vf.pareto(rep, "val", "acc", tmp_path / "a.pdf")
    vf.pareto(rep, "val", "unsafe", tmp_path / "u.pdf")
    vf.ablations(rep, "val", tmp_path / "x.pdf")
    vf.yesno({"questions": {"pedestrian vs pedestrian": dict(auroc=0.7, ci95=[0.65, 0.75]), "hidden vs hidden": dict(auroc=0.55, ci95=[0.5, 0.6])}},
             tmp_path / "y.pdf")
    vf.latency({"VoI (per decision, per level)": 0.06, "VLM embed": 0.4, "VLM yes/no x3": 1.5}, tmp_path / "l.pdf")
    for n in ("a.pdf", "u.pdf", "x.pdf", "y.pdf", "l.pdf"):
        _vector(tmp_path / n)
