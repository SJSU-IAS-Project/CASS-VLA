"""Phase 5 checks: the camera frame is taken at the same decision point the oracle labelled."""
import numpy as np
import pytest

from cassvla.perception import FrameRenderer, frame_key
from cassvla.planning import Oracle

FAMILY, SEED, T_DEC, SIZE = "occluded_pedestrian", 101, 2.0, (320, 180)


@pytest.fixture(scope="module")
def frames():
    # MetaDrive allows one engine per process, so the oracle and the renderer run one after the other.
    oracle = Oracle(FAMILY, start_seed=SEED, num_scenarios=1)
    try:
        rec = oracle.label(SEED, T_DEC)
    finally:
        oracle.close()
    renderer = FrameRenderer(FAMILY, start_seed=SEED, num_scenarios=1, size=SIZE)
    try:
        first, second = renderer.render(SEED, T_DEC), renderer.render(SEED, T_DEC)
    finally:
        renderer.close()
    return rec, first, second


def test_frame_shape_and_type(frames):
    _, out, _ = frames
    w, h = SIZE
    assert out["image"].shape == (h, w, 3) and out["image"].dtype == np.uint8
    assert out["key"] == frame_key(FAMILY, SEED, T_DEC) == "occluded_pedestrian/101_2.0"


def test_frame_is_rgb(frames):
    # the top rows are sky: blue must dominate red in RGB order (MetaDrive's raw buffer is BGR)
    sky = frames[1]["image"][:10].reshape(-1, 3).astype(float).mean(axis=0)
    assert sky[2] > sky[0]


def test_ego_pose_matches_oracle_record(frames):
    rec, out, _ = frames
    assert "skipped" not in rec
    assert np.allclose(out["ego"]["position"], rec["ego"]["position"], atol=0.02)
    assert out["ego"]["heading"] == pytest.approx(rec["ego"]["heading"], abs=1e-3)
    assert out["ego"]["speed"] == pytest.approx(rec["ego"]["speed"], abs=0.02)


def test_rendering_is_repeatable(frames):
    _, a, b = frames
    # re-resetting one env drifts by ~1e-5 m (docs/oracle.md), so allow sub-grey-level differences
    assert np.abs(a["image"].astype(int) - b["image"].astype(int)).mean() < 0.5


def test_render_seed_matches_oracle_at_every_decision():
    """One rollout per seed stops at each t_dec; the ego must be where separate oracle prefixes put it."""
    family, seed, times = "occluded_cross_traffic", 103, [1.0, 2.5, 4.0]
    oracle = Oracle(family, start_seed=seed, num_scenarios=1)
    try:
        recs = {t: oracle.label(seed, t) for t in times}
    finally:
        oracle.close()
    renderer = FrameRenderer(family, start_seed=seed, num_scenarios=1, size=SIZE)
    try:
        outs = list(renderer.render_seed(seed, reversed(times)))
    finally:
        renderer.close()
    assert [o["t_dec"] for o in outs] == times
    for o in outs:
        rec = recs[o["t_dec"]]
        assert np.allclose(o["ego"]["position"], rec["ego"]["position"], atol=0.02)
        assert o["ego"]["speed"] == pytest.approx(rec["ego"]["speed"], abs=0.02)
