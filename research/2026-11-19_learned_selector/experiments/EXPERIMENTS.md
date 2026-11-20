# Learned-selector learner variants (exploratory)

Written 2026-11-19. Exploratory only: judged on `val` and `test` of `out/v2_dataset`, never on `out/v3_final*`. None of this is pre-registered, and several variants were tried, so any single "win" below carries a multiple-comparisons caveat.

## Sources

- Code: `exp.py` (trainers and harness; it imports `scripts/eval_triggers.py` and `scripts/eval_baselines.py` unchanged), `show.py`, `gen_tables.py`. Logs: `log_signed.txt`, `log_rest.txt`, `log_toolw.txt`.
- Results: `res_<variant>.json` (curve, by-budget harm and benefit, unsafe rate, difference against the frozen MLP with CI). Tables below are generated into `tables.md` by `gen_tables.py`.
- Reference: `out/v3_eval/triggers.json`. The harness reproduces the frozen `plandiscrim` and `scene_only` mean accuracies in all 12 cells exactly (for example test/mid 0.4073, val/high 0.3683), so the harness matches.

## Setup

Same training data as `triggers.json` (25,036 rows: `out/v2_dataset` train plus `out/v2_extra_ds` train, expected-gain targets from `out/v2_expgain.jsonl` and `out/v2_extra_expgain.jsonl`). Same architecture, steps, learning rate and L2 as `fit_mlp` (32 hidden units, 300 full-batch Adam steps, lr 0.01, l2 1e-3), three init seeds (0, 1, 2) averaged. The metric is accuracy averaged over the 21 budgets. The difference is against the frozen MLP with the same feature set. The CI is a paired seed-bootstrap (1,000 resamples, grouped by scenario seed). Differences of one point (0.01) or less are near the noise floor of this study: the CI half-width is typically 0.003 to 0.006, but it only covers resampling of test scenarios, not the choice of variant, the init seeds or the training set.

Variants:
1. `signed_mse_abstain`: per-tool MLP with linear outputs and squared loss on the unclipped gain (expected gain minus no-tool accuracy). Score is the maximum predicted gain, tool is its argmax. A call is made only inside the budget AND if the predicted gain is above 0. Also `signed_mse_noabstain` (same model, no gain>0 test), `signed_huber_abstain` (clipped residual, delta 0.2) and `signed_mse_abstain_toolw` (per-tool loss weights, the inverse frequency of being the best tool on train, as asked by the manager).
2. `cal_isotonic` and `cal_platt`: the frozen MLP trained on 80% of train (split by scenario seed, 20% of seeds held out), per-tool isotonic or Platt calibration to the clipped gain on the held-out 20%, then rank by the maximum calibrated score. `cal_control_80pct` is the same 80% model with no calibration, so the cost of using less training data is separated from the effect of calibration.
3. Gradient-boosted trees: skipped. `sklearn` is not importable in `.venv` and nothing was installed.
4. `softmax_none`: K+1 softmax with a "none" class. Target is the clipped gains plus a none mass of 1 minus the largest gain, normalized (my own choice, arbitrary). Score is 1 minus p(none).
5. `pairwise_rank`: a scalar decision-level score trained with a pairwise logistic loss on random pairs ordered by the best clipped gain. The tool is the argmax of a frozen-style MLP trained alongside it.

## Results: difference in mean accuracy against the frozen MLP (CI in brackets)


### Feature set: plandiscrim

| variant | val/low | val/mid | val/high | test/low | test/mid | test/high | mean unsafe mid(val/test) | drop after 0.65 (mid val/test) |
|---|---|---|---|---|---|---|---|---|
| frozen MLP (acc) | 0.5166 | 0.4543 | 0.3683 | 0.4808 | 0.4073 | 0.3325 | 0.450 / 0.497 | 0.047 / 0.038 |
| signed_mse_abstain | +0.0056 [+0.0006,+0.0107] | +0.0105 [+0.0045,+0.0162] | +0.0180 [+0.0118,+0.0239] | +0.0003 [-0.0032,+0.0040] | +0.0098 [+0.0052,+0.0150] | +0.0184 [+0.0125,+0.0240] | 0.435 / 0.484 | 0.001 / 0.000 |
| signed_mse_noabstain | +0.0040 [-0.0011,+0.0087] | +0.0071 [+0.0016,+0.0121] | +0.0115 [+0.0062,+0.0168] | -0.0005 [-0.0039,+0.0031] | +0.0070 [+0.0024,+0.0119] | +0.0119 [+0.0064,+0.0174] | 0.439 / 0.487 | 0.040 / 0.034 |
| signed_huber_abstain | +0.0044 [+0.0006,+0.0081] | +0.0109 [+0.0065,+0.0157] | +0.0174 [+0.0108,+0.0234] | -0.0003 [-0.0040,+0.0033] | +0.0099 [+0.0056,+0.0148] | +0.0184 [+0.0124,+0.0240] | 0.435 / 0.486 | 0.001 / 0.000 |
| signed_mse_abstain_toolw | +0.0061 [+0.0021,+0.0104] | +0.0072 [+0.0010,+0.0134] | +0.0180 [+0.0116,+0.0235] | +0.0010 [-0.0031,+0.0054] | +0.0098 [+0.0041,+0.0161] | +0.0171 [+0.0110,+0.0230] | 0.437 / 0.486 | 0.001 / 0.002 |
| cal_control_80pct | -0.0007 [-0.0030,+0.0015] | -0.0012 [-0.0030,+0.0007] | -0.0015 [-0.0034,+0.0003] | -0.0006 [-0.0026,+0.0015] | -0.0017 [-0.0033,+0.0001] | +0.0006 [-0.0017,+0.0029] | 0.452 / 0.500 | 0.045 / 0.037 |
| cal_isotonic | +0.0011 [-0.0024,+0.0041] | -0.0014 [-0.0040,+0.0012] | -0.0015 [-0.0038,+0.0006] | +0.0000 [-0.0027,+0.0027] | -0.0008 [-0.0037,+0.0023] | -0.0006 [-0.0035,+0.0022] | 0.452 / 0.498 | 0.048 / 0.033 |
| cal_platt | +0.0001 [-0.0021,+0.0024] | -0.0015 [-0.0038,+0.0007] | +0.0012 [-0.0009,+0.0033] | +0.0005 [-0.0017,+0.0027] | -0.0025 [-0.0047,-0.0003] | +0.0003 [-0.0020,+0.0026] | 0.452 / 0.500 | 0.051 / 0.039 |
| softmax_none | -0.0039 [-0.0091,+0.0010] | -0.0006 [-0.0052,+0.0041] | -0.0002 [-0.0055,+0.0055] | -0.0068 [-0.0116,-0.0019] | -0.0010 [-0.0050,+0.0034] | +0.0035 [-0.0019,+0.0087] | 0.453 / 0.499 | 0.052 / 0.042 |
| pairwise_rank | -0.0009 [-0.0036,+0.0017] | +0.0020 [-0.0012,+0.0052] | +0.0046 [+0.0006,+0.0087] | -0.0023 [-0.0045,+0.0000] | +0.0017 [-0.0009,+0.0041] | +0.0042 [+0.0009,+0.0071] | 0.450 / 0.497 | 0.056 / 0.045 |

### Feature set: scene_only

| variant | val/low | val/mid | val/high | test/low | test/mid | test/high | mean unsafe mid(val/test) | drop after 0.65 (mid val/test) |
|---|---|---|---|---|---|---|---|---|
| frozen MLP (acc) | 0.4980 | 0.4344 | 0.3433 | 0.4566 | 0.3775 | 0.3089 | 0.463 / 0.518 | 0.013 / 0.009 |
| signed_mse_abstain | +0.0020 [-0.0008,+0.0048] | +0.0041 [+0.0009,+0.0073] | +0.0126 [+0.0083,+0.0172] | -0.0001 [-0.0031,+0.0029] | +0.0041 [+0.0010,+0.0076] | +0.0085 [+0.0040,+0.0130] | 0.454 / 0.509 | 0.002 / 0.000 |
| signed_mse_noabstain | +0.0018 [-0.0010,+0.0046] | +0.0033 [+0.0000,+0.0063] | +0.0098 [+0.0060,+0.0137] | -0.0004 [-0.0034,+0.0025] | +0.0035 [+0.0003,+0.0071] | +0.0068 [+0.0023,+0.0113] | 0.456 / 0.510 | 0.015 / 0.012 |
| signed_huber_abstain | -0.0012 [-0.0051,+0.0030] | +0.0019 [-0.0023,+0.0064] | +0.0103 [+0.0061,+0.0146] | -0.0029 [-0.0063,+0.0007] | +0.0018 [-0.0023,+0.0062] | +0.0041 [-0.0003,+0.0084] | 0.459 / 0.513 | 0.001 / 0.000 |
| signed_mse_abstain_toolw | +0.0012 [-0.0017,+0.0044] | +0.0037 [+0.0006,+0.0070] | +0.0126 [+0.0085,+0.0169] | -0.0017 [-0.0054,+0.0018] | +0.0044 [+0.0007,+0.0081] | +0.0080 [+0.0035,+0.0126] | 0.454 / 0.509 | 0.004 / 0.000 |
| softmax_none | -0.0015 [-0.0061,+0.0030] | -0.0010 [-0.0062,+0.0043] | +0.0039 [-0.0010,+0.0088] | -0.0032 [-0.0071,+0.0004] | -0.0004 [-0.0041,+0.0035] | +0.0016 [-0.0023,+0.0055] | 0.465 / 0.517 | 0.012 / 0.009 |

### Harm rate / benefit captured, plandiscrim, mid noise, val then test (budgets 0.1 / 0.2 / 0.3 / 0.5)

| variant | split | harm 0.1 | 0.2 | 0.3 | 0.5 | benefit 0.1 | 0.2 | 0.3 | 0.5 |
|---|---|---|---|---|---|---|---|---|---|
| frozen | val | 0.0375 | 0.0255 | 0.019 | 0.0357 | 0.1937 | 0.3698 | 0.504 | 0.733 |
| frozen | test | 0.0357 | 0.0246 | 0.0234 | 0.0316 | 0.2056 | 0.3684 | 0.4971 | 0.723 |
| signed_mse_abstain | val | 0.0045 | 0.0105 | 0.015 | 0.012 | 0.1958 | 0.3531 | 0.4936 | 0.7254 |
| signed_mse_abstain | test | 0.003 | 0.0074 | 0.0139 | 0.0119 | 0.1976 | 0.3583 | 0.4976 | 0.7172 |
| signed_mse_noabstain | val | 0.0045 | 0.0105 | 0.015 | 0.012 | 0.1958 | 0.3531 | 0.4936 | 0.7254 |
| signed_mse_noabstain | test | 0.003 | 0.0074 | 0.0139 | 0.0119 | 0.1976 | 0.3583 | 0.4976 | 0.7172 |
| signed_huber_abstain | val | 0.024 | 0.0203 | 0.014 | 0.0171 | 0.1964 | 0.3602 | 0.504 | 0.7318 |
| signed_huber_abstain | test | 0.0149 | 0.0216 | 0.0174 | 0.0164 | 0.2041 | 0.3646 | 0.4958 | 0.7289 |
| signed_mse_abstain_toolw | val | 0.006 | 0.0113 | 0.0145 | 0.0117 | 0.1937 | 0.3551 | 0.4941 | 0.7214 |
| signed_mse_abstain_toolw | test | 0.0 | 0.0089 | 0.0149 | 0.0116 | 0.1986 | 0.3538 | 0.4936 | 0.712 |
| cal_control_80pct | val | 0.0405 | 0.0233 | 0.0215 | 0.0378 | 0.1919 | 0.3753 | 0.5088 | 0.7329 |
| cal_control_80pct | test | 0.0342 | 0.0261 | 0.0269 | 0.0316 | 0.2054 | 0.3639 | 0.4985 | 0.7228 |
| cal_isotonic | val | 0.0165 | 0.024 | 0.0215 | 0.0369 | 0.2024 | 0.3725 | 0.5051 | 0.7273 |
| cal_isotonic | test | 0.0134 | 0.0261 | 0.0279 | 0.0298 | 0.2048 | 0.3664 | 0.4947 | 0.7205 |
| cal_platt | val | 0.0405 | 0.024 | 0.0225 | 0.0384 | 0.1928 | 0.3752 | 0.508 | 0.7329 |
| cal_platt | test | 0.0342 | 0.0261 | 0.0269 | 0.0316 | 0.2053 | 0.364 | 0.4986 | 0.7227 |
| softmax_none | val | 0.0015 | 0.0045 | 0.009 | 0.0261 | 0.194 | 0.3541 | 0.4842 | 0.7303 |
| softmax_none | test | 0.0074 | 0.0097 | 0.0119 | 0.0256 | 0.1979 | 0.3569 | 0.4884 | 0.7303 |
| pairwise_rank | val | 0.0105 | 0.0158 | 0.016 | 0.0246 | 0.1999 | 0.3622 | 0.5014 | 0.733 |
| pairwise_rank | test | 0.006 | 0.0201 | 0.0174 | 0.0224 | 0.2019 | 0.3595 | 0.4957 | 0.7287 |

### Tool-optimal rate (share of decisions with a positive-gain tool where the chosen tool is the best one) and tool shares roi/depth/collision, plandiscrim

| variant | cell | tool-optimal | shares |
|---|---|---|---|
| frozen | val/low | 0.4853 | [0.315, 0.479, 0.206] |
| frozen | val/mid | 0.5442 | [0.269, 0.645, 0.086] |
| frozen | val/high | 0.541 | [0.229, 0.703, 0.068] |
| frozen | test/low | 0.4837 | [0.296, 0.488, 0.216] |
| frozen | test/mid | 0.5643 | [0.24, 0.67, 0.09] |
| frozen | test/high | 0.5282 | [0.199, 0.74, 0.061] |
| signed_mse_abstain | val/low | 0.4192 | [0.146, 0.502, 0.352] |
| signed_mse_abstain | val/mid | 0.5161 | [0.126, 0.64, 0.234] |
| signed_mse_abstain | val/high | 0.5056 | [0.132, 0.612, 0.256] |
| signed_mse_abstain | test/low | 0.4208 | [0.133, 0.523, 0.344] |
| signed_mse_abstain | test/mid | 0.5184 | [0.107, 0.677, 0.217] |
| signed_mse_abstain | test/high | 0.4876 | [0.133, 0.636, 0.231] |
| signed_mse_abstain_toolw | val/low | 0.3948 | [0.144, 0.494, 0.362] |
| signed_mse_abstain_toolw | val/mid | 0.4933 | [0.117, 0.637, 0.246] |
| signed_mse_abstain_toolw | val/high | 0.4937 | [0.134, 0.618, 0.248] |
| signed_mse_abstain_toolw | test/low | 0.3987 | [0.137, 0.51, 0.353] |
| signed_mse_abstain_toolw | test/mid | 0.4964 | [0.103, 0.677, 0.22] |
| signed_mse_abstain_toolw | test/high | 0.4779 | [0.123, 0.651, 0.226] |

### Curves (plandiscrim, test/mid, budgets 0.5 to 1.0 step 0.05)

- frozen: 0.458 0.470 0.481 0.483 0.483 0.481 0.477 0.469 0.460 0.450 0.445
- signed_mse_abstain: 0.463 0.477 0.486 0.488 0.490 0.491 0.491 0.491 0.491 0.491 0.491
- signed_mse_abstain_toolw: 0.463 0.476 0.484 0.488 0.491 0.492 0.492 0.490 0.490 0.490 0.490
- pairwise_rank: 0.463 0.474 0.482 0.489 0.489 0.487 0.479 0.469 0.461 0.452 0.445

## What the numbers say

**Signed-gain regression with abstain (`signed_mse_abstain`) is the one variant with a clear effect.** On plandiscrim, mid noise it gains +0.010 on val and +0.010 on test, high noise +0.018 and +0.018, all with CIs above 0. At low noise the effect is small and not reliable (+0.006 on val, CI just above 0; +0.0003 on test, CI spans 0). The harm rate at budgets 0.1 to 0.5 falls (mid test: 0.036 to 0.003 at budget 0.1, 0.032 to 0.012 at 0.5), and the mean unsafe rate falls about 0.013 to 0.015 at mid noise. Benefit captured is the same or slightly lower (mid test at 0.5: 0.723 to 0.717), so this is mostly fewer harmful calls, not more captured gain. Huber behaves the same on plandiscrim (+0.010 mid, +0.018 high), so the loss choice does not matter there; on scene-only Huber is weaker (mid +0.002 and +0.002, CIs span 0).

**The curve no longer falls above budget 0.65.** The frozen MLP at test/mid peaks at 0.483 (budget 0.65 to 0.70) and drops to 0.445 at budget 1.0. With abstain the curve rises to 0.491 and stays flat from budget 0.8 to 1.0 (0.491 each, because it stops calling once no tool has positive predicted gain). The drop after the peak is 0.001 or less in every plandiscrim cell, against 0.03 to 0.07 for the frozen MLP. Without abstain (`signed_mse_noabstain`) the drop is back (0.034 to 0.063), and the gain is smaller (+0.007 mid, +0.012 high). So about a third to a half of the gain in this variant comes from the regression target and the rest comes from the abstain rule.

**What the gain does not do.** Most of it appears above budget 0.5, where the abstain rule bites; at budgets up to 0.3 the benefit captured barely changes. The gain is largest at high noise, where the frozen MLP over-calls most. At low noise there is little to fix. Scene-only gets the same direction with about half the size (+0.004 mid, +0.009 high), so the abstain rule helps regardless of features.

**Tool choice (manager's question).** Per-tool loss weights did not help: `signed_mse_abstain_toolw` is level with the unweighted version in accuracy (within 0.0035 in every cell, inside the noise). The tool-optimal rate (share of decisions with a positive-gain tool where the chosen tool is the best one) is not better for either signed variant than for the frozen MLP: test/mid 0.564 frozen, 0.518 signed, 0.496 weighted. The signed regression shifts tool shares away from roi (0.24 to 0.11) and toward collision (0.09 to 0.22), so it does spread calls to collision more, but the picked tool is right less often. So the depth collapse is partly a tool-assignment issue that the abstain rule does not fix, and the accuracy gain comes from where it stops calling, not from choosing better tools. I did not try per-tool score offsets tuned on a held-out split.

**Calibration (isotonic, Platt) does nothing.** All differences are within about 0.003 and mostly span 0. The one CI that excludes 0 is Platt at test/mid (-0.0025 [-0.0047,-0.0003]), a negative effect, and the 80% control alone shows differences of the same size, so calibration should not be pursued. The curve still falls after 0.65 (drop 0.033 to 0.062).

**K+1 softmax with "none" is no better than the frozen MLP** (differences -0.007 to +0.004, mostly spanning 0, one significantly negative: test/low). It lowers harm at small budgets but the accuracy does not improve, and the curve still falls (0.042 to 0.070). The none-mass definition is my own and was not tuned.

**Pairwise ranking helps a little at high noise only** (+0.005 val, +0.004 test, CIs just above 0), is null at mid and low (test/low -0.002 [-0.0045, 0.0000]), and the curve still falls after 0.65 (drop 0.045 to 0.074). It uses the frozen MLP's tool choice, so this isolates ranking; the ranking itself brings little.

## Caveats

- Nine variants on six cells each is a lot of looks; only the signed-abstain family has an effect that is consistent in sign and size over val and test at mid and high noise (all four CIs above 0 on plandiscrim, and also on scene-only), which is better than one lucky cell, but the data is the same dataset used to pick it, so a fresh split is needed.
- The CIs resample scenario seeds only. They do not include variation across init seeds (by-seed accuracies are in the json files) or across training sets.
- Low noise shows no reliable effect for any variant.
- The abstain rule at predicted gain above 0 has no tuned threshold, which is a plus for a pre-registration (no free parameter), but a threshold or a score offset might do better; not tried.
- Each variant was trained on the same train rows used for the frozen MLP; the calibration variants used 80% of them.
- An earlier launch of the same script ran twice at once for a few minutes (two copies, same results written to the same files); outputs are identical and deterministic.

## Recommendation

Consider `signed_mse_abstain` (linear output, squared loss on the unclipped gain, abstain when the predicted gain is not above 0, no other parameters) for a future pre-registered test, as a clearly labelled secondary method next to the frozen MLP, not a replacement, because it was found on val/test of the data it is compared on. A pre-registration should fix the loss (MSE), the threshold (0), and report the budget curve beyond 0.65 and the tool-optimal rate. Not worth pursuing: calibration, K+1 softmax, per-tool loss weights. Pairwise ranking is a weak maybe. Trees were not run (no sklearn).
