# H3, post hoc: unsafe rate against always_on on the first final split

This note is post hoc. It was written after the pre-registered evaluation of the first final split (`out/v3_final_ds`, seeds 760-859, 4,903 decisions) and none of it was planned in `PREREG.md`. Nothing here counts as a pre-registered result. The second reserved test (`out/v4_final*`) was not touched.

## What was done

I retrained the frozen MLP (`plandiscrim`, `scene_only`) and `signed_mse_abstain` once per noise level, with the training data of `PREREG.md` (34,718 rows from v2, v2_extra and v3_extra). The re-derived curves match `out/v3_eval/triggers_final.json` to within 0.0001 for `plandiscrim`, `scene_only` and `uncertainty_margin`, which is rounding. `signed_mse_abstain` is not in that file, so its numbers come only from this run. Everything is averaged over init seeds 0, 1 and 2. The scripts are `calc.py` (training and per-decision tables), `stats.py` (matching points and bootstraps) and `fig.py`. The results are in `h3_posthoc.json`.

A budget b means that a fraction b of decisions gets one tool call, so it costs b calls per decision. `always_on` costs 3 calls per decision. `signed_mse_abstain` can call less often than its budget, because it abstains when its predicted gain is not above 0. Its actual call rate tops out at 0.85, 0.81 and 0.75 at low, mid and high noise. The tables use the actual call rate, which equals the budget wherever the method has not run out of calls.

"Matches" means the first budget at which the curve is at least `always_on`'s accuracy, or at most its unsafe rate. "Both" means both on the same budget. Unsafe is the share of decisions where the ranker's top candidate is unsafe by the oracle's label. All CIs are paired bootstraps over the 100 scenario seeds, 1,000 resamples, on the per-decision difference from `always_on`.

`always_on` reference values: low accuracy 0.5841 and unsafe 0.3286; mid 0.4860 and 0.4104; high 0.3586 and 0.4936.

## 1. Unsafe rate of plandiscrim minus always_on, with CIs

Negative means plandiscrim is safer. The first three rows use the budget where plandiscrim first reaches `always_on` accuracy on the 0.05 grid in `triggers_final.json`.

| Budget | Low | Mid | High |
|---|---|---|---|
| Accuracy-match budget (0.60 / 0.50 / 0.35) | -0.0049 [-0.0123, 0.0032] | -0.0000 [-0.0099, 0.0103] | +0.0432 [0.0302, 0.0561] |
| 0.3 | +0.1252 [0.1115, 0.1379] | +0.0837 [0.0705, 0.0977] | +0.0577 [0.0438, 0.0709] |
| 0.5 | +0.0204 [0.0105, 0.0303] | -0.0000 [-0.0099, 0.0103] | +0.0094 [-0.0036, 0.0212] |
| 0.7 | -0.0078 [-0.0141, -0.0010] | -0.0123 [-0.0199, -0.0045] | -0.0031 [-0.0136, 0.0066] |

At low and mid noise, plandiscrim's unsafe rate at the matching budget is not distinguishable from `always_on`'s, since both CIs contain 0. At high noise it is clearly worse at the accuracy-match budget of 0.35, by 4.3 points. It never reaches `always_on`'s unsafe rate by 0.5 either. It gets there only at about 0.57 calls per decision, where the difference is -0.0014 [-0.0131, 0.0096]. At 0.7 it is safer than `always_on` at low and mid noise with the CI excluding 0, and at high noise it is level.

## 2. signed_mse_abstain against always_on

Same layout. Negative means safer than `always_on`.

| Budget | Low | Mid | High |
|---|---|---|---|
| Plandiscrim's accuracy-match budget (0.60 / 0.50 / 0.35) | -0.0137 [-0.0220, -0.0055] | -0.0131 [-0.0235, -0.0023] | +0.0322 [0.0188, 0.0451] |
| 0.3 | +0.1216 [0.1064, 0.1367] | +0.0794 [0.0664, 0.0919] | +0.0494 [0.0350, 0.0630] |
| 0.5 | +0.0105 [0.0009, 0.0203] | -0.0131 [-0.0235, -0.0023] | -0.0169 [-0.0289, -0.0044] |
| 0.7 | -0.0176 [-0.0251, -0.0101] | -0.0304 [-0.0398, -0.0213] | -0.0345 [-0.0451, -0.0243] |

Yes, `signed_mse_abstain` matches `always_on`'s unsafe rate at high noise. On the 0.05 grid the first budget is 0.45, with a difference of -0.0027 [-0.0154, 0.0100] (a tie), and accuracy there is 0.0373 above `always_on` [0.0233, 0.0514]. At 0.5 it is safer than `always_on` with the CI excluding 0 (-0.0169), and from 0.5 on it stays safer, down to -0.0345 at 0.7. That is 0.45 to 0.5 calls per decision, which is 15 to 17 percent of `always_on`'s 3 calls. It is also 0.05 to 0.1 calls cheaper than plandiscrim, which needs about 0.57. These are point estimates at chosen budgets, so I would not call the gap between the two methods established without a paired comparison between them, which I did not run.

## 3. Calls per decision to match always_on (post hoc)

First budget on the 0.05 grid, which equals calls per decision except where noted. "Not reached" means no budget up to 1.0 qualifies. The 0.01 grid values are in the next section.

| Method | Target | Low | Mid | High |
|---|---|---|---|---|
| plandiscrim | accuracy | 0.60 | 0.50 | 0.35 |
| plandiscrim | unsafe | 0.60 | 0.50 | 0.60 |
| plandiscrim | both | 0.60 | 0.50 | 0.60 |
| signed_mse_abstain | accuracy | 0.60 | 0.50 | 0.35 |
| signed_mse_abstain | unsafe | 0.55 | 0.50 | 0.45 |
| signed_mse_abstain | both | 0.60 | 0.50 | 0.45 |
| scene_only | accuracy | 0.75 | 0.75 | 0.55 |
| scene_only | unsafe | 0.75 | not reached | not reached |
| scene_only | both | 0.75 | not reached | not reached |
| uncertainty_margin | accuracy | not reached | not reached | not reached |
| uncertainty_margin | unsafe | not reached | not reached | not reached |
| uncertainty_margin | both | not reached | not reached | not reached |

For `signed_mse_abstain`, the "both" cell at high noise is 0.45 because its accuracy already exceeds `always_on`'s at 0.35 and stays above. At low noise "both" is 0.60, set by accuracy on this grid.

The simple trigger `uncertainty_margin` uses the single best tool (depth) at every level, so its ceiling is one call per decision. Its best accuracy is 0.5639, 0.4660 and 0.3559 against `always_on`'s 0.5841, 0.4860 and 0.3586, and its lowest unsafe rate is above `always_on`'s at every level. `scene_only` reaches `always_on` accuracy only late and never matches its unsafe rate at mid or high noise (its lowest unsafe rates are 0.4141 and 0.5055).

## 4. Does the matching budget depend on how budgets are spaced?

A little. On a 0.01 grid, plandiscrim first reaches `always_on` accuracy at 0.57, 0.49 and 0.35 calls per decision (low, mid, high), against 0.60, 0.50 and 0.35 on the 0.05 grid. So the 0.05 grid rounds up by at most 0.03. It first reaches `always_on`'s unsafe rate at 0.58, 0.50 and 0.57. The ordering of methods does not change.

The first match is also fragile, because curves are noisy near the crossing. A seed-bootstrap over the first accuracy-match budget gives a median and 95% interval of 0.57 [0.53, 0.59] at low, 0.49 [0.46, 0.53] at mid and 0.35 [0.30, 0.40] at high. For the unsafe match the numbers are 0.58 [0.54, 0.62], 0.50 [0.48, 0.55] and 0.56 [0.49, 0.64]. At high noise 8.4 percent of resamples never reach `always_on`'s unsafe rate at all. The accuracy curve of plandiscrim stays at or above `always_on` from the first match to budget 0.88 at low noise, 0.90 at mid and 1.0 at high, so for accuracy the first match is a stable crossing. The unsafe curve is not: at all three levels it dips under `always_on`'s and later comes back above it near budget 1, and it never stays below from the first crossing to the end.

For `signed_mse_abstain` on the 0.01 grid the first matches are accuracy 0.57, 0.48 and 0.33, unsafe 0.54, 0.46 and 0.45, and both 0.57, 0.48 and 0.45 (low, mid, high). Its curve stays matched to the end of its call range, since it stops calling past 0.75 to 0.85.

## Limits

This is one final split, and the budgets and methods were chosen after seeing both the pre-registered output and val and test, so the comparison of `signed_mse_abstain` with plandiscrim is a description, not a test. The 1,000-resample CIs are for one chosen budget each and are not corrected for the number of budgets I looked at. The figure `h3_posthoc.png` shows the difference from `always_on` in accuracy and unsafe rate across all budgets.
