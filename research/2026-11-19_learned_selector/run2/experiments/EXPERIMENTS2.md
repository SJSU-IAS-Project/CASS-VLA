# Signed-abstain fixes (run 2, exploratory)

Written 2026-11-20. Everything here is exploratory and was judged on `val` and `test` of `out/v2_dataset` only. Nothing touched `out/v3_final*` or `out/v4_final*`. None of it is pre-registered. Four experiments with about a dozen variants were run on the same 4,457 evaluation rows, so a single small win carries a multiple-comparisons caveat, and the CIs cover only resampling of scenarios (grouped by scenario seed, 1,000 paired resamples), not the init seeds, the training set or the choice of variant.

## Sources

- Code: `exp2.py` (new), `exp.py` (a copy of the run-1 harness, method code unchanged), `show2.py`, `gen2.py`. Logs: `log_AC.txt`, `log_D.txt`, `log_B.txt`.
- Results: `res2_AC.json`, `res2_D.json`, `res2_B.json`. Full tables with harm, benefit, unsafe rate, tool shares for every variant and cell: `tables2.md` (made by `gen2.py`).
- Settings as in run 1: 32 hidden units, 300 full-batch Adam steps, lr 0.01, L2 1e-3, init seeds 0, 1, 2 averaged, accuracy averaged over 21 budgets, 8-draw expected-gain targets.
- Training data for A, C and D: `out/v2_dataset`, `out/v2_extra_ds`, `out/v3_extra_ds` train, 34,718 rows. Experiment B has VLM embeddings only for v2 and v2_extra, so it trains on 25,036 rows and has its own comparator (geometry-only signed model on the same rows).
- Comparator everywhere is `signed_mse_abstain` on plandiscrim features. Its means on this data are val/low 0.5228, test/low 0.4829, val/mid 0.4641, test/mid 0.4179, val/high 0.3851, test/high 0.3515. Its mean unsafe rate at mid noise is 0.435 (val) and 0.483 (test), and the drop after the peak is at most 0.0014 in every cell.

## Results: difference in mean accuracy against signed_mse_abstain (CI in brackets)

Column order is val/low, test/low, val/mid, test/mid, val/high, test/high. The last column is the tool-optimal rate at mid noise (val / test); the comparator has 0.515 / 0.525.

| variant | val/low | test/low | val/mid | test/mid | val/high | test/high | tool-optimal mid |
|---|---|---|---|---|---|---|---|
| A offsets, tool-optimal objective | +0.0010 [-0.0027,+0.0050] | +0.0017 [-0.0021,+0.0056] | -0.0001 [-0.0029,+0.0028] | -0.0003 [-0.0030,+0.0021] | -0.0001 [-0.0022,+0.0022] | -0.0001 [-0.0024,+0.0025] | 0.554 / 0.570 |
| A offsets, expected-gain objective | +0.0026 [-0.0014,+0.0069] | +0.0020 [-0.0016,+0.0055] | +0.0012 [-0.0016,+0.0043] | +0.0022 [-0.0010,+0.0054] | +0.0010 [-0.0007,+0.0025] | -0.0008 [-0.0031,+0.0015] | 0.545 / 0.554 |
| A hybrid (BCE MLP picks the tool) | +0.0011 [-0.0021,+0.0043] | -0.0005 [-0.0035,+0.0024] | +0.0003 [-0.0026,+0.0032] | +0.0005 [-0.0035,+0.0042] | +0.0008 [-0.0017,+0.0030] | -0.0017 [-0.0047,+0.0011] | 0.552 / 0.570 |
| A control: 80% model, no offsets | -0.0012 [-0.0033,+0.0009] | +0.0004 [-0.0019,+0.0026] | +0.0007 [-0.0014,+0.0028] | -0.0002 [-0.0020,+0.0016] | +0.0008 [-0.0004,+0.0020] | -0.0010 [-0.0031,+0.0010] | 0.508 / 0.520 |
| B signed + VLM PCA-32 (vs geometry-only signed, same rows) | +0.0110 [+0.0070,+0.0152] | +0.0149 [+0.0101,+0.0193] | +0.0113 [+0.0065,+0.0159] | +0.0116 [+0.0068,+0.0162] | +0.0088 [+0.0050,+0.0128] | +0.0084 [+0.0041,+0.0129] | 0.547 / 0.547 (comparator 0.515 / 0.518) |
| C scene-only signed | -0.0227 [-0.0293,-0.0162] | -0.0250 [-0.0317,-0.0188] | -0.0250 [-0.0318,-0.0181] | -0.0361 [-0.0428,-0.0293] | -0.0286 [-0.0350,-0.0214] | -0.0347 [-0.0410,-0.0287] | 0.524 / 0.541 |
| D threshold eps chosen on held-out | +0.0003 [-0.0001,+0.0006] | -0.0000 [-0.0005,+0.0004] | +0.0000 [-0.0001,+0.0002] | -0.0000 [-0.0001,+0.0001] | -0.0000 [-0.0003,+0.0003] | +0.0002 [-0.0000,+0.0003] | 0.515 / 0.525 |
| D eps fixed 0.02 | +0.0002 [-0.0000,+0.0004] | +0.0000 [-0.0002,+0.0002] | +0.0002 [-0.0002,+0.0006] | +0.0002 [-0.0002,+0.0005] | -0.0000 [-0.0004,+0.0003] | +0.0002 [-0.0000,+0.0006] | 0.515 / 0.525 |
| D eps fixed 0.05 | +0.0001 [-0.0004,+0.0006] | +0.0001 [-0.0003,+0.0005] | +0.0001 [-0.0006,+0.0007] | -0.0002 [-0.0009,+0.0004] | -0.0003 [-0.0011,+0.0006] | -0.0000 [-0.0005,+0.0005] | 0.515 / 0.525 |

Two more A variants (offsets applied to the 80% model, which keeps the held-out rows clean) are in `tables2.md`; they match the full-model versions within 0.0015.

## A. Tool-choice fix

Offsets were added to the predicted gain of tools 1 (depth) and 2 (collision) for the argmax only, with tool 0 (roi) fixed at 0. The grid was -0.10 to +0.10 in steps of 0.02, and the call decision (maximum predicted gain above 0, and the rank score) was left alone. They were chosen per noise level and init seed on the 20% of train scenario seeds held out, by fitting an 80% model. Two objectives were used: tool-optimal rate, and expected gain of the chosen tool summed over calling decisions.

The offsets do what they were chosen to do on the tool-optimal rate: mid noise rises from 0.515 / 0.525 to 0.554 / 0.570 (val / test), and the depth share goes up (the gain objective sends 0.93 of calls to depth, roi and collision nearly vanish). Accuracy does not move. All 18 CIs for the A variants span 0, and the point estimates are within +0.003 and -0.002. The hybrid (the frozen BCE MLP picks the tool) gives the same tool-optimal rate gain (0.552 / 0.570) and the same null in accuracy. Harm and benefit curves are in `tables2.md` and do not differ in any pattern.

Caveats. The chosen offsets sit on the edge of the grid for several levels (-0.10 for collision with the optimal objective in most runs, +0.10 for depth in some gain runs), so the optimum may lie outside the grid; I did not extend it because accuracy is flat. A tool-optimal rate that counts only the single best tool also penalises choosing a tool of equal gain, which makes it a weak proxy for accuracy. The held-out control (80% model without offsets) is itself within 0.0012 of the comparator, so training on 80% costs nothing measurable.

Finding: a better tool-optimal rate does not translate into accuracy here. The tool-choice weakness is real by that metric but its effect on the headline curve is below the noise floor (about 0.003).

## B. Signed + VLM

`signed_mse_abstain` on the 36 plandiscrim geometry features plus 32 PCA components of the `image_mid` embedding (PCA fitted on train only, as in `scripts/eval_vlm.py`). The PCA was computed from the covariance matrix instead of an SVD to keep memory low, which gives the same subspace. The comparator is the geometry-only signed model trained on the same 25,036 rows.

Adding VLM features helps in all six cells, with every CI above 0: +0.011 to +0.015 at low noise, +0.011 to +0.012 at mid, +0.008 to +0.009 at high. Mean unsafe rate falls by about 0.006 to 0.012 (mid val 0.435 to 0.429, mid test 0.484 to 0.476, low test 0.427 to 0.414), the tool-optimal rate rises from 0.515 to 0.547 at mid, and the curve still has no drop after the peak. I did not compare this with the earlier VLM effect on the frozen MLP (see `docs/phase5_vlm.md`). I did not rerun the shuffle and family controls on the signed model, so the claim that the gain comes from image content, not family identity, is not established here. The earlier controls were for the frozen MLP.

Caveat: the VLM variant has 68 input features against 36, so some of the gain could be extra capacity that any informative 32 features would bring. Only the shuffle control would separate that.

Memory: loading only `image_mid` as float32 peaked at about 1.2 GB resident after the setup, not the 3.7 GB of `eval_vlm.py`. My first attempt with an SVD peaked near 2 to 3.5 GB and was killed by the system out-of-memory handler once; the covariance route fixed that.

## C. Scene-only signed twin

Signed abstain on scene-only features (no candidate-divergence features) is 0.023 to 0.036 below the plandiscrim signed model in every cell, CIs far from 0 (for example test/mid -0.0361 [-0.0428,-0.0293]). Its mean unsafe rate is higher by 0.02 to 0.03. The same result appears in experiment B on the smaller training set (-0.022 to -0.036). So the plandiscrim advantage over the scene-only model survives when both get the signed-abstain treatment: the abstain rule does not close the gap, and the plandiscrim features carry real information. This is the fair H2 comparison and it favours plandiscrim by a margin much larger than the noise floor.

## D. Threshold on predicted gain

A call needs a predicted gain above eps. eps was chosen from {0, 0.01, 0.02, 0.03, 0.05, 0.08} on the held-out 20% (80% model, accuracy averaged over budgets), and fixed values 0.02 and 0.05 were tried. The held-out accuracy is flat in eps (for example mid: 0.4377 to 0.4379), so the choice is arbitrary (the picks were 0.0 to 0.08 depending on the init seed). Results are within 0.0003 of the comparator in every cell and all CIs span 0 or touch it. The gain>0 threshold is already close to optimal; no reason to add a parameter.

## Recommendation

- Only one variant is worth pre-registering as a secondary hypothesis: **B, signed abstain on geometry plus VLM PCA-32 `image_mid` features**, compared with geometry-only signed abstain on the same training rows. It is the only variant with a clear, consistent effect (all six cells, CIs above 0, about +0.01).
- C is not a new method; it is the comparison to report for H2 (signed plandiscrim against signed scene-only), where the effect is large. If the manager wants H2 to be fair, pre-register it as the rival.
- A and D should not be pre-registered: nothing separates from the comparator, and offsets add tuned parameters.

Settings to freeze for B: the signed model as in `exp.py` `fit_reg` (MSE on the unclipped expected gain minus the no-tool accuracy, 32 hidden units, 300 steps, lr 0.01, L2 1e-3, init seeds 0 to 2); a call only if the maximum predicted gain is above 0 and within the budget; tool is the argmax; field `image_mid`; PCA dimension 32 fitted on train only; train rows of v2, v2_extra and v3_extra once v3_extra has embeddings (the comparison here used v2 and v2_extra only, so the effect size with v3_extra rows is not measured); metric the mean accuracy over the 21 budgets, with the paired seed-bootstrap CI; headline at mid noise on the final split, plus low and high as secondary. The PCA method (covariance or SVD) should also be fixed. Note the VLM effect is not yet controlled for on the signed model (shuffle across rows would be the check to run next).
