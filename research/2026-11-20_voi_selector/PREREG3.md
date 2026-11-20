# Pre-registration 3: the VoI selector against the learned selector

Written on 2026-11-20, before seeds 1160-1259 were swept. Those seeds have never been generated, labelled or looked
at. The final run happens once, with the settings below, and every outcome is reported as it comes out.

## Data

- Test: seeds 1160-1259 (100 seeds, all six families), swept with `scripts/run_sweep.py`, built with
  `build_dataset.py --as-split final` into `out/v5_final_ds`, expected-gain labels in `out/v5_final_expgain.jsonl`
  (8 draws).
- Training for the learned selectors, as in PREREG2: `out/v2_dataset`, `out/v2_extra_ds` and `out/v3_extra_ds`
  train rows with their expected-gain labels. VoI trains nothing; its fitted priors come from the 10,329 `v2_dataset`
  train decisions (`out/voi/priors_fitted.json`).

## Methods (frozen in `FROZEN.json`)

- **`voi`** (primary): compositional world model (every world is a measurement-noise draw of the visible actors,
  with at most one hidden event on top), fitted priors, 8 draws, all classes, tool answers simulated at the
  evaluated noise level. A call is made inside the budget only when the best VoI is above 0.
- **`voi_budget`**: the same scores without abstention.
- **`voi_vlm`** (secondary): `voi` with the occlusion priors set per decision from the VLM's P(Yes) to "Is part of
  the road ahead hidden behind a parked or stopped vehicle, so that a pedestrian or a car could be behind it?"
  (Qwen2.5-VL-3B-Instruct-4bit, float32 vision tower): occl_static = occl_ped = P / 2. It pays one VLM call per
  decision, reported as `cost_offset` 1.
- **`signed`**: Max's `signed_mse_abstain` on the plandiscrim features, 3 init seeds, unchanged harness
  (`research/2026-11-19_learned_selector/run2/experiments/final.py`).
- **`uncertainty_margin`**, **`always_on`**: as in PREREG2.

All methods are scored by `scripts/eval_voi.py`, which uses the harness's evaluation, budgets 0 to 1 call per decision
in steps of 0.05, and the paired seed bootstrap over scenario seeds with 1,000 resamples.

## Hypotheses

- **V1 (primary):** `voi` is non-inferior to `signed` on mean accuracy over budgets. The lower bound of the 95% CI of
  `voi - signed` is above -0.01 at low, mid and high noise.
- **V2:** `voi` beats `uncertainty_margin` at all three levels, with the CI above 0.
- **V3:** at its own call rate (lambda = 0, no budget cap), `voi` is non-inferior to `always_on` in accuracy (CI lower
  bound above -0.01) and no less safe (unsafe-rate difference CI upper bound below +0.01), at all three levels.
- **V4 (secondary, runs only if every final decision has a yes/no answer):** `voi_vlm` beats `voi` at all three
  levels with the CI above 0, at equal tool budget.

## What validation already showed (seeds 100-399, `out/voi_eval/`)

On validation `voi` was well below `signed` and close to `uncertainty_margin`, so V1 is expected to fail and V2 is
uncertain. The test is run anyway, as registered, because a pre-registered negative result is the honest way to
report the comparison.
