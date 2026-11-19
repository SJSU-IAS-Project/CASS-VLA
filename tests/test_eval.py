"""Checks for the evaluation and the VLM features on small synthetic data with known answers."""
import importlib.util
import os

import numpy as np
import pytest

from cassvla.perception.vlm_features import PROMPTED_NAMES, VLMFeatures, prompted_vector
from cassvla.planning.tools import TOOLS

_spec = importlib.util.spec_from_file_location("eval_baselines", os.path.join(os.path.dirname(__file__), "..", "scripts", "eval_baselines.py"))
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)


def _row(rng, seed, i):
    """A decision where tool ``fix`` (or none, -1) turns a wrong top-1 into c*."""
    fix = int(rng.integers(-1, 3))
    base_ok = fix == -1 and rng.random() < 0.5
    out = lambda ok: dict(correct=bool(ok), correct_tol=bool(ok), unsafe=not ok, spearman=1.0 if ok else 0.0)
    tools = {t: out(base_ok or j == fix) for j, t in enumerate(TOOLS)}
    level = dict(tools=tools, always_on=out(base_ok or fix >= 0))
    feats = [float(fix == j) + 0.1 * rng.normal() for j in range(3)] + [rng.normal()]
    return dict(family="fam", seed=seed, t_dec=0.5 * i, no_tool=out(base_ok), features=feats, levels={lv: level for lv in ev.LEVELS}, _fix=fix)


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(0)
    rows = [_row(rng, s, i) for s in range(40) for i in range(10)]
    return [r for r in rows if r["seed"] < 30], [r for r in rows if r["seed"] >= 30]


def test_holm_matches_hand_computation():
    c = ev.holm(dict(a=dict(p_boot=0.01), b=dict(p_boot=0.04), c=dict(p_boot=0.03)))
    assert (c["a"]["p_holm"], c["c"]["p_holm"], c["b"]["p_holm"]) == (0.03, 0.06, 0.06)


def test_budget_zero_is_no_tool_and_full_budget_uses_the_tool():
    a0, u0 = np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 1.0])
    at = np.array([[1.0, 0, 0], [1, 1, 1], [0, 0, 1]])
    order, tool = np.arange(3), np.array([0, 0, 2])
    assert ev.apply_policy(order, tool, a0, u0, at, 1 - at, 0.0)[0].tolist() == a0.tolist()
    assert ev.apply_policy(order, tool, a0, u0, at, 1 - at, 1.0)[0].tolist() == [1.0, 1.0, 1.0]


def test_evaluate_with_a_perfect_prompted_vlm_reaches_the_oracle(data):
    train, test = data
    agn = {"margin": 3}
    tool_te = np.array([r["_fix"] if r["_fix"] >= 0 and not r["no_tool"]["correct"] else -1 for r in test])
    vlm = dict(Xtr=np.array([r["features"][:3] for r in train]), Xte=np.array([r["features"][:3] for r in test]), tool_te=tool_te, cost=1.0)
    r = ev.evaluate(train, test, "mid", "correct", agn, vlm)
    n_fix = r["oracle_selector"]["cost"]
    b = int(np.argmin(np.abs(np.array(r["budgets"]) - n_fix)))
    assert r["curves"]["vlm_prompted"][b][0] == pytest.approx(r["oracle_selector"]["acc"], abs=0.02)
    assert r["vlm"]["asked_precision"] == 1.0 and r["vlm"]["abstain_precision"] == 1.0
    assert set(r["cost_offset"]) == {"plandiscrim_vlm_only", "plandiscrim_geom_vlm", "vlm_prompted"}
    for c in r["comparisons"].values():
        assert 1.0 / ev.N_BOOT <= c["p_boot"] <= c["p_holm"] <= 1.0
    # informative features: the learned selector must beat random at every budget above 0
    for (pd, _), (rnd, _) in list(zip(r["curves"]["plandiscrim_geometry"], r["curves"]["random"]))[2:]:
        assert pd >= rnd


def test_vlm_methods_do_not_change_the_other_methods(data):
    train, test = data
    agn = {"margin": 3}
    vlm = dict(Xtr=np.ones((len(train), 2)), Xte=np.ones((len(test), 2)), tool_te=-np.ones(len(test), int), cost=1.0)
    a, b = ev.evaluate(train, test, "low", "correct", agn), ev.evaluate(train, test, "low", "correct", agn, vlm)
    for k in ("plandiscrim_geometry", "uncertainty_margin", "random", "scene_only_learned", "oracle"):
        assert a["curves"][k] == b["curves"][k]


def _cache(n, dim=6, seed=0):
    rng = np.random.default_rng(seed)
    keys = [f"fam/{i}_1.0" for i in range(n)]
    ans = lambda i: dict(hazards=["car"] * (i % 3), occlusion=bool(i % 2), light="red", query=("roi", "none", "collision")[i % 3], parse_error=False)
    return dict(keys=keys, emb=rng.normal(size=(n, dim)).astype(np.float32), prompted={k: ans(i) for i, k in enumerate(keys)})


def test_vlm_features_fit_on_train_only():
    rows = [dict(family="fam", seed=i, t_dec=1.0) for i in range(12)]
    vf = VLMFeatures(_cache(12), n_pca=3).fit(rows[:8])
    X = vf.transform(rows)
    assert X.shape == (12, 3 + len(PROMPTED_NAMES)) and len(vf.names()) == X.shape[1]
    assert np.allclose(X[:8, :3].mean(axis=0), 0.0, atol=1e-9)        # centred on train rows
    assert not np.allclose(X[8:, :3].mean(axis=0), 0.0, atol=1e-3)     # test rows did not move the mean
    assert vf.prompted_tool(rows[:3]).tolist() == [TOOLS.index("roi"), -1, TOOLS.index("collision")]


def test_vlm_features_coverage_and_none_hazards():
    vf = VLMFeatures(_cache(2))
    rows = [dict(family="fam", seed=1, t_dec=1.0), dict(family="fam", seed=5, t_dec=1.0)]
    assert vf.covered(rows).tolist() == [True, False]
    v = prompted_vector(dict(hazards=["none"], occlusion=False, light="green", query="depth", parse_error=False))
    assert v[PROMPTED_NAMES.index("vlm_n_hazards")] == 0.0 and v[PROMPTED_NAMES.index("vlm_query_depth")] == 1.0
