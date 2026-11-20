# Counterfactual value-of-information selector

Eshan's contribution: a training-free tool selector that decides which single perception query to make by reasoning
about what each tool could reveal, compared head to head with Max's learned selector (`signed`). Code:
`cassvla/planning/hypotheses.py`, `cassvla/planning/voi.py`, `scripts/voi_scores.py`, `scripts/voi_priors.py`,
`scripts/eval_voi.py`, `scripts/voi_figures.py`. Every number below is read from `out/voi_eval/*.json` by the script
that generated this page section; the full tables are in `research/2026-11-20_voi_selector/`.

## Result

The pre-registered final test (seeds 1160-1259, never seen before, 4,557 decisions, run once) is negative. The VoI
selector is 0.08 to 0.10 below the learned selector at every noise level and level with the ranker-margin
baseline. All three registered hypotheses fail; the VLM variant (V4) did not run on the final seeds.

| Final split, mean accuracy over budgets 0-1 | Low | Mid | High |
|---|---|---|---|
| Learned selector `signed` (Max) | 0.495 | 0.435 | 0.364 |
| VoI, abstains at VoI <= 0 | 0.397 | 0.345 | 0.288 |
| VoI, budget only | 0.399 | 0.347 | 0.288 |
| Ranker margin | 0.400 | 0.345 | 0.280 |
| Always-on (3 calls) | 0.577 | 0.472 | 0.346 |

| Final split, paired difference [95% seed-bootstrap CI] | Low | Mid | High |
|---|---|---|---|
| VoI - learned selector (V1 needs lower bound > -0.01) | -0.098 [-0.107, -0.088] | -0.090 [-0.099, -0.081] | -0.076 [-0.085, -0.066] |
| VoI - ranker margin (V2 needs lower bound > 0) | -0.003 [-0.014, +0.009] | -0.000 [-0.010, +0.010] | +0.008 [-0.003, +0.018] |

![Accuracy against calls per decision on the final split](../paper/figures/voi_pareto_acc.pdf)

VoI is better than the ranker margin when calls are scarce and worse when they are plentiful:

| Final split, accuracy at a fixed budget | Low | Mid | High |
|---|---|---|---|
| VoI at 0.1 calls/decision | 0.270 | 0.259 | 0.247 |
| Ranker margin at 0.1 calls/decision | 0.239 | 0.225 | 0.213 |
| VoI at 0.3 calls/decision | 0.344 | 0.307 | 0.270 |
| Ranker margin at 0.3 calls/decision | 0.325 | 0.290 | 0.248 |
| VoI at 1.0 calls/decision | 0.509 | 0.415 | 0.318 |
| Ranker margin at 1.0 calls/decision | 0.557 | 0.454 | 0.332 |

Validation and test (seeds 100-399, `out/voi_eval/valtest.json`) show the same picture:

| Mean accuracy | Val low | Val mid | Val high | Test low | Test mid | Test high |
|---|---|---|---|---|---|---|
| Learned selector `signed` (Max) | 0.507 | 0.449 | 0.376 | 0.470 | 0.406 | 0.341 |
| VoI, abstains at VoI <= 0 | 0.398 | 0.351 | 0.306 | 0.365 | 0.318 | 0.263 |
| Ranker margin | 0.404 | 0.359 | 0.284 | 0.373 | 0.316 | 0.250 |
| Always-on (3 calls) | 0.577 | 0.483 | 0.341 | 0.560 | 0.440 | 0.329 |

## Method

For one decision the selector weighs world hypotheses built from the base observation only. Every world is a
measurement-noise draw of the visible actors (8 draws, the base camera's noise model), and some worlds add one hidden
event on top: a stopped vehicle or a pedestrian at an occluded point on a candidate path, an unread light set to red
or green, or a fast car behind. Each tool is run on a pseudo-record in which that world is the truth, the ranker
reranks the candidates on the merged belief, and the tool's value is the expected gain in the ranker's own utility
(score, minus 200 when unsafe) over not calling it. The decision calls the best tool only when its value is above 0.
No hidden actor, `c_star`, oracle metric or true light state is read; a test enforces this.

Class priors were fitted on the 10,329 training decisions as event rates: occluded vehicle 0.0143, occluded pedestrian 0.1021, unread light not green 0.4147, car behind 0.0.

## Ablations (validation)

| Variant - reference (uniform priors), mean accuracy | Low | Mid | High |
|---|---|---|---|
| reference_budget | +0.002 [+0.001, +0.002] | +0.001 [+0.001, +0.002] | +0.000 [-0.001, +0.001] |
| fitted_priors | +0.018 [+0.008, +0.027] | +0.006 [-0.004, +0.016] | +0.018 [+0.006, +0.029] |
| alternatives_uniform | +0.005 [-0.002, +0.013] | -0.007 [-0.018, +0.004] | -0.003 [-0.015, +0.007] |
| draws4 | +0.004 [-0.002, +0.010] | -0.005 [-0.013, +0.003] | -0.003 [-0.013, +0.007] |
| draws16 | +0.007 [+0.001, +0.013] | +0.000 [-0.008, +0.009] | +0.001 [-0.008, +0.010] |
| no_depth | -0.003 [-0.012, +0.005] | -0.012 [-0.022, -0.003] | -0.007 [-0.021, +0.007] |
| no_occl_static | +0.005 [-0.002, +0.012] | +0.004 [-0.004, +0.013] | +0.003 [-0.008, +0.013] |
| no_occl_ped | +0.005 [-0.000, +0.011] | -0.006 [-0.013, +0.000] | +0.001 [-0.008, +0.010] |
| no_light | -0.006 [-0.012, -0.002] | -0.008 [-0.013, -0.003] | -0.008 [-0.014, -0.003] |
| no_rear | +0.008 [+0.003, +0.013] | +0.004 [-0.004, +0.011] | +0.010 [+0.002, +0.018] |
| noise_unaware | +0.011 [+0.005, +0.018] | +0.000 [+0.000, +0.000] | +0.008 [-0.004, +0.018] |

Fitted priors help most. Removing the measurement-noise draws or the light hypotheses hurts. The imaginary car
behind never occurs in the data and removing it helps; fitted priors give it weight 0. A first design that treated the
noise-free base estimate as a world of its own (`alternatives_uniform`) was no better and was replaced, on validation,
before the final test.

## Why it falls short (diagnosis)

- VoI optimises the ranker's own utility, but the label is agreement with the oracle's `c*`, which re-simulates
  reactive hazards. The base ranker is right on only 24% of validation decisions, and with all tools at zero noise it
  recovers `c*` on 63.6% (`docs/baseline_results.md`). A world model built on the ranker inherits that mismatch; the
  learned selector is trained on real outcomes and absorbs it.
- On validation at mid noise VoI's score separates decisions where some tool helps from those where none does with
  AUROC 0.61 (ranker margin: 0.56), but its per-tool rank correlation with the true expected gain is only 0.15-0.19,
  and its tool choice is optimal on 38% of helped decisions against 50% for the learned selector (`valtest.json`).
- VoI's calls are harmful (negative expected gain) on 13% of calls at budget 0.3, against 1.5% for the learned selector.

## Cost on this Mac

| Step | Seconds |
|---|---|
| Learned selector (MLP forward pass) | 2e-06 |
| VoI selector (per decision, per noise level) | 0.0574 |
| VLM embedding (float32) | 0.396 |
| VLM prompted answer (float32) | 1.66 |

VoI needs no training and no labels but costs about 0.06 s per decision per noise level (about 100 ranker calls),
against microseconds for the learned selector's forward pass.

## Reproduce

```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_priors.py --sweep out/v2_sweep --manifest out/v2_dataset/manifest.json --out out/voi/priors_fitted.json
OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep out/v5_sweep --out out/voi/v5_final.jsonl --priors out/voi/priors_fitted.json --procs 8
OMP_NUM_THREADS=1 .venv/bin/python scripts/eval_voi.py --voi voi=out/voi/v5_final.jsonl --methods voi voi_budget signed uncertainty_margin always_on \
  --test-dir v5_final_ds --test-expgain v5_final_expgain.jsonl --splits final --out out/voi_eval/final.json
```
