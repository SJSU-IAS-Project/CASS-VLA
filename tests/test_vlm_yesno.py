"""Ground truth and AUROC for the VLM yes/no questions (scripts/eval_vlm_yesno.py)."""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RECS = {json.loads(line)["family"]: json.loads(line) for line in open(os.path.join(HERE, "fixtures", "records_small.jsonl"))}


def test_truth_hidden_uses_line_of_sight():
    from eval_vlm_yesno import truth
    assert truth(RECS["occluded_pedestrian"])["hidden"] is True       # the pedestrian behind the parked car
    assert truth(RECS["lane_blockage"])["hidden"] is False            # every actor in view is visible


def test_truth_pedestrian_counts_hidden_ones():
    from eval_vlm_yesno import truth
    t = truth(RECS["occluded_pedestrian"])
    assert t["pedestrian"] is True and t["pedestrian_visible"] is False


def test_auroc_perfect_scores():
    from eval_vlm_yesno import auroc
    y = np.array([0, 0, 1, 1, 1])
    assert auroc(y.astype(float), y) == 1.0
    assert auroc(1.0 - y, y) == 0.0
    assert auroc(np.full(5, 0.5), y) == pytest.approx(0.5)
