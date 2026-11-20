"""Analysis functions behind docs/vlm_failure_analysis.md (no model needed)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

ROW = '{{"hazards": ["none"], "occlusion": false, "light": "{}", "query": "{}"}}'


def _row(key, light="green", query="none", raw=None):
    return dict(key=key, raw=raw or ROW.format(light, query), light=light, query=query, occlusion=False, hazards=["none"], parse_error=False)


def test_summarize_counts_template_copies():
    from vlm_probe import summarize_replies
    rows = [_row("a/1_1.0"), _row("a/1_1.5"), _row("b/2_1.0", raw='{"hazards": ["none"], "occlusion": false, "light": "green", "query": "roi|depth|collision|none"}'),
            _row("b/2_1.5", raw="!!!!!!!!")]
    s = summarize_replies(rows)
    assert s["n"] == 4 and s["distinct_replies"] == 3
    assert s["template_copies"] == 1 and s["bang_replies"] == 1
    assert s["query_counts"] == {"none": 4}


def test_light_confusion_uses_ego_status():
    from vlm_probe import light_confusion
    rows = [_row("ambiguous_light/5_2.0", light="green"), _row("ambiguous_light/5_2.5", light="red"), _row("lane_blockage/5_2.0", light="green")]
    records = [dict(family="ambiguous_light", seed=5, t_dec=2.0, signals=dict(ego_status="TRAFFIC_LIGHT_RED")),
               dict(family="ambiguous_light", seed=5, t_dec=2.5, signals=dict(ego_status="TRAFFIC_LIGHT_RED")),
               dict(family="lane_blockage", seed=5, t_dec=2.0, signals=dict(ego_status=None)),
               dict(family="lane_blockage", seed=5, t_dec=9.0, skipped="episode ended")]          # sweep lines without signals
    c = light_confusion(rows, records)
    assert c["confusion"] == {"TRAFFIC_LIGHT_RED -> green": 1, "TRAFFIC_LIGHT_RED -> red": 1}
    assert c["accuracy"] == 0.5
    assert c["no_light_families"] == {"n": 1, "answered_green": 1}
