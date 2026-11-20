"""Diagnosis statistics behind docs/voi_selector.md."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_spearman_matches_known_values():
    from voi_diagnosis import spearman
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)


def test_diagnose_on_a_perfect_score():
    from voi_diagnosis import diagnose
    rng = np.random.default_rng(0)
    gain = rng.normal(size=(200, 3))
    d = diagnose(voi=gain.copy(), gain=gain, base_correct=np.zeros(200), margin=rng.normal(size=200))
    assert d["auroc_maxvoi_any_gain"] == pytest.approx(1.0)
    assert d["spearman_per_tool"] == pytest.approx([1.0, 1.0, 1.0])
    assert d["tool_optimal_when_gain"] == 1.0 and d["base_correct_rate"] == 0.0
