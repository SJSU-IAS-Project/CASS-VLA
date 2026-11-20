# Learned tool selector: report for the 2026-11-19 run

This report answers the professor's question for the learned selector (Track A): does trajectory-conditioned tool selection reach similar or better safety decisions with far fewer calls than always-on or generic uncertainty triggers? Every number cites the file it comes from. Anything chosen on the val or test splits is called exploratory. Only the final test on seeds 760-859 was pre-registered, in `PREREG.md`.

## 1. Result in one paragraph

The pre-registered final test used 100 fresh seeds (760-859, 4,903 decisions), and nothing was tuned on them. On it, the learned selector `plandiscrim` beat the ranker-margin trigger and the scene-only selector at all three noise levels, with every 95% CI above 0 (H1 and H2 hold). It beat the margin trigger by +0.071 to +0.093 mean accuracy and the scene-only selector by +0.020 to +0.021. It matched always-on accuracy at 0.35 to 0.60 calls per decision, against 3 for always-on (H3, descriptive). At low and mid noise it also matched always-on's unsafe rate at the same budget. At high noise it did not, and a post hoc read of the curves, not pre-registered, shows that it needed 0.60 calls to match both (0.20 of always-on's calls). The margin trigger never reached always-on on any budget at any level. The counterfactual flip features did not help (S1 fails: only mid noise has a CI above 0, +0.0029). The variant `signed_mse_abstain` beat the frozen MLP on fresh seeds at mid (+0.0099) and high noise (+0.0175), with CIs above 0 (S4 holds). Its curve no longer falls at high budgets. The exploratory val/test work found the same picture. Most of the lead comes from conditioning on the candidates, calls ranked past 65% are often harmful, and the model picks depth far too often. These results measure top-1 agreement with the oracle's best candidate, plus the oracle's unsafe label on the chosen candidate. They are not a closed-loop collision rate.

## 2. Pre-registered final test (seeds 760-859)

The run happened once, after `PREREG.md` and its two amendments were written and before any final output existed. Training data were `out/v2_dataset` train, `out/v2_extra_ds` train and the train set from `out/v3_extra`, 34,718 rows in all (`n_train` in `out/v3_eval/triggers_final.json`). The final split has 4,903 decisions from seeds 760-859 (`out/v3_final_ds/manifest.json`). No flip rows were missing (`out/v3_eval/final/triggers_final_*.log`). The learned selectors average three init seeds. CIs are a paired bootstrap over scenario seeds, 1,000 resamples. Numbers come from `results.final/<level>.comparisons` in `triggers_final.json` (merged from the per-level files in `out/v3_eval/final/`) and from `results.signed_mse_abstain` in `out/v3_eval/final/s4_signed.json`. `s4_signed.json` was written by `python research/2026-11-19_learned_selector/experiments/exp.py signed_mse_abstain --featsets plandiscrim --train-dirs v2_dataset v2_extra_ds v3_extra_ds --expgain v2_expgain.jsonl v2_extra_expgain.jsonl v3_extra_expgain.jsonl v3_final_expgain.jsonl --test-dir v3_final_ds --splits final --out out/v3_eval/final/s4_signed.json`, with the log in `out/v3_eval/final/s4_signed.log`. I read `scripts/eval_triggers.py` and `experiments/exp.py` to check the keys.

### Verdicts

Mean difference in accuracy averaged over the 21 budgets, with the 95% CI in brackets.

| Hypothesis | Low noise | Mid noise | High noise | Verdict |
|---|---|---|---|---|
| H1: `plandiscrim` minus `uncertainty_margin` | +0.0931 [0.0849, 0.1011] | +0.0795 [0.0713, 0.0882] | +0.0707 [0.0615, 0.0789] | holds at all three |
| H2: `plandiscrim` minus `scene_only` | +0.0201 [0.0157, 0.0246] | +0.0214 [0.0181, 0.0250] | +0.0212 [0.0173, 0.0250] | holds at all three |
| S1: `plandiscrim_flip` minus `plandiscrim` | +0.0000 [-0.0022, 0.0020] | +0.0029 [0.0013, 0.0045] | +0.0011 [-0.0002, 0.0024] | fails (only mid is above 0) |
| S4: `signed_mse_abstain` minus `plandiscrim` | +0.0038 [0.0006, 0.0072] | +0.0099 [0.0062, 0.0136] | +0.0175 [0.0141, 0.0211] | holds at mid and high; low is reported, not part of S4 |

The top-level `hypotheses` key of `triggers_final.json` agrees for H1, H2 and S1 (`final: H1 true, H2 true, S1 false`). The S4 CIs are in `diff_vs_frozen` of `s4_signed.json`. The frozen MLP in that file reproduces the `plandiscrim` means of `triggers_final.json` (0.4990, 0.4338, 0.3588).

### Mean accuracy over budgets

| Policy | Low | Mid | High |
|---|---|---|---|
| random | 0.3835 | 0.3265 | 0.2719 |
| uncertainty_margin | 0.4058 | 0.3543 | 0.2881 |
| ego_speed | 0.3902 | 0.3390 | 0.2893 |
| candidate_spread | 0.3903 | 0.3390 | 0.2895 |
| fixed_schedule | 0.3812 | 0.3358 | 0.2834 |
| scene_only | 0.4788 | 0.4123 | 0.3376 |
| candidate_only | 0.4901 | 0.4287 | 0.3541 |
| plandiscrim | 0.4990 | 0.4338 | 0.3588 |
| plandiscrim_flip | 0.4990 | 0.4367 | 0.3599 |
| signed_mse_abstain (S4) | 0.5028 | 0.4437 | 0.3763 |
| fair_ceiling | 0.5413 | 0.4726 | 0.3867 |

Source: `results.final/<level>.<policy>.mean_acc` and, for S4, `results.signed_mse_abstain.final/<level>/plandiscrim.mean_acc`. The simple triggers sit between 0.002 below and 0.03 above random (`fixed_schedule` is 0.002 below random at low noise). `knowno` calls 99.76% to 100% of decisions at every level and alpha (`knowno.<alpha>.call_rate`), so it is degenerate, as the first amendment said.

### Calls needed to match always-on (H3, descriptive)

Always-on makes 3 calls per decision. Its accuracy and unsafe rate come from `always_on` in each level. The budget is the share of decisions that get one call, so it is also calls per decision. The reached budget uses the 0.05 grid. Source: `h3_always_on` and `curve`, `unsafe_curve` of each policy.

| Level | always-on accuracy / unsafe | `plandiscrim` first reaches the accuracy at | its accuracy / unsafe there | first budget with accuracy and unsafe both matched (post hoc, not in `PREREG.md`) |
|---|---|---|---|---|
| low | 0.5841 / 0.3286 | 0.60 | 0.5937 / 0.3237 | 0.60 (20% of always-on's calls) |
| mid | 0.4860 / 0.4104 | 0.50 | 0.4900 / 0.4103 | 0.50 (17%) |
| high | 0.3586 / 0.4936 | 0.35 | 0.3618 / 0.5367 | 0.60 (20%) |

- At low and mid noise, `plandiscrim` is at or below always-on's unsafe rate as soon as it matches the accuracy. At mid noise the margin is 0.0001, which is a tie.
- At high noise it matches accuracy at 0.35 calls but its unsafe rate there is 0.0431 above always-on's. Post hoc, it needs 0.60 to match both. This is the one place where fewer calls trade away some safety.
- Other selectors, accuracy then both: `candidate_only` 0.65 and 0.65 (low), 0.55 and 0.60 (mid), 0.40 and 0.65 (high). `scene_only` matches accuracy at 0.75, 0.75 and 0.55, but matches the unsafe rate only at low noise (0.75). At mid and high noise it never does.
- `uncertainty_margin` never reaches always-on accuracy or unsafe rate at any budget up to 1.0. Its accuracy at budget 1.0 (the best single tool on every decision) is 0.5639 at low noise, against 0.5841 for always-on.
- Post hoc, not pre-registered: at a fixed budget of 0.5, `plandiscrim` is above always-on's accuracy at mid (0.4900) and high (0.3935) noise but not at low noise (0.5647). Its unsafe rate at 0.5 is 0.3490 (low), 0.4103 (mid) and 0.5030 (high), against 0.3286, 0.4104 and 0.4936.
- The `plandiscrim` curve peaks at budget 0.65 at every level (0.5996, 0.5146, 0.4113) and then falls to 0.5763, 0.4726 and 0.3613 at budget 1.0.

### Harm and benefit at budgets 0.1 to 0.5 (S2)

Each cell shows the harm rate, then the benefit captured. Harm rate is the share of made calls whose chosen tool has a negative expected gain. Source: `by_budget.<budget>.{harm_rate,benefit_captured}`.

| Level | Policy | 0.1 | 0.2 | 0.3 | 0.5 |
|---|---|---|---|---|---|
| low | `plandiscrim` | 0.009 / 0.203 | 0.007 / 0.389 | 0.018 / 0.533 | 0.025 / 0.781 |
| low | `scene_only` | 0.040 / 0.181 | 0.048 / 0.334 | 0.048 / 0.473 | 0.054 / 0.701 |
| low | `uncertainty_margin` | 0.163 / 0.037 | 0.113 / 0.137 | 0.096 / 0.265 | 0.079 / 0.478 |
| mid | `plandiscrim` | 0.046 / 0.181 | 0.029 / 0.351 | 0.028 / 0.494 | 0.035 / 0.727 |
| mid | `scene_only` | 0.065 / 0.166 | 0.082 / 0.310 | 0.092 / 0.433 | 0.095 / 0.645 |
| mid | `uncertainty_margin` | 0.416 / 0.030 | 0.273 / 0.125 | 0.222 / 0.246 | 0.166 / 0.453 |
| high | `plandiscrim` | 0.115 / 0.180 | 0.073 / 0.329 | 0.058 / 0.454 | 0.066 / 0.655 |
| high | `scene_only` | 0.134 / 0.158 | 0.156 / 0.283 | 0.156 / 0.381 | 0.143 / 0.573 |
| high | `uncertainty_margin` | 0.474 / 0.031 | 0.323 / 0.118 | 0.263 / 0.226 | 0.195 / 0.420 |

The margin trigger spends its first calls where a tool hurts: 41.6% harmful at mid noise and budget 0.1, against 4.6% for `plandiscrim`. Harm for `plandiscrim` is higher at high noise (5.8% to 11.5%) than on val and test (3.7% to 4.9% on test).

### Per-family accuracy (S3)

Mean accuracy over budgets, from `by_family` of each policy. The columns are `plandiscrim`, `scene_only` and `uncertainty_margin`.

| Family | Low | Mid | High |
|---|---|---|---|
| ambiguous_light | 0.604 / 0.587 / 0.450 | 0.581 / 0.559 / 0.429 | 0.533 / 0.512 / 0.401 |
| lane_blockage | 0.726 / 0.668 / 0.607 | 0.695 / 0.639 / 0.563 | 0.590 / 0.538 / 0.476 |
| lead_brake_cutin | 0.300 / 0.301 / 0.267 | 0.271 / 0.268 / 0.217 | 0.232 / 0.227 / 0.184 |
| merge_closing_speed | 0.686 / 0.666 / 0.491 | 0.458 / 0.443 / 0.386 | 0.297 / 0.278 / 0.256 |
| occluded_cross_traffic | 0.330 / 0.317 / 0.274 | 0.325 / 0.316 / 0.264 | 0.271 / 0.265 / 0.217 |
| occluded_pedestrian | 0.533 / 0.493 / 0.479 | 0.465 / 0.417 / 0.423 | 0.396 / 0.355 / 0.329 |

`plandiscrim` is above `scene_only` in 17 of 18 cells. The exception is `lead_brake_cutin` at low noise (0.300 against 0.301). The gain is largest for `lane_blockage` (+0.052 to +0.058) and `occluded_pedestrian` (+0.040 to +0.048), as on val and test. I did not compute family-level CIs on the final split.

### S4 in detail: `signed_mse_abstain`

Source: `results.signed_mse_abstain.final/<level>/plandiscrim` in `s4_signed.json`, next to `results.frozen` in the same file.

| Measure | Low | Mid | High |
|---|---|---|---|
| mean accuracy, S4 / frozen | 0.5028 / 0.4990 | 0.4437 / 0.4338 | 0.3763 / 0.3588 |
| accuracy at budget 1.0, S4 / frozen | 0.6024 / 0.5763 | 0.5205 / 0.4726 | 0.4293 / 0.3613 |
| drop after the peak (`drop_after_0.65`) | 0.0000 | 0.0006 | 0.0000 |
| harm rate at budget 0.1, S4 / frozen | 0.001 / 0.009 | 0.008 / 0.046 | 0.012 / 0.115 |
| mean unsafe over budgets, S4 / frozen | 0.4048 / 0.4144 | 0.4549 / 0.4712 | 0.5156 / 0.5395 |
| tool-optimal rate, S4 / frozen | 0.4316 / 0.5180 | 0.5101 / 0.5575 | 0.4911 / 0.5285 |

- On fresh seeds the curve no longer falls above budget 0.65, as it did on val and test. The S4 curve at budget 1.0 (one call per decision at most, since it stops when no tool has a positive predicted gain) is above always-on's accuracy at every level: 0.6024 against 0.5841, 0.5205 against 0.4860 and 0.4293 against 0.3586.
- The tool-optimal rate is lower than the frozen MLP's at every level, as on val and test. S4 stops calling at the right places, but it does not choose better tools. Collision is its predicted tool on 0.352, 0.216 and 0.230 of decisions, against 0.205, 0.081 and 0.064 for the frozen MLP.
- S4 was chosen on val and test. The final test is its confirmation, and it is also the only test of S4. Nothing else about S4 was tuned on the final seeds.

### Reading the final test

H1 and H2 replicate the val and test result on fresh seeds, and the lead over `scene_only` (+0.020 to +0.021) is inside the val and test range (+0.019 to +0.030). H3 supports "about half a call per decision" at low and mid noise but not at high noise on the unsafe measure. S1 fails, so the flip features are not worth keeping. S4 holds. All of it is top-1 accuracy and the oracle's unsafe label, not collisions.

## 3. What the val/test analysis showed (exploratory)

All of this is on val (2,222 decisions) and test (2,235 decisions) of `out/v2_dataset`, with 25,036 training rows, three init seeds, and noise levels low, mid and high. The headline metric is accuracy averaged over 21 budgets from 0 to 1. A budget is the share of decisions that get one tool call, so a budget of 0.5 is half a call per decision, while always-on makes 3 calls per decision. Accuracy means the ranker's top candidate equals the oracle's best candidate after the optional call. Sources are `analysis/RESULTS.md`, `analysis2/FAILURES.md` and `analysis3/SAFETY.md` unless stated.

**Learned selector against simple triggers.**
- `plandiscrim` beats every simple trigger in all six cells. It scores 0.333 to 0.517, against 0.256 to 0.418 for the ranker-margin trigger (`analysis/RESULTS.md`, headline table).
- The paired seed-bootstrap lead over the margin trigger is +0.076 to +0.099, with every 95% CI above 0. The lead over `scene_only` is +0.019 to +0.030, also above 0 in all six cells (`analysis2/FAILURES.md`, table T5).
- The simple triggers (margin, ego speed, candidate spread, fixed schedule) sit only 0 to 0.03 above random. `plandiscrim` closes 68% to 75% of the gap between the best simple trigger and the fair ceiling.
- `knowno` is degenerate. Its threshold calls 99.7% to 100% of decisions, so it equals always calling the best single tool.

**Which features carry the lead.**
- `candidate_only` beats `scene_only` by 0.011 to 0.026 in every cell. Adding the scene features back (`plandiscrim`) adds only 0.004 to 0.009. The sampling noise of one cell is about plus or minus 0.006, so that last gap is unresolved (`analysis2/FAILURES.md`, section 5).
- Permutation importance says that which candidate the ranker chose matters most (a drop of 0.056 at mid noise and 0.046 at high). Scene features cost 0.045 and 0.036. The divergence group costs 0.019 and 0.014, and `div_time` is its strongest single feature (0.0067 at mid).
- So the idea of looking at how the candidates differ helps. But most of the gain comes from knowing which candidate was picked, not from how it differs from the runner-up.
- The counterfactual flip features added nothing on val and test. `plandiscrim_flip` minus `plandiscrim` was -0.0004 to +0.0029, and only test/low had a CI above 0 (`PLAN.md`, log entry 18:43). The final test agrees (section 2).

**Harm.** A call is harmful when the chosen tool has a negative expected gain. On test, at budgets 0.1 to 0.5, `plandiscrim` makes harmful calls on 2.3% to 3.6% of calls at mid noise and 3.7% to 4.9% at high noise. The margin trigger does so on 17% to 37% (mid) and 20% to 45% (high). At budget 0.1 and mid noise the margin trigger captures 3% of the possible benefit, against 20.6% for `plandiscrim` (`analysis/RESULTS.md`, harm tables).

**Failure modes** (`analysis2/FAILURES.md`).
- Late calls hurt. The accuracy curve peaks near budget 0.65 and then falls, for example from 0.483 to 0.445 at test/mid. Calls ranked past 65% are harmful 26% to 46% of the time, yet only 4% to 10% of the total best-tool gain sits there.
- Wrong decision against wrong tool. 55% to 76% of the gap to the ceiling comes from calling the wrong decisions, and the rest from choosing the wrong tool.
- Depth collapse. At mid noise the model predicts depth on 1,514 of 2,222 val decisions. It predicts collision on 130, although collision is the best tool on 272.
- Weak families. `lane_blockage` and `occluded_pedestrian` gain over `scene_only` in every cell. `lead_brake_cutin` loses to a simple trigger at low noise, and the `ambiguous_light` loss at test/high is inside its CI.

**The professor's criterion on val and test** (`analysis3/SAFETY.md`). In all six cells `plandiscrim` reaches always-on accuracy and always-on unsafe rate together at 0.50 to 0.65 calls per decision. That is 17% to 22% of always-on's 3 calls. The margin trigger never reaches either. The crossing is read on the same split it was found on, so it is optimistic. "Unsafe" is the oracle's safety label applied to the ranker's top candidate. It is not a collision rate.

**VLM features.** Adding 32 PCA dimensions of Qwen3.5-9B image features gives +0.005 to +0.010 mean accuracy with 25,036 training rows, positive for all three init seeds in every cell. With 10,329 rows the gain was +0.003 to +0.007 (`analysis/RESULTS.md`, VLM table). The shuffle and family controls were started but have no result file (see limits).

**Learner variants** (`experiments/EXPERIMENTS.md`). `signed_mse_abstain` is the same MLP with a linear output, squared loss on the unclipped gain, and a call only when the predicted gain is above 0. Against the frozen MLP it gained +0.010 at mid noise (val and test) and +0.018 at high noise, all with CIs above 0. At low noise the effect was not reliable. The curve no longer fell after 0.65, and the harm rate at budget 0.1 and test/mid dropped from 0.036 to 0.003. Calibration, a softmax with a "none" class and per-tool loss weights added nothing. Pairwise ranking is a weak maybe (+0.004 to +0.005 at high noise only). Trees were not run because `sklearn` is not installed. Nine variants were tried, so only the signed family, which was consistent across four cells, deserved attention. That is why it became the pre-registered S4.

## 4. Limits

- **The metric is not safety.** Accuracy is exact top-1 match with the oracle's best candidate, and "unsafe" is the oracle's label for the chosen candidate. Nothing was run closed loop, so no collision rate exists (`analysis3/SAFETY.md`, section 3).
- **Same-split optimism on val and test.** The budget at which `plandiscrim` matches always-on, and the 0.65 peak, were read off the split they are reported on. The 0.05 budget grid and small margins at the crossings (for example 0.458 against 0.4537 at test/mid) make the exact budget soft. The final test removes the optimism for H3 only in part, because the matching budget is still read off the final curve (a fixed budget of 0.5 was not pre-registered). Read it as "about half a call per decision".
- **High noise on the final test.** At the accuracy crossing (0.35 calls) the unsafe rate was 0.0431 above always-on's. The safety claim needs 0.60 calls there.
- **Always-on is a tool reference.** It merges all three tool outputs. It is not a VLM verifier, and a "call" is a simulated tool call, not a VLA call (`analysis3/SAFETY.md`).
- **One sweep design.** All data come from the same scenario generator, six families, one noise model and one frozen MLP. Seeds differ across splits, but the generator does not.
- **No CI on unsafe-rate differences.** `comparisons` in the eval files hold only accuracy CIs.
- **VLM controls.** The controls are exploratory, one run per cell with no CIs. Shuffling the VLM features removes the gain (at or below geometry in 5 of 6 cells), and a family one-hot recovers 20% to 77% of it (49% overall), so about half of the gain is information beyond scene family (`docs/phase5_vlm.md`, section Controls). The final seeds have no frames, so the final test has no VLM features (`PREREG.md`).
- **Tests were not run to completion.** The suite was killed after 5 minutes with no summary line, so there is no pass or fail result (`inventory/INVENTORY.md`, section 6).
- **README is still the old proposal.** It is 585 words and describes the original CASS-VLA proposal, not the current results. It needs a rewrite by you (`docs_changes.md`).
- **Docs were checked once.** `audit/AUDIT_docs.md` found 15 problems in the morning's docs edits and all were fixed. The later edits were not re-audited.

## 5. Recommended next steps

1. **Evaluate closed loop.** Run the selected candidate in MetaDrive for a sample of decisions and count collisions at about 0.5 calls per decision against always-on. Why: the professor asked for safety decisions, and today's evidence is top-1 match plus an oracle label.
2. **Make `signed_mse_abstain` the main method.** It held on fresh seeds at mid and high noise and removes the hand-picked budget. Report the frozen MLP as the baseline. Why: the frozen model loses up to 0.06 accuracy by calling too much (section 3), and S4 fixed that without a free parameter.
3. **Test the VLM gain on fresh seeds with frames.** The controls say about half of it is beyond scene family. Why: that estimate is one run per cell, with no CIs, and the final seeds have no frames.
4. **Attack the tool choice.** S4 stops calling at the right places but picks the best tool less often than the frozen MLP, and per-tool loss weights did not help. Try a score offset per tool tuned on held-out seeds, or a two-stage model. Why: 24% to 45% of the gap to the ceiling is wrong tool.
5. **Drop the flip features and say so.** S1 failed on val, test and the final split. Why: they cost a sweep pass and add at most +0.003, and S1 failed.
6. **Put a CI on the unsafe rate and fix a budget in advance.** Bootstrap the unsafe difference by seed. Why: the high-noise unsafe gap on the final test is a single point estimate.
7. **Look at `lead_brake_cutin`.** It is the largest family, has the lowest ceiling, and is one of two families where a simple trigger can win (the other is `occluded_cross_traffic`). A family-aware feature is the cheapest next idea.
8. **Rewrite the README and run the tests per file.** Why: both are course deliverables, and the README is the first thing the professor reads.

## 6. Files

Paths are relative to `research/2026-11-19_learned_selector/` unless they start with `out/`, `scripts/` or `docs/`.

| File | What it is |
|---|---|
| `BRIEF.md`, `PLAN.md`, `runner_status.md` | The shared brief, the schedule and log, and the compute runner's log. |
| `PREREG.md` | The pre-registered final test and its two amendments (knowno, S4). |
| `analysis/RESULTS.md` (+ `tables.csv`, two figures, `analyse.py`, `build_results.py`, `figures.py`) | Digest of the val/test trigger comparison, with a table of every headline number. |
| `analysis2/FAILURES.md` (+ `results.json`, `tables.md`, two figures, `run.py`, `tables.py`, `md_tables.py`, `figures.py`) | Late-call harm, wrong decision against wrong tool, feature importance, CIs. |
| `analysis3/SAFETY.md` (+ `calc.json`, `calc.py`, `tables.py`, `fig.py`, `fig_unsafe_vs_calls.png`) | The professor's criterion: calls to match always-on and unsafe rates. |
| `experiments/EXPERIMENTS.md` (+ `exp.py`, `show.py`, `gen_tables.py`, `tables.md`, `res_*.json`, `neutral_check.json`, logs) | Nine learner variants on val and test. |
| `lit/LIT.md` | 25 papers on query selection, and ranked cheap experiments. |
| `inventory/INVENTORY.md` | Survey of `out/`, `scripts/`, docs and git, with a cleanup proposal. |
| `docs_changes.md`, `audit/AUDIT_docs.md` | What the docs agent changed, and the audit of those changes. |
| `REPORT.md` | This file. |
| `scripts/eval_triggers.py`, `scripts/merge_trigger_runs.py`, `scripts/flip_features.py`, `scripts/eval_vlm.py` | New scripts. `merge_trigger_runs.py` joins per-level runs. |
| `out/v3_eval/triggers.json` | Val/test trigger comparison (first written 2026-11-07). |
| `out/v3_eval/dev/` | Development runs of the extended evaluator, including a fake final split. |
| `out/v3_eval/triggers_final.json`, `out/v3_eval/final/` | The pre-registered final run: merged file, per-level files and logs, and `s4_signed.json` (written by `experiments/exp.py signed_mse_abstain`, command in section 2, log `s4_signed.log`). |
| `out/v3_final/`, `out/v3_final_ds/`, `out/v3_final_expgain.jsonl` | Final seeds 760-859: sweep, dataset (4,903 rows) and expected-gain labels. |
| `out/v3_extra_ds/`, `out/v3_extra_expgain.jsonl` | Training data built from seeds 860-1059. |
| `out/v3_flip/` | Flip features for every sweep. |

## 7. Cleanup proposals and git

These are proposals from `inventory/INVENTORY.md`. I deleted nothing and ran no git write command.

**Cleanup, for you to decide.**
- About 417 MB of v1 outputs in `out/` are superseded, and no doc mentions them: `sweep`, `dataset`, `windows_*`, `phase2_*`, `sweep_stale_lane_blockage`, `bench`, `baseline`, `eval` and `session_scratch`. Archive them to a tarball outside `out/` first, or delete them after a look.
- `research/2026-11-06_cass_vla_sota/listing_sweep/html` (109 MB) and `html_early` (252 MB) hold fetched pages that are not gitignored. Move them out of the repo, or add a `.gitignore` line so that `git status` and `git add` never pick them up.
- Keep every `v2_*` and `v3_*` entry, `vlm_main` (424 MB), `vlm_extra` (352 MB), `v2_frames` and the `*_run.sh` files. The `v3_run.done` marker is misleading and can be ignored.

**What to commit.** Do not commit anything under `out/` (it is gitignored), the listing html, `listing_sweep/fetch*.log` or `verify_run*.log`. The new files from today that belong in git are the scripts (`eval_triggers.py`, `merge_trigger_runs.py`, `flip_features.py`, `eval_vlm.py`, `label_expected_gain.py`, `render_frames.py`, `vlm_encode.py` and `scripts/hpc/`), the docs, the agent notes and this research folder. The research folder holds only small files and figures, but check its size first. The test suite did not finish, so run each test file before you commit the code group. The Long2RAG data is not in this repo and must never be committed.

Run these yourself. Each block is safe to paste whole. This repository lives at `~/CASS-VLA`.

```bash
cd ~/CASS-VLA
echo 'research/2026-11-06_cass_vla_sota/listing_sweep/html*/' >> .gitignore
git status --short | head -50
du -sh research/2026-11-19_learned_selector
```

```bash
cd ~/CASS-VLA
git add cassvla/planning/features.py cassvla/planning/oracle.py cassvla/planning/tools.py cassvla/scenarios/families.py cassvla/scenarios/hazards.py tests/test_hazards.py tests/test_tools.py
git commit -m "fix hazard placement and features, update tests"
git add scripts/build_dataset.py scripts/eval_baselines.py scripts/plot_pareto.py scripts/label_expected_gain.py scripts/render_frames.py scripts/vlm_encode.py scripts/eval_vlm.py scripts/eval_triggers.py scripts/merge_trigger_runs.py scripts/flip_features.py scripts/hpc
git commit -m "add label, vlm, trigger and flip scripts"
git add docs README.md
git commit -m "update results docs and phase 5 notes"
git add .agents .gitignore
git commit -m "add agent notes and handoff"
git add research/2026-11-06_cass_vla_sota/REPORT.md research/2026-11-06_cass_vla_sota/RELATED_WORK_DELTA.md research/2026-11-19_learned_selector
git commit -m "add 2026-11-19 learned selector research"
git push
```
