"""Joining VoI rows onto the harness's split rows."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def _rows(n):
    split = [dict(family="f", seed=s, t_dec=0.5 * (i + 1)) for s in range(n) for i in range(2)]
    vois = []
    for j, r in enumerate(split):
        v = {"roi": float(j), "depth": float(-j), "collision": 0.5}
        vois.append(dict(family=r["family"], seed=r["seed"], t_dec=r["t_dec"], levels={"mid": dict(voi=v)}))
    return split, vois


def test_align_orders_by_split_rows():
    from eval_voi import align
    split, vois = _rows(3)
    rng = np.random.default_rng(0)
    shuffled = [vois[i] for i in rng.permutation(len(vois))]
    score, tool, allow = align(shuffled, split, "mid", 0.0)
    assert score.tolist() == [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
    assert tool.tolist() == [2, 0, 0, 0, 0, 0]
    assert allow.tolist() == [True] * 6


def test_align_aborts_on_missing_rows():
    from eval_voi import align
    split, vois = _rows(3)
    with pytest.raises(SystemExit, match="1 of 6"):
        align(vois[1:], split, "mid", 0.0)


def test_align_matches_t_dec_float_noise():
    from eval_voi import align
    split, vois = _rows(1)
    split[0]["t_dec"] = 0.5000000000000001
    score, _, _ = align(vois, split, "mid", 0.0)
    assert len(score) == 2


def test_lambda_none_gives_budget_only():
    from eval_voi import align
    split, vois = _rows(2)
    assert align(vois, split, "mid", None)[2] is None


def test_harness_root_is_this_repo():
    from eval_voi import ROOT, _harness
    F = _harness()
    assert os.path.realpath(F.X.ROOT) == os.path.realpath(ROOT)
