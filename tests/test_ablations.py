"""Checks for the ablation runner's cost-aware policy, on hand-made data."""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("ablations", os.path.join(os.path.dirname(__file__), "..", "scripts", "ablations.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)
ev = ab.ev


def _data(n=40, seed=0):
    rng = np.random.default_rng(seed)
    a0 = np.zeros(n)
    at = (rng.random((n, 3)) < np.array([0.6, 0.3, 0.5])).astype(float)
    prob = at * 0.8 + 0.1 * rng.random((n, 3))
    return prob, a0, at


def test_unit_costs_reproduce_the_evaluation_policy():
    prob, a0, at = _data()
    plain = ab.policy_curve(prob, a0, at, np.random.default_rng(0))
    unit = ab.policy_curve(prob, a0, at, np.random.default_rng(0), costs=[1.0, 1.0, 1.0])
    assert np.array_equal(plain, unit)
    assert np.array_equal(plain[:, 0], a0)        # budget 0 is no tool


def test_cheap_tool_buys_more_queries_and_cost_awareness_uses_it():
    prob, a0, at = _data()
    costs = [4.0, 4.0, 0.25]
    aware = ab.policy_curve(prob, a0, at, np.random.default_rng(0), costs=costs)
    unaware = ab.policy_curve(prob, a0, at, np.random.default_rng(0), costs=costs, aware=False)
    b = list(ev.BUDGETS).index(0.25)
    assert aware[:, b].mean() > unaware[:, b].mean()


def test_budget_never_overspent():
    prob, a0, at = _data()
    costs = np.array([3.0, 1.0, 0.5])
    rng = np.random.default_rng(0)
    per_cost = prob / costs
    order, tool = ev.rank_desc(per_cost.max(axis=1), rng), per_cost.argmax(axis=1)
    spent = np.cumsum(costs[tool[order]])
    for b in ev.BUDGETS:
        k = int(np.searchsorted(spent, b * len(a0) + 1e-9, side="right"))
        assert k == 0 or spent[k - 1] <= b * len(a0) + 1e-9


def test_gbm_selector_learns_a_separable_rule():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(300, 2))
    gain = np.stack([(X[:, 0] > 0), (X[:, 1] > 0), np.zeros(300, bool)], axis=1).astype(float)
    p = ab.predict_gbm(ab.fit_gbm(X, gain), X)
    assert ((p[:, 0] > 0.5) == (X[:, 0] > 0)).mean() > 0.95
    assert np.allclose(p[:, 2], 0.0)              # a tool that never helps gets a constant 0
