# Why a small on-device VLM cannot choose the perception tool

This page diagnoses the prompted-VLM selector from Phase 5. The VLM is Qwen2.5-VL-3B-Instruct (4-bit, through mlx)
running on an Apple Silicon Mac. It sees one front-camera frame per decision and is asked which single query
(`roi`, `depth`, `collision` or `none`) the planner should make. Every number below comes from
`scripts/vlm_probe.py` output: `out/vlm_probe/report.json` (float32 vision tower) and
`out/vlm_probe/report_fp16.json` (the original float16 cache). Both cover the 1,018 decision frames of the dev
sweep, seeds 100-119.

## Result

The prompted selector carries no information about the decision. The model sees the scene but does not use what
it sees when it fills in the answer, and it cannot reason about which tool would help. There are four separate
causes; the fourth was a bug and is fixed.

| | float16 cache | float32 cache |
|---|---|---|
| Distinct replies over 1,018 frames | 7 | 5 |
| `query` answers | `none` 1,018 times | `none` 1,018 times |
| `occlusion: true` | 0 | 0 |
| Replies that copy the template `roi\|depth\|collision\|none` verbatim | 4 | 4 |
| `!!!!` replies (NaN in the vision tower) | 11 | 0 |
| NaN embeddings | 11 | 0 |
| Light read correctly, frames with a light | 0.886 | 0.925 (281 frames) |
| Frames with no light answered "green" | 737 of 737 | 737 of 737 |

## 1. The model fills in the template instead of reading the scene

The prompt showed the answer format inline: `"light": "green|yellow|red|none|unknown"`,
`"query": "roi|depth|collision|none"` and `"hazards": ["short phrase", ...]`. The model copied it.

- 4 replies return `"query": "roi|depth|collision|none"` verbatim.
- On all 737 frames from families without a traffic light, `light` is "green", the first listed option. The
  correct option, "none", is never chosen.
- `hazards` is `["none"]` or `["no hazards"]` on every frame.

## 2. It perceives the scene but does not pass that into its answer

`occluded_pedestrian/100_2.0` holds a parked red car with a pedestrian next to it. The oracle's best maneuver is
`change_left`, and 3 of the 6 candidates are unsafe. The same model, on the same frame, with different prompts:

| Prompt variant | Reply (start) |
|---|---|
| `describe`: list every vehicle and pedestrian | "there is one vehicle and one pedestrian visible" |
| `ped`: is there a pedestrian? yes/no | "No, there is no pedestrian in the image." |
| `occl`: is anything blocking the view? | "No, there is no object blocking the view of the road ahead." |
| `noschema`: list hazards, then pick a query | lists "a person standing on the right side of the road" as a hazard, then picks **none** |
| `orig` (the cached prompt) | `{"hazards": ["none"], "occlusion": false, "light": "green", "query": "none"}` |

The free-text yes/no answers lean to "No" even when the description contains the object. Section 5 shows the
first-token probabilities do carry the signal.

## 3. Choosing a tool is beyond it, whatever the wording

The `forced` variant removes `none` from the options. On the 8 probe frames the answer becomes `depth` on 6
(occluded pedestrian, lane blockage, lead brake) and `roi` on both traffic-light frames, with no hazards listed in
any of them. The constant answer moves from `none` to `depth`; it does not depend on the scene. Picking a tool
needs counterfactual reasoning about simulator tools (for example, that ROI can report occluded objects), which a
3B model does not do from a text description.

For comparison, Max's Qwen3.5-9B run on an A100 (`docs/phase5_vlm.md`) called a tool on 8% of decisions and reached
0.261 at mid noise against 0.250 for no tool. A model three times larger is still weak at this task.

## 4. The float16 vision tower overflowed (fixed)

The 4-bit checkpoint runs its vision tower in float16. On 11 `occluded_cross_traffic` frames at t = 7.5-8.0 s (close
to the intersection, a large flat road surface) it overflowed to NaN. The language model then emitted token id 0
(`!`) repeatedly, `parse_answer` turned that into `query="none"`, and the NaN embeddings made the PCA fit fail
(`SVD did not converge`). The vision tower now runs in float32 (`MLXBackend.__init__`), `cache_frames` raises on a
non-finite embedding, and a cache records `vision_dtype` and refuses to mix dtypes. The earlier dev evaluation
`out/eval_dev_vlm` used a partial cache and should be ignored. `out/eval_dev_vlm_fp32` replaces it.

## 5. What the VLM is good for instead

Narrow yes/no questions scored by the probability of "Yes" against "No" in the first answer token avoid causes 1
and 2. On the same frame, "Is there a pedestrian in this image?" puts 27.0 on "Yes" and 26.0 on "No" in the logits,
even though the free-text answer is "No". `scripts/eval_vlm_yesno.py` measures these probabilities as detectors
(AUROC) on validation and test, and `voi_vlm` uses P(hidden road user) as the occlusion prior of the VoI selector.
Results are in `docs/voi_selector.md`.

## On-device cost (Apple Silicon Mac, a sweep running alongside)

From `out/vlm_dev_fp32/profile.json` and `out/vlm_dev/profile.json`:

| Step | float16 | float32 |
|---|---|---|
| Embedding (vision tower, mean-pooled) | 0.331 s | 0.396 s |
| Prompted answer (up to 120 tokens) | 1.258 s | 1.655 s |
| Peak memory | 3.8 GB | 5.7 GB |

## Reproduce

```bash
.venv/bin/python scripts/cache_vlm.py --frames out/frames_dev --records out/sweep_dev --out out/vlm_dev_fp32
.venv/bin/python scripts/vlm_probe.py --cache out/vlm_dev_fp32 --sweep out/sweep_dev --frames out/frames_dev \
  --variants orig describe ped occl noschema forced --keys occluded_pedestrian/100_2.0 occluded_pedestrian/101_1.5 \
  lane_blockage/100_2.0 lane_blockage/101_2.0 lead_brake_cutin/100_11.0 lead_brake_cutin/100_6.0 \
  ambiguous_light/100_3.5 ambiguous_light/101_5.5 --out out/vlm_probe/report.json
```
