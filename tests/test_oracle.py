"""Phase 2 checks: candidate geometry, tracking, oracle labels and determinism."""
import numpy as np
import pytest

from cassvla.planning import Oracle, Tracker, generate_candidates
from cassvla.planning.geometry import box, poly_distance
from cassvla.scenarios import make_env


def test_poly_distance():
    a = box((0, 0), 0.0, 4.0, 2.0)
    assert poly_distance(a, box((1, 0), 0.3, 4.0, 2.0)) == 0.0
    assert poly_distance(a, box((10, 0), 0.0, 4.0, 2.0)) == pytest.approx(6.0)


@pytest.fixture(scope="module")
def oracle():
    o = Oracle("lane_blockage", start_seed=0, num_scenarios=2)
    yield o
    o.close()


def test_candidates_and_tracking(oracle):
    env = oracle.env
    env.reset(seed=0)
    for _ in range(15):
        env.step([0.0, 0.4])
    cands = generate_candidates(env)
    names = [c.name for c in cands]
    assert names[:4] == ["keep", "keep_fast", "decelerate", "stop"]
    assert {"change_left", "change_right"} <= set(names)       # ego spawns in the middle lane
    for c in cands:
        assert len(c.t) == len(c.xy) == len(c.speed)
        assert np.linalg.norm(c.xy[0] - np.asarray(env.agent.position)[:2]) < 0.5
        assert np.all(np.linalg.norm(np.diff(c.xy, axis=0), axis=1) < 2.0)   # no jumps
    stop = cands[names.index("stop")]
    assert stop.speed[-1] == 0.0
    tr = Tracker(stop, env.agent)
    for _ in range(len(stop.t) - 1):
        env.step(tr.act(env.agent))
    assert env.agent.speed < 0.3
    assert tr.tracking_error()["max_along"] < 1.0


def test_label_ranks_safe_first(oracle):
    rec = oracle.label(seed=0, t_dec=2.0)
    assert "skipped" not in rec
    m = rec["metrics"]
    assert set(rec["oracle_order"]) == set(m)
    assert m["keep_fast"]["collision"] or not m["keep_fast"]["safe"]   # stalled car ahead in the ego lane
    assert m["stop"]["safe"]
    assert m[rec["c_star"]]["safe"]
    safe_flags = [m[n]["safe"] for n in rec["oracle_order"]]
    assert safe_flags == sorted(safe_flags, reverse=True)
    assert rec["retained"]


def test_label_is_repeatable(oracle):
    a, b = oracle.label(seed=1, t_dec=1.5), oracle.label(seed=1, t_dec=1.5)
    assert a["oracle_order"] == b["oracle_order"]
    for n in a["metrics"]:
        assert abs(a["metrics"][n]["score"] - b["metrics"][n]["score"]) < 0.05
