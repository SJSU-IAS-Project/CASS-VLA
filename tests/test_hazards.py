"""Hazard geometry and label independence from earlier runs in the same env."""
import numpy as np
import pytest

from cassvla.planning import Oracle
from cassvla.planning.geometry import box
from cassvla.scenarios import make_env


def _segment_hits_box(a, b, poly, n=200):
    lo, hi = poly.min(axis=0), poly.max(axis=0)
    pts = np.linspace(a, b, n)
    return bool(np.any(np.all((pts >= lo) & (pts <= hi), axis=1)))


@pytest.mark.parametrize("seed", range(6))
def test_pedestrian_starts_hidden_behind_parked_car(seed):
    env = make_env("occluded_pedestrian", seed=0, num_scenarios=6)
    try:
        env.reset(seed=seed)
        hz = env.hazards.get_state()["hazards"]
        car, ped = hz["parked_car"], hz["pedestrian"]
        cx, cy = car["position"]
        length, width = car["size"]
        px, py = ped["position"]
        assert abs(py - cy) < 0.5
        assert px - cx > length / 2
        poly = box((cx, cy), car["heading"], length, width)
        assert _segment_hits_box(np.asarray(env.agent.position)[:2], np.array([px, py]), poly)
    finally:
        env.close()


def test_cut_in_reaches_ego_lane():
    env = make_env("lead_brake_cutin", seed=0, num_scenarios=20)
    try:
        cut_ins = 0
        for seed in range(20):
            env.reset(seed=seed)
            if "cutter" not in env.hazards.get_state()["hazards"]:
                continue
            cut_ins += 1
            ego_y = float(env.agent.position[1])
            ys = []
            for _ in range(150):
                env.step([0.0, 0.5])
                ys.append(env.hazards.get_state()["hazards"]["cutter"]["position"][1])
            assert min(abs(y - ego_y) for y in ys) < 0.5, f"seed {seed}: cutter stayed at {ys[-1]}"
        assert cut_ins > 0
    finally:
        env.close()


def test_label_does_not_depend_on_history():
    family, seed, t = "occluded_cross_traffic", 2, 4.0
    fresh = Oracle(family, start_seed=0, num_scenarios=5)
    a = fresh.label(seed, t)
    fresh.close()
    used = Oracle(family, start_seed=0, num_scenarios=5)
    grid = [round(float(h), 2) for h in np.arange(0.5, 12.01, 0.5)]
    for s in range(seed):
        for h in grid:
            if "skipped" in used.label(s, h):
                break
    for h in grid:
        if h < t:
            used.label(seed, h)
    b = used.label(seed, t)
    used.close()
    assert a["n_safe"] == b["n_safe"]
    assert a["oracle_order"] == b["oracle_order"]
    for n in a["metrics"]:
        assert a["metrics"][n]["safe"] == b["metrics"][n]["safe"]
        assert abs(a["metrics"][n]["score"] - b["metrics"][n]["score"]) < 0.5


def test_reused_cones_start_at_rest():
    o = Oracle("lane_blockage", start_seed=210, num_scenarios=5)
    try:
        for t in (2.0, 3.0, 4.0):
            o.label(210, t)
        o.env.reset(seed=213)
        cones = [c for h in o.env.hazards.hazards if h.name == "cones" for c in h.objs]
        assert cones and all(np.linalg.norm(c.velocity) == 0.0 for c in cones)
    finally:
        o.close()


def test_record_logs_actor_state():
    o = Oracle("merge_closing_speed", start_seed=0, num_scenarios=1)
    try:
        rec = o.label(0, 3.0)
        actors = {a["name"]: a for a in rec["actors"]}
        assert {"slow_lead", "fast_closer"} <= set(actors)
        for a in actors.values():
            assert a["length"] > 0 and a["width"] > 0 and len(a["poly"]) == 4
        closer = actors["fast_closer"]
        assert np.linalg.norm(closer["measured_velocity"]) > 5.0
    finally:
        o.close()
