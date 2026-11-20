"""The results page generator's own computation: how much weight each hidden event really gets."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_effective_weights_normalise_over_components_and_split_light():
    from make_voi_page import effective_weights
    w = effective_weights(dict(null=1.0, depth=1.0, occl_static=0.0, occl_ped=0.0, light=1.0, rear=0.0))
    assert w["no_hidden_event"] == pytest.approx(0.5)
    assert w["red_light"] == pytest.approx(0.25)          # the light class holds a red and a green world
    assert w["occluded_road_user"] == 0.0
