"""The shared hypothesis generator: same worlds as the flip features, built from the base observation only."""
import json
import os
import sys

import pytest

from cassvla.planning import tools as T
from cassvla.scenarios.signals import GREEN, RED

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from flip_features import flip_row  # noqa: E402

RECORDS = [json.loads(line) for line in open(os.path.join(HERE, "fixtures", "records_small.jsonl"))]
EXPECTED = json.load(open(os.path.join(HERE, "fixtures", "flip_expected.json")))


def _key(rec):
    return f"{rec['family']}/{rec['seed']}_{rec['t_dec']}"


@pytest.mark.parametrize("rec", RECORDS, ids=_key)
def test_flip_features_unchanged_by_refactor(rec):
    assert flip_row(rec)["flip"] == EXPECTED[_key(rec)]


@pytest.mark.parametrize("rec", RECORDS, ids=_key)
def test_hypotheses_use_only_visible_actors(rec):
    from cassvla.planning.hypotheses import hypotheses
    base = T.base_observation(rec)
    visible = {a["name"] for a in base["actors"]}
    hidden = {a["name"] for a in rec["actors"]} - visible
    for worlds in hypotheses(rec, base).values():
        for w in worlds:
            names = {a["name"] for a in w["actors"]}
            assert visible <= names
            assert not names & hidden


@pytest.mark.parametrize("rec", RECORDS, ids=_key)
def test_light_hypotheses_only_when_unread(rec):
    from cassvla.planning.hypotheses import hypotheses
    base = T.base_observation(rec)
    light = hypotheses(rec, base)["light"]
    if base["light"] is not None or T.light_stop_distance(rec) is None:
        assert light == []
    else:
        assert sorted(w["light"] for w in light) == sorted([RED, GREEN])
    read = dict(base, light=GREEN)
    assert hypotheses(rec, read)["light"] == []
