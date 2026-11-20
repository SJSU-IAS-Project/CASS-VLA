"""Phase 5 checks for the VLM cache that need no model: prompt, parser and cache bookkeeping."""
import json
import os

import numpy as np
import pytest

from cassvla.perception.vlm import (PROMPT, build_prompt, cache_frames, describe_candidates, load_cache, parse_answer,
                                    summarize_timings)


def test_prompt_lists_candidates_and_hides_oracle_information():
    text = build_prompt(7.25, ["keep", "stop", "change_left"])
    assert "7.2 m/s" in text or "7.3 m/s" in text
    assert "- stop: brake to a stop in the lane" in text
    assert "keep_fast" not in text
    # the only per-decision inputs are speed and maneuver names; no safety flags, c* or scores
    assert text == PROMPT.format(speed=7.25, candidates=describe_candidates(["keep", "stop", "change_left"]))
    for leak in ("unsafe", "c_star", "oracle", "score"):
        assert leak not in text.lower()


def test_describe_unknown_maneuver_falls_back_to_name():
    assert describe_candidates(["u_turn"]) == "- u_turn: u turn"


@pytest.mark.parametrize("text, query, light, occl, err", [
    ('{"hazards": ["parked car"], "occlusion": true, "light": "none", "query": "roi"}', "roi", "none", True, False),
    ('```json\n{"hazards": [], "occlusion": "yes", "light": "RED", "query": "Depth"}\n```', "depth", "red", True, False),
    ('Sure! {"hazards": "pedestrian", "occlusion": false, "light": "purple", "query": "collision."}', "collision", "unknown", False, False),
    ('{"hazards": [], "occlusion": false, "light": "green", "query": "lidar"}', "none", "green", False, True),
    ("I cannot see anything.", "none", "unknown", False, True),
    ('{"hazards": [', "none", "unknown", False, True),
])
def test_parse_answer(text, query, light, occl, err):
    out = parse_answer(text)
    assert (out["query"], out["light"], out["occlusion"], out["parse_error"]) == (query, light, occl, err)
    assert isinstance(out["hazards"], list)


def test_parse_answer_wraps_single_hazard_string():
    assert parse_answer('{"hazards": "pedestrian", "query": "roi"}')["hazards"] == ["pedestrian"]


class FakeBackend:
    model_id, revision = "fake", "0"

    def __init__(self):
        self.calls = []

    def embed(self, path):
        self.calls.append(("embed", path))
        return np.full(4, len(self.calls), np.float32), dict(seconds=0.1)

    def ask(self, path, text):
        self.calls.append(("ask", path))
        return '{"hazards": [], "occlusion": false, "light": "none", "query": "depth"}', dict(seconds=1.0)


def _frames(n):
    return [dict(key=f"fam/{i}_1.0", path=f"fam/{i}_1.0.png", speed=5.0, candidates=["keep", "stop"]) for i in range(n)]


def test_cache_round_trip_and_resume(tmp_path, monkeypatch):
    monkeypatch.setattr("cassvla.perception.vlm.SHARD_SIZE", 2)
    out = str(tmp_path / "vlm")
    be = FakeBackend()
    t1 = cache_frames(_frames(3), "frames", be, out, log=None)
    assert len(t1) == 3 and len(be.calls) == 6
    cache = load_cache(out)
    assert cache["keys"] == [f"fam/{i}_1.0" for i in range(3)]
    assert cache["emb"].shape == (3, 4)
    assert set(cache["prompted"]) == set(cache["keys"]) and cache["prompted"]["fam/0_1.0"]["query"] == "depth"
    assert cache["meta"]["model"] == "fake"

    be2 = FakeBackend()
    t2 = cache_frames(_frames(5), "frames", be2, out, log=None)    # only the two new frames run
    assert len(t2) == 2 and [p for _, p in be2.calls] == ["frames/fam/3_1.0.png"] * 2 + ["frames/fam/4_1.0.png"] * 2
    assert load_cache(out)["emb"].shape == (5, 4)


def test_cache_refuses_a_different_prompt_or_model(tmp_path):
    out = str(tmp_path / "vlm")
    cache_frames(_frames(1), "frames", FakeBackend(), out, log=None)
    meta = json.load(open(os.path.join(out, "meta.json")))
    meta["prompt_hash"] = "other"
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
    with pytest.raises(ValueError, match="prompt_hash"):
        cache_frames(_frames(2), "frames", FakeBackend(), out, log=None)


def test_summarize_timings():
    s = summarize_timings([dict(embed=dict(seconds=0.2), ask=dict(seconds=2.0)), dict(embed=dict(seconds=0.4))], 3.5)
    assert s["embed"]["n"] == 2 and s["embed"]["mean_s"] == pytest.approx(0.3) and s["ask"]["n"] == 1
    assert s["peak_memory_gb"] == 3.5


def test_prompt_template_formats():
    assert "{" in PROMPT and build_prompt(0, []).count("{") == 1


class NaNBackend(FakeBackend):
    def embed(self, path):
        self.calls.append(("embed", path))
        return np.full(4, np.nan, np.float32), dict(seconds=0.1)


def test_cache_rejects_non_finite_embedding(tmp_path):
    out = str(tmp_path / "vlm")
    with pytest.raises(ValueError, match="non-finite embedding for fam/0_1.0"):
        cache_frames(_frames(1), "frames", NaNBackend(), out, log=None)
    assert not [f for f in os.listdir(out) if f.startswith("emb_")]
    assert load_cache(out)["prompted"] == {}


class FP32Backend(FakeBackend):
    vision_dtype = "float32"


def test_cache_refuses_mixed_vision_dtype(tmp_path):
    out = str(tmp_path / "vlm")
    cache_frames(_frames(1), "frames", FP32Backend(), out, log=None)
    assert json.load(open(os.path.join(out, "meta.json")))["vision_dtype"] == "float32"
    meta = json.load(open(os.path.join(out, "meta.json")))
    meta["vision_dtype"] = "float16"
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
    with pytest.raises(ValueError, match="vision_dtype"):
        cache_frames(_frames(2), "frames", FP32Backend(), out, log=None)


def test_yes_prob_rejects_nan():
    from cassvla.perception.vlm import yes_probability
    with pytest.raises(ValueError, match="non-finite"):
        yes_probability(np.array([np.nan, 1.0, 2.0]), yes_ids=[1], no_ids=[2])


def test_yes_probability_is_softmax_over_yes_and_no():
    from cassvla.perception.vlm import yes_probability
    logits = np.array([5.0, 2.0, 0.0, 9.0])               # token 3 (not yes/no) must be ignored
    assert yes_probability(logits, yes_ids=[1], no_ids=[2]) == pytest.approx(np.exp(2) / (np.exp(2) + 1))
    assert yes_probability(logits, yes_ids=[1, 0], no_ids=[2]) == pytest.approx((np.exp(2) + np.exp(5)) / (np.exp(2) + np.exp(5) + 1))


class YesNoBackend(FakeBackend):
    def yes_prob(self, path, question):
        self.calls.append(("yes", path))
        return 0.25


def test_cache_yesno_resumes(tmp_path):
    from cassvla.perception.vlm import QUESTIONS, cache_yesno
    out = str(tmp_path / "yesno.jsonl")
    be = YesNoBackend()
    cache_yesno(_frames(2), "frames", be, out, log=None)
    assert len(be.calls) == 2 * len(QUESTIONS)
    rows = [json.loads(x) for x in open(out)]
    assert "questions_hash" in rows[0]["header"] and rows[1]["p"] == {q: 0.25 for q in QUESTIONS}
    be2 = YesNoBackend()
    cache_yesno(_frames(2), "frames", be2, out, log=None)
    assert be2.calls == []


def test_yesno_profile_path_never_overwrites_the_cache():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cache_vlm", os.path.join(os.path.dirname(__file__), "..", "scripts", "cache_vlm.py"))
    cv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cv)
    assert cv.profile_path("out/vlm_yesno/v5.jsonl") == "out/vlm_yesno/v5_profile.json"
    assert cv.profile_path("out/vlm_yesno/v5") == "out/vlm_yesno/v5_profile.json"
