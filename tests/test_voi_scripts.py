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


def _occl_weight(rec, priors):
    from cassvla.planning import tools as T
    from cassvla.planning.voi import weighted_worlds
    total = 0.0
    for w, world in weighted_worlds(rec, T.base_observation(rec), priors):
        if any(a["name"] == "hyp" and not any(a["velocity"]) for a in world["actors"]):
            total += w
    return total


def test_vlm_prior_sets_occlusion_weights():
    from cassvla.planning.voi import UNIFORM
    from voi_scores import priors_for
    rec = next(json.loads(x) for x in open(FIXTURE) if json.loads(x)["family"] == "occluded_pedestrian")
    ws = [_occl_weight(rec, priors_for(UNIFORM, p)) for p in (0.0, 0.25, 0.5, 1.0)]
    assert ws[0] == 0.0
    assert ws[1] < ws[2] < ws[3]


def test_vlm_prior_requires_every_row(tmp_path, monkeypatch):
    import voi_scores
    from cassvla.perception.frames import frame_key
    recs = [json.loads(x) for x in open(FIXTURE) if json.loads(x).get("retained")]
    yn = tmp_path / "yn.jsonl"
    with open(yn, "w") as f:
        f.write(json.dumps(dict(header=dict(questions_hash="x"))) + "\n")
        for r in recs[1:]:
            f.write(json.dumps(dict(key=frame_key(r["family"], r["seed"], r["t_dec"]), p=dict(hidden=0.5))) + "\n")
    with pytest.raises(SystemExit, match=f"1 of {len(recs)}"):
        _run(voi_scores, ["--sweep", FIXTURE, "--out", str(tmp_path / "v.jsonl"), "--levels", "mid", "--procs", "1", "--vlm-yesno", str(yn)], monkeypatch)


def test_voi_scores_keeps_only_the_chosen_splits(tmp_path, monkeypatch):
    import voi_scores
    recs = [json.loads(x) for x in open(FIXTURE) if json.loads(x).get("retained")]
    seeds = sorted({r["seed"] for r in recs})
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps(dict(splits=dict(train=seeds[1:], val=seeds[:1], test=[]))))
    out = tmp_path / "v.jsonl"
    _run(voi_scores, ["--sweep", FIXTURE, "--out", str(out), "--levels", "mid", "--procs", "1", "--manifest", str(man), "--splits", "val"], monkeypatch)
    rows = [json.loads(x) for x in open(out)][1:]
    assert rows and {r["seed"] for r in rows} == {seeds[0]}
