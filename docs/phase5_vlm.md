# Phase 5: cached VLM features

This page reports the first offline VLM pass from [`refined_proposal.md`](refined_proposal.md). It follows
[`baseline_results.md`](baseline_results.md), whose fair ceiling and expected-gain targets it uses. That page also
holds the comparison with simple call triggers, which come from `scripts/eval_triggers.py`.

## Result

Adding cached VLM features to the geometry selector raised its accuracy in all 6 validation and test cells, by
0.003 to 0.007. That met the decision rule, which was fixed before the features existed. The gain was positive for
every one of the 3 training seeds in every cell. It closes 7% to 20% of the gap to the fair ceiling, so most of
that gap remains.

| Split | Tool noise | Scene-only MLP | VLM-only MLP | Geometry selector | Geometry + VLM | Fair ceiling |
|---|---|---|---|---|---|---|
| Validation | Low | 0.497 | 0.504 | 0.515 | 0.522 | 0.553 |
| Validation | Mid | 0.433 | 0.434 | 0.450 | 0.453 | 0.493 |
| Validation | High | 0.342 | 0.345 | 0.368 | 0.374 | 0.398 |
| Test | Low | 0.456 | 0.467 | 0.481 | 0.485 | 0.513 |
| Test | Mid | 0.379 | 0.391 | 0.407 | 0.413 | 0.441 |
| Test | High | 0.309 | 0.311 | 0.333 | 0.339 | 0.365 |

These are averages over budgets from 0 to 1 call per decision, over 3 training seeds, with expected-gain targets
and the 210 main training seeds. The VLM-only MLP sees the VLM features plus the ranker margin. It does about as
well as the scene-only MLP, which sees hand-made scene features, so the frame alone carries about as much as those
features.

## Prompted variant

The second variant from the proposal asks the VLM which tool it would call, given the frame, the candidate names
and the planner's pick. It called a tool on only 8% of decisions: `roi` 167 times and `collision` 16 times out of
2,222 on validation, and `depth` never. At that call rate it reached 0.261 on validation at mid noise. No tool gives
0.250, and the geometry + VLM selector reaches 0.323 at 0.1 calls. Test gives the same picture.

## Setup

- Model: Qwen3.5-9B, bf16, temperature 0, thinking off, on one A100 40 GB of the SJSU cluster.
- Frames: one 640x360 front-camera frame per decision, 220 image tokens each. All 17,695 frames of the main
  dataset and 14,707 of seeds 460-759 were rendered with headless EGL. Each one is within 5 mm of the recorded
  ego position.
- VLM features: the mean of the image-token states at the middle layer. A PCA fitted on the training split
  reduces it to 32 dimensions.
- The final split (seeds 400-459) has frames and features but was not used.

Run it with `scripts/vlm_encode.py` (cluster job `scripts/hpc/vlm.sbatch`) and evaluate with:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/eval_vlm.py --data out/v2_dataset --embed out/vlm_main/embed.npz --expgain out/v2_expgain.jsonl --prompt out/vlm_main/prompt_val.jsonl out/vlm_main/prompt_test.jsonl --out out/v2_eval/vlm.json
```

## Training on the extra seeds

This check was exploratory. It was not pre-registered, and it was run after the first result was known. It repeats the
evaluation with the 14,707 extra decisions from seeds 460-759 added to the training split. The selectors then train on
25,036 rows instead of 10,329. Validation and test are unchanged. The results are in `out/v2_eval/vlm_extra_train.json`,
next to `out/v2_eval/vlm.json`.

| Split | Tool noise | Geometry, 10,329 rows | Geometry + VLM, 10,329 rows | Geometry, 25,036 rows | Geometry + VLM, 25,036 rows | Fair ceiling |
|---|---|---|---|---|---|---|
| Validation | Low | 0.515 | 0.522 | 0.517 | 0.526 | 0.553 |
| Validation | Mid | 0.450 | 0.453 | 0.454 | 0.459 | 0.493 |
| Validation | High | 0.368 | 0.374 | 0.368 | 0.374 | 0.398 |
| Test | Low | 0.481 | 0.485 | 0.481 | 0.487 | 0.513 |
| Test | Mid | 0.407 | 0.413 | 0.407 | 0.416 | 0.441 |
| Test | High | 0.333 | 0.339 | 0.333 | 0.343 | 0.365 |

- With more data, the VLM gain rose in five of the six cells and stayed at +0.006 in validation at high noise. It
  moved from a range of +0.003 to +0.007 to a range of +0.005 to +0.010.
- The gain was positive for all 3 training seeds in every cell, and the decision rule was met again.
- The features now close 13% to 31% of the gap to the fair ceiling, against 7% to 20% before.
- The geometry-only selector barely changed, by at most 0.005 in any cell. The extra data helps the VLM features and
  not the geometry features.
- Geometry + VLM reaches 0.416 on test at mid noise, which is 0.025 below the fair ceiling.

## Controls

These controls ask how much of the VLM gain comes from the image content. They also ask how much comes from knowing
the scene family of a decision. They are exploratory. They were not pre-registered, they use the same 25,036-row training set
as the extra-train run, and they have no confidence intervals. Each cell is one run of 3 training seeds. The numbers
are mean accuracy over budgets from 0 to 1, from `out/v2_eval/vlm_extra_train.json` and
`out/v2_eval/vlm_control_{shuffle,shuffle_family,family}.json`.

The four runs differ only in the 32 VLM dimensions given to the selector:

- Real: the features from the frame.
- Shuffle: the features permuted across all rows of the training split.
- Shuffle within family: the features permuted among rows of the same scene family.
- Family: the features replaced by a one-hot code of the scene family.

Each cell shows the gain of geometry + VLM over the geometry selector, whose accuracy is the same in every run.

| Split | Tool noise | Geometry | Real | Shuffle | Shuffle within family | Family |
|---|---|---|---|---|---|---|
| Validation | Low | 0.5166 | +0.0099 | -0.0041 | +0.0014 | +0.0058 |
| Validation | Mid | 0.4543 | +0.0050 | -0.0022 | +0.0009 | +0.0010 |
| Validation | High | 0.3683 | +0.0060 | -0.0005 | +0.0008 | +0.0022 |
| Test | Low | 0.4808 | +0.0066 | -0.0018 | -0.0007 | +0.0051 |
| Test | Mid | 0.4073 | +0.0086 | -0.0039 | +0.0010 | +0.0032 |
| Test | High | 0.3325 | +0.0100 | +0.0001 | +0.0047 | +0.0051 |

- Full shuffling removes the gain. Geometry + VLM is at or below geometry in 5 of the 6 cells, and +0.0001 in the
  sixth. So the gain does not come from the extra input dimensions or from the extra capacity.
- A family code alone recovers part of the gain. In each cell it gives 20% to 77% of the real gain, and 49% over all six
  cells together (+0.0224 against +0.0461 summed). The largest shares are on test at low noise (77%) and validation at low
  noise (59%), and the smallest is validation at mid noise (20%).
- Shuffling within a family keeps little: at most +0.0014 in five cells, and +0.0047 on test at high noise. The family
  identity inside the features explains little of the gain, and the rest depends on the frame.
- About half of the real gain is information beyond the scene family. By cell, the share is between 23% and 80%. With one run per cell and no intervals, the individual shares are rough.
- The decision rule from the first result was not met by the shuffled runs (`decision_rule_met` is false in both
  shuffle files), and it was met by the family run.

## Pre-registered check with the abstain selector

The second pre-registered final test (seeds 1060-1159, 4,922 decisions) included one VLM hypothesis, Q1. It asks
whether the abstain selector `signed` does better with the 32 VLM dimensions than without them. The features come from
the same encoder and the same PCA recipe as above, with the PCA fitted on the training rows only. Both models train on
the 34,718 rows of the first final test. The results are in `out/v4_eval/final_vlm.json`, and the full test is in
[`baseline_results.md`](baseline_results.md).

| Tool noise | `signed` | `signed` + VLM | Difference (95% interval) |
|---|---|---|---|
| Low | 0.500 | 0.516 | +0.016 (0.013 to 0.020) |
| Mid | 0.447 | 0.459 | +0.012 (0.008 to 0.015) |
| High | 0.375 | 0.385 | +0.010 (0.007 to 0.013) |

Q1 holds at all three levels. At 0.6 calls per decision, the VLM features raise accuracy by 0.016, 0.012 and 0.012
and lower the unsafe rate by 0.012, 0.004 and 0.003, at low, mid and high noise. The shuffle and family controls above were run on the earlier
selector and were not repeated on `signed`, so this result does not say how much of the gain is scene-family
identity.

## Not yet tried

- Other layers, the last-token state, or more than 32 PCA dimensions. These were not tuned, so the numbers above
  use the first setting that was chosen.
- Using the scene descriptions as features.
