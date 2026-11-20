# Figures index

Regenerate all with `MPLBACKEND=Agg /home/user/CASS-VLA/.venv/bin/python make_figures.py` (this folder). Each figure has a PNG (200 dpi, 13.33 in wide) and an SVG. Light background, categorical colors are slots 1-4 of the dataviz palette (#2a78d6 blue, #eb6834 orange, #1baf7a aqua, #eda100 yellow; validator passes on the adjacent pairlist, contrast WARN relieved by legends, distinct markers and value labels). Methods keep a fixed order and color: signed, frozen, signed_scene, uncertainty_margin. always_on is black.

Paths below are relative to /home/user/CASS-VLA. For selectors, calls per decision = budget b (a fraction b of decisions gets one tool call), so their curves run from 0 to 1.0 (21 points, budgets 0, 0.05, ..., 1.0). Only always_on costs 3 calls per decision. The f1/f2 x-axis is linear 0 to 3.

| file | shows | source and keys |
|---|---|---|
| f0_pipeline | scene + K candidates -> selector -> one tool or none -> ranker -> decision, scored against the oracle | no data (drawn by hand) |
| f1_pareto_low / _mid / _high | accuracy vs calls per decision on the second final; always_on star at x=3 with dashed level line; dotted line at 0.6 calls | out/v4_eval/final_geom.json: results["final/<level>"][method]["curve"] for signed, frozen, signed_scene, uncertainty_margin; results[...]["always_on"]["mean_acc"] |
| f2_unsafe_mid / _high | unsafe rate vs calls per decision, same methods | same file: [method]["unsafe_curve"]; ["always_on"]["mean_unsafe"] |
| f3_p4 | P4: signed minus always_on at 0.6 calls, accuracy and unsafe rate, per noise level, 95% CI, margins -0.01 / +0.01 with failing zone shaded | out/v4_eval/final_geom.json: hypotheses["final"]["P4"]["cells"][level]: acc_diff, acc_diff_ci95, unsafe_diff, unsafe_diff_ci95 |
| f4_hypotheses | forest plot of every pre-registered difference, both finals. First final (n=4,903): H1, H2, S1 from comparisons (mean_diff, ci95_by_seed), S4 from diff_vs_frozen (mean, ci95). Second final: P1-P3 (mean_diff, ci95), P4 accuracy and unsafe rows. Axis is accuracy difference; P4 unsafe rows are unsafe-rate differences (negative is safer). S4 low is reported but not part of the hypothesis. | out/v3_eval/triggers_final.json: results["final/<level>"]["comparisons"]["plandiscrim_vs_uncertainty_margin" / "plandiscrim_vs_scene_only" / "plandiscrim_flip_vs_plandiscrim"]; out/v3_eval/final/s4_signed.json: results["signed_mse_abstain"]["final/<level>/plandiscrim"]["diff_vs_frozen"]; out/v4_eval/final_geom.json: hypotheses["final"]["P1".."P4"]["cells"] |
| f5_harm | harm rate at budgets 0.1, 0.2, 0.3, 0.5 for signed, frozen, uncertainty_margin, mid noise, second final (budgets are categorical positions) | out/v4_eval/final_geom.json: results["final/mid"][method]["harm"]["0.1"|"0.2"|"0.3"|"0.5"] |
| f6_gap_split | share of the gap to the ceiling that is (a) wrong decisions and (b) wrong tool, plandiscrim seed 0, val and test, budgets 0.2 and 0.5. Exploratory (stated in the title). Share b = b_wrong_tool / gap_exp_acc; share a = 1 - b. | research/2026-11-19_learned_selector/analysis2/results.json: cells["<split>/<level>"]["q2"]["plandiscrim"] entries with budget 0.2 and 0.5: gap_exp_acc, b_wrong_tool (matches T4 in analysis2/FAILURES.md) |
| f7_vlm_controls | gain of geometry+VLM over geometry per cell for real, shuffle, shuffle_family, family. Exploratory, one run per cell, no CIs. | out/v2_eval/vlm_extra_train.json (real), vlm_control_shuffle.json, vlm_control_shuffle_family.json, vlm_control_family.json: results["<split>/<level>"]["geometry_vlm"]["mean_acc"] minus ["geometry"]["mean_acc"] |

Notes
- f1 mid is the headline figure for the P4 claim: at 0.6 calls signed is above the always_on dashed line in accuracy at mid noise.
- The always_on accuracy and unsafe rate are the "mean_acc" and "mean_unsafe" of the always_on entry, which is the value at 3 calls.
