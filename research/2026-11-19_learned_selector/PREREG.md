# Pre-registered final test, written 2026-11-19 18:03 PST

Written before the second final split (`out/v3_final`, seeds 760-859) was finished, labelled or evaluated. It runs once.

**Training data:** `out/v2_dataset` train, `out/v2_extra_ds` train and the train set built from `out/v3_extra`
(seeds 860-1059), all with expected-gain targets from `scripts/label_expected_gain.py` (8 draws).

**Methods:**
- **Learned selectors:** the frozen MLP from `eval_baselines.fit_mlp`, averaged over init seeds 0, 1 and 2.
  - `plandiscrim`: all geometry and candidate features.
  - `scene_only`: the scene features and the margin.
  - `candidate_only`: the candidate features and the margin.
  - `plandiscrim_flip`: all features plus `scripts/flip_features.py`. This one is secondary.
- **Simple triggers:** `uncertainty_margin`, `ego_speed`, `candidate_spread`, `fixed_schedule`, `knowno`, and
  `random` (20 runs).
- **References:** `always_on` and `fair_ceiling`.
- No VLM features (no frames exist for these seeds).

**Metric:** decision accuracy (`correct`) averaged over the 21 budgets from 0 to 1, at the low, mid and high noise
levels. The 95% CIs come from a paired bootstrap over seeds, with 1,000 resamples.

**Primary hypotheses.** Each must hold at all three noise levels:
- **H1:** `plandiscrim` beats `uncertainty_margin`, with a 95% CI above 0.
- **H2:** `plandiscrim` beats `scene_only`, with a 95% CI above 0.
- **H3:** for the professor's criterion, report the smallest budget at which `plandiscrim` reaches `always_on`
  accuracy, if it does, and its unsafe rate there compared with `always_on`'s. If it never does, report
  "not reached" and the gap at budget 0.3. This is descriptive, with no pass or fail.

**Secondary:**
- **S1:** `plandiscrim_flip` beats `plandiscrim` at all three levels.
- **S2:** the harm rate and benefit captured at budgets 0.1, 0.2, 0.3 and 0.5.
- **S3:** per-family accuracy.

**What is not allowed:** changing methods, features, settings or training data after seeing any `v3_final`
output. Any later change is reported as exploratory.

**Amendment, 2026-11-19 18:08, before any `v3_final` output exists:** `knowno` stays in the output but is
reported as degenerate when its call rate is above 0.95. On val and test the threshold called 99.7 to 100% of
decisions, so it is not a budgeted trigger. No other change.

**Amendment 2, 2026-11-19 20:33, before any `v3_final` output exists:** adds secondary hypothesis S4 for
`signed_mse_abstain` from `experiments/exp.py`. It is the same MLP with a linear output, MSE on the unclipped expected
gain, and a call only when the predicted gain is above 0. Its settings are fixed as they ran on val and test, with the
same training data as the primary methods.

S4: `signed_mse_abstain` beats `plandiscrim` at mid and high noise, with a seed-bootstrap 95% CI above 0. Low noise
is reported but not part of the hypothesis. We also report its curve past budget 0.65 and the tool-optimal rate.

It was chosen on val and test, so S4 is a confirmation test on fresh seeds. H1 to H3 are unchanged.
