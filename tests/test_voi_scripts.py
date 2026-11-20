"""scripts/voi_scores.py and scripts/voi_priors.py on the fixture records."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(__file__)
FIXTURE = os.path.join(HERE, "fixtures", "records_small.jsonl")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))


def _run(module, argv, monkeypatch):
    monkeypatch.setattr(sys, "argv", [module.__name__] + argv)
    module.main()


def test_voi_scores_writes_config_then_one_row_per_retained_record(tmp_path, monkeypatch):
    import voi_scores
    out = tmp_path / "v.jsonl"
    _run(voi_scores, ["--sweep", FIXTURE, "--out", str(out), "--levels", "mid", "--procs", "1"], monkeypatch)
    lines = [json.loads(x) for x in open(out)]
    retained = sum(1 for x in open(FIXTURE) if json.loads(x).get("retained"))
    assert set(lines[0]) == {"config"} and lines[0]["config"]["priors"]["null"] == 1.0
    rows = lines[1:]
    assert len(rows) == retained
    assert set(rows[0]["levels"]["mid"]["voi"]) == {"roi", "depth", "collision"}


def test_priors_use_train_seeds_only(tmp_path, monkeypatch):
    import voi_priors
    seeds = sorted({json.loads(x)["seed"] for x in open(FIXTURE)})
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps(dict(splits=dict(train=[], val=seeds, test=[]))))
    with pytest.raises(SystemExit, match="no train records"):
        _run(voi_priors, ["--sweep", FIXTURE, "--manifest", str(man), "--out", str(tmp_path / "p.json")], monkeypatch)


def test_priors_are_rates_between_zero_and_one(tmp_path, monkeypatch):
    import voi_priors
    seeds = sorted({json.loads(x)["seed"] for x in open(FIXTURE)})
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps(dict(splits=dict(train=seeds, val=[], test=[]))))
    out = tmp_path / "p.json"
    _run(voi_priors, ["--sweep", FIXTURE, "--manifest", str(man), "--out", str(out)], monkeypatch)
    p = json.load(open(out))
    assert p["priors"]["null"] == 1.0 and p["priors"]["depth"] == 1.0
    assert all(0.0 <= p["priors"][c] <= 1.0 for c in ("occl_static", "occl_ped", "light", "rear"))
    assert p["counts"]["occl_static"]["n"] > 0
