"""Tool models, labels, dataset split and the policy invariants."""
import json
import os
import sys

import numpy as np
import pytest

from cassvla.planning import Oracle
from cassvla.planning.features import FEATURE_NAMES
from cassvla.planning.labels import label_record
from cassvla.planning.ranker import rank
from cassvla.planning.tools import LEVELS, TOOLS, base_observation, in_camera, tool_collision, tool_depth, tool_roi

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from build_dataset import split_seeds  # noqa: E402


@pytest.fixture(scope="module")
def recs():
    def jsonable(rec):
        return json.loads(json.dumps(rec))
    out = {}
    for fam, seed, t in (("occluded_pedestrian", 0, 1.5), ("ambiguous_light", 0, 2.0), ("merge_closing_speed", 0, 3.0)):
        o = Oracle(fam, start_seed=seed, num_scenarios=1)
        out[fam] = jsonable(o.label(seed, t))
        o.close()
    return out


def _truth(rec):
    return {a["name"]: a for a in rec["actors"]}


def test_perfect_tools_return_ground_truth(recs):
    for rec in recs.values():
        truth = _truth(rec)
        for fn in (tool_roi, tool_depth, tool_collision):
            for a in fn(rec, "perfect")["actors"]:
                assert np.allclose(a["position"], truth[a["name"]]["position"])
                assert np.allclose(a["velocity"], truth[a["name"]]["measured_velocity"])
    rec = recs["ambiguous_light"]
    assert tool_roi(rec, "perfect")["light"] == rec["signals"]["ego_status"]


def test_same_record_gives_same_noise(recs):
    rec = recs["merge_closing_speed"]
    for fn in (tool_roi, tool_depth, tool_collision):
        a, b = fn(rec, "high")["actors"], fn(rec, "high")["actors"]
        assert [x["name"] for x in a] == [x["name"] for x in b]
        for x, y in zip(a, b):
            assert np.array_equal(x["position"], y["position"])
    x = [a["position"] for a in tool_depth(rec, "low")["actors"]]
    y = [a["position"] for a in tool_depth(rec, "high")["actors"]]
    assert not all(np.array_equal(p, q) for p, q in zip(x, y))


def test_roi_reveals_the_hidden_pedestrian(recs):
    rec = recs["occluded_pedestrian"]
    ped = next(a for a in rec["actors"] if a["name"] == "pedestrian")
    assert not in_camera(rec, ped)
    assert "pedestrian" not in {a["name"] for a in base_observation(rec)["actors"]}
    assert "pedestrian" in {a["name"] for a in tool_roi(rec, "perfect")["actors"]}
    assert "pedestrian" not in {a["name"] for a in tool_depth(rec, "perfect")["actors"]}


def test_label_schema(recs):
    for rec in recs.values():
        lab = label_record(rec)
        assert len(lab["features"]) == len(FEATURE_NAMES)
        assert set(lab["levels"]) == set(LEVELS)
        for lv in lab["levels"].values():
            assert set(lv["tools"]) == set(TOOLS)
            assert lv["abstain"] == (not any(lv["decision_change"].values()))
        if lab["no_tool"]["correct"]:
            assert all(not any(lv["decision_change"].values()) for lv in lab["levels"].values())


def test_ranker_puts_predicted_safe_first(recs):
    rec = recs["merge_closing_speed"]
    r = rank(rec, base_observation(rec))
    flags = [r["metrics"][n]["safe"] for n in r["order"]]
    assert flags == sorted(flags, reverse=True)


def test_split_has_no_shared_seeds():
    s = split_seeds(range(100, 400))
    a, b, c = set(s["train"]), set(s["val"]), set(s["test"])
    assert not (a & b or a & c or b & c)
    assert len(a) == 210 and len(b) == 45 and len(c) == 45
    assert s == split_seeds(range(100, 400))
