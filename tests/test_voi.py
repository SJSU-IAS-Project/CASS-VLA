"""The counterfactual value-of-information selector on fixture records with known structure."""
import copy
import json
import os

import numpy as np
import pytest

from cassvla.planning import tools as T

HERE = os.path.dirname(__file__)
RECS = {json.loads(line)["family"]: json.loads(line) for line in open(os.path.join(HERE, "fixtures", "records_small.jsonl"))}


def test_weights_sum_to_one_and_skip_empty_classes():
    from cassvla.planning.voi import UNIFORM, weighted_worlds
    for rec in RECS.values():
        base = T.base_observation(rec)
        worlds = weighted_worlds(rec, base, UNIFORM)
        assert abs(sum(w for w, _ in worlds) - 1.0) < 1e-9
    rec = RECS["lane_blockage"]                       # no stop line, so no light worlds
    only = weighted_worlds(rec, T.base_observation(rec), UNIFORM, classes=("null", "light"))
    assert len(only) == 1 and only[0][0] == 1.0


def _unique_names(rec):
    names = [a["name"] for a in rec["actors"]]
    return len(names) == len(set(names))


def test_voi_is_zero_when_only_null_world():
    # tools.merge keys actors by name, so a call collapses repeated names (lane_blockage's three "cones");
    # VoI models that real merge, and a perfect tool in the null world is a no-op only when names are unique
    from cassvla.planning.voi import select, voi
    for rec in filter(_unique_names, RECS.values()):
        out = voi(rec, "perfect", classes=("null",))
        assert out["voi"] == {t: 0.0 for t in T.TOOLS}
        assert select(out["voi"])[2] is False


def test_noisy_tool_never_helps_in_the_null_world():
    from cassvla.planning.voi import select, voi
    for rec in RECS.values():
        out = voi(rec, "mid", classes=("null",))
        assert all(v <= 1e-9 for v in out["voi"].values()), rec["family"]
        assert select(out["voi"])[2] is False


def test_pseudo_record_keeps_observed_shapes_in_the_null_world():
    from cassvla.planning.voi import pseudo_record
    for rec in RECS.values():
        base = T.base_observation(rec)
        observed = [a["poly"] for a in rec["actors"] if T.in_camera(rec, a)]
        got = [a["poly"] for a in pseudo_record(rec, base, 0, base)["actors"]]
        assert len(got) == len(observed)
        for g, o in zip(got, observed):
            assert np.allclose(g, o)


def test_voi_ignores_privileged_fields():
    from cassvla.planning.voi import voi
    for rec in RECS.values():
        before = voi(rec, "mid")["voi"]
        r = copy.deepcopy(rec)
        r["c_star"] = next(c["name"] for c in r["candidates"] if c["name"] != rec["c_star"])
        r["oracle_order"] = list(reversed(r["oracle_order"]))
        r["metrics"] = {n: dict(m, safe=not m["safe"], score=-m["score"]) for n, m in r["metrics"].items()}
        visible = {a["name"] for a in T.base_observation(rec)["actors"]}
        for a in r["actors"]:
            if a["name"] not in visible:
                a["measured_velocity"] = [v + 3.0 for v in a["measured_velocity"]]
        d = T.light_stop_distance(rec)
        if d is None or d > T.LIGHT_READABLE_RANGE:   # unreadable light: the true state must not matter
            r["signals"] = dict(r["signals"], ego_status="TRAFFIC_LIGHT_RED")
        assert voi(r, "mid")["voi"] == before, rec["family"]


def test_voi_is_deterministic():
    from cassvla.planning.voi import voi
    rec = RECS["occluded_pedestrian"]
    assert voi(rec, "high")["voi"] == voi(rec, "high")["voi"]


def test_perfect_roi_has_highest_voi_behind_occluder():
    from cassvla.planning.voi import voi
    out = voi(RECS["occluded_pedestrian"], "perfect", classes=("null", "occl_ped"))["voi"]
    assert out["roi"] > 0
    assert out["roi"] > out["depth"]


def test_light_world_values_roi_on_unread_light():
    from cassvla.planning.voi import select, voi
    rec = RECS["ambiguous_light"]
    assert T.base_observation(rec)["light"] is None and T.light_stop_distance(rec) is not None
    out = voi(rec, "perfect", classes=("null", "light"))["voi"]
    assert T.TOOLS[select(out)[1]] == "roi" and out["roi"] > 0


def test_select_abstains_below_lambda():
    from cassvla.planning.voi import select
    assert select({"roi": -1.0, "depth": 0.0, "collision": -2.0}, 0.0) == (0.0, 1, False)
    assert select({"roi": 2.0, "depth": 0.5, "collision": 0.0}, 0.0) == (2.0, 0, True)
