# Second pre-registered final test, written 2026-11-20 01:50 PST

Written before any evaluation on `out/v4_final` (seeds 1060-1159, 4,922 decisions). It runs once. The labels were
built by the runner, who checked row counts only.

**Training data:** the train splits of `out/v2_dataset`, `out/v2_extra_ds` and `out/v3_extra_ds`, 34,718 rows, all
with expected-gain targets from 8 draws.

**Test data:** `out/v4_final_ds/final.jsonl`, with labels from `out/v4_final_expgain.jsonl`.

**Methods.** Settings are frozen as they ran in `run2/experiments/exp2.py` and `experiments/exp.py`, averaged over
init seeds 0, 1 and 2.
- **`signed`** (primary): `signed_mse_abstain` on the plandiscrim features. The MLP has 32 hidden units, a linear
  output, MSE on the unclipped expected gain, 300 Adam steps, lr 0.01 and L2 1e-3. It calls only when the largest
  predicted gain is above 0 and the decision falls within the budget, and it picks the argmax tool.
- **`frozen`:** the original plandiscrim MLP from `eval_baselines.fit_mlp`, with BCE on the clipped gain.
- **`signed_scene`:** `signed` trained on the scene features and the margin only.
- **`uncertainty_margin`:** calls the lowest-margin decisions first, with the tool that is best on train.
- **`always_on`:** calls all three tools on every decision, which is 3 calls per decision.
- **`signed_vlm`** (secondary): `signed` with the image_mid VLM features added as PCA-32 inputs. The PCA comes from a
  covariance eigendecomposition fitted on the training rows only. Embeddings: `out/vlm_main`, `out/vlm_extra`, and
  `out/vlm_v3` for v3_extra and v4_final.

**Metric:** decision accuracy averaged over the 21 budgets from 0 to 1, at low, mid and high noise. 95% CIs come
from a paired bootstrap over scenario seeds, with 1,000 resamples.

**Primary hypotheses:**
- **P1:** `signed` beats `frozen` at mid and high noise, with the CI above 0. This replicates S4 from the first
  final test.
- **P2:** `signed` beats `signed_scene` at all three levels, with the CI above 0.
- **P3:** `signed` beats `uncertainty_margin` at all three levels, with the CI above 0.
- **P4:** the professor's criterion, at a fixed budget of 0.6 calls per decision (20% of always-on's calls). At all
  three levels, `signed` is non-inferior to `always_on`:
  - the CI for its accuracy minus always-on's has a lower bound above -0.01;
  - the CI for its unsafe rate minus always-on's has an upper bound below +0.01.
  - The 0.6 budget was chosen post hoc from the first final split (`analysis4/H3_POSTHOC.md`); these seeds are fresh.

**Secondary:**
- **Q1:** `signed_vlm` beats `signed` at all three levels, with the CI above 0. This runs only if `out/vlm_v3`
  covers every v3_extra and v4_final row. If it doesn't, Q1 is reported as not run.
- **Q2:** report harm rate and benefit captured at budgets 0.1, 0.2, 0.3 and 0.5, the unsafe rate, the curve after
  budget 0.65, the tool-optimal rate and per-family accuracy.

**What is not allowed:** changing methods, features, settings, the training data or the 0.6 budget after seeing any
`v4_final` output. Any later analysis is post hoc.

**Multiple comparisons:** 4 primary hypotheses, each tested at every level it names. No correction is applied, so
read a narrow pass with that in mind.
