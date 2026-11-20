### T1 ranks 0-65% against 65-100%, plandiscrim seed 0

| cell | early score | early gain of chosen | early harm | late n | late score | late gain of chosen | late best-tool gain | late harm | late zero | late positive | late no-tool correct | share of best gain in late |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| val/low | 0.6627 | 0.5506 | 0.0485 | 778 | 0.0833 | -0.081 | -0.0088 | 0.2969 | 0.5938 | 0.1093 | 0.545 | 0.0408 |
| val/mid | 0.5476 | 0.4266 | 0.063 | 778 | 0.1072 | -0.1477 | -0.0328 | 0.3882 | 0.4897 | 0.1221 | 0.5501 | 0.0534 |
| val/high | 0.3911 | 0.2748 | 0.0796 | 778 | 0.1153 | -0.1917 | -0.0683 | 0.4627 | 0.3766 | 0.1607 | 0.5347 | 0.0776 |
| test/low | 0.6741 | 0.5804 | 0.0351 | 783 | 0.1029 | -0.0605 | 0.0069 | 0.258 | 0.6271 | 0.1149 | 0.4725 | 0.0454 |
| test/mid | 0.5567 | 0.4398 | 0.0572 | 783 | 0.1238 | -0.1027 | 0.0014 | 0.3563 | 0.4623 | 0.1814 | 0.4662 | 0.0701 |
| test/high | 0.3938 | 0.2763 | 0.0709 | 783 | 0.1298 | -0.1427 | -0.0348 | 0.3934 | 0.3729 | 0.2337 | 0.4432 | 0.0989 |

### T2 late decisions, mean expected gain per tool and chosen-tool mix

| cell | gain if roi | gain if depth | gain if collision | chosen roi | chosen depth | chosen collision |
|---|---|---|---|---|---|---|
| val/low | -0.0946 | -0.0569 | -0.0601 | 0.6645 | 0.2905 | 0.045 |
| val/mid | -0.1713 | -0.108 | -0.097 | 0.5411 | 0.4422 | 0.0167 |
| val/high | -0.1893 | -0.1811 | -0.1525 | 0.4422 | 0.5308 | 0.027 |
| test/low | -0.0814 | -0.0356 | -0.039 | 0.645 | 0.3142 | 0.0409 |
| test/mid | -0.1389 | -0.0715 | -0.0712 | 0.4879 | 0.4955 | 0.0166 |
| test/high | -0.1502 | -0.1367 | -0.1173 | 0.4189 | 0.5453 | 0.0358 |

### T3 late decisions by family (harm share / mean expected gain of chosen / share where no tool has positive gain / n)

| family | val/mid | test/mid | val/high | test/high |
|---|---|---|---|---|
| ambiguous_light | 0.17 / -0.04 / 0.94 / 111 | 0.17 / -0.01 / 0.83 / 111 | 0.28 / -0.07 / 0.89 / 114 | 0.30 / -0.06 / 0.79 / 109 |
| lane_blockage | 0.66 / -0.23 / 0.96 / 112 | 0.70 / -0.23 / 0.98 / 104 | 0.92 / -0.37 / 0.95 / 105 | 0.85 / -0.40 / 0.95 / 99 |
| lead_brake_cutin | 0.36 / -0.16 / 0.69 / 231 | 0.35 / -0.16 / 0.66 / 274 | 0.36 / -0.17 / 0.57 / 225 | 0.33 / -0.14 / 0.54 / 267 |
| merge_closing_speed | 0.63 / -0.24 / 0.73 / 52 | 0.48 / +0.02 / 0.48 / 54 | 0.61 / -0.28 / 0.64 / 77 | 0.41 / -0.10 / 0.45 / 74 |
| occluded_cross_traffic | 0.13 / -0.05 / 0.91 / 173 | 0.15 / -0.01 / 0.88 / 168 | 0.22 / -0.08 / 0.75 / 162 | 0.18 / -0.03 / 0.75 / 158 |
| occluded_pedestrian | 0.70 / -0.28 / 0.72 / 99 | 0.57 / -0.17 / 0.60 / 72 | 0.72 / -0.31 / 0.74 / 95 | 0.59 / -0.19 / 0.59 / 76 |

### T4 gap to the fair ceiling in expected accuracy, split (plandiscrim seed 0; scene_only in brackets)

| cell | budget | gap | (a) wrong decisions | (b) wrong tool | calls inside ceiling set | calls with a non-best tool | calls with negative gain | scene_only [gap; shares] |
|---|---|---|---|---|---|---|---|---|
| val/low | 0.2 | 0.03313 | 0.0219 (66%) | 0.0112 (34%) | 0.491 | 0.241 | 0.0068 | [0.0577; a 82%; b 18%] |
| val/low | 0.5 | 0.09327 | 0.0627 (67%) | 0.0306 (33%) | 0.811 | 0.2754 | 0.0234 | [0.1326; a 78%; b 22%] |
| val/mid | 0.2 | 0.05547 | 0.0416 (75%) | 0.0138 (25%) | 0.5676 | 0.2815 | 0.027 | [0.0752; a 83%; b 17%] |
| val/mid | 0.5 | 0.09811 | 0.0582 (59%) | 0.0399 (41%) | 0.7948 | 0.3456 | 0.0387 | [0.1389; a 72%; b 28%] |
| val/high | 0.2 | 0.05063 | 0.0354 (70%) | 0.0152 (30%) | 0.5518 | 0.2883 | 0.0563 | [0.0787; a 78%; b 22%] |
| val/high | 0.5 | 0.08753 | 0.0479 (55%) | 0.0396 (45%) | 0.7615 | 0.3348 | 0.0576 | [0.1337; a 68%; b 32%] |
| test/low | 0.2 | 0.02931 | 0.0213 (73%) | 0.0080 (27%) | 0.5101 | 0.2192 | 0.0045 | [0.0551; a 84%; b 16%] |
| test/low | 0.5 | 0.10117 | 0.0747 (74%) | 0.0265 (26%) | 0.8014 | 0.2612 | 0.0224 | [0.1432; a 83%; b 17%] |
| test/mid | 0.2 | 0.04955 | 0.0379 (76%) | 0.0117 (24%) | 0.5682 | 0.2796 | 0.0179 | [0.0736; a 85%; b 15%] |
| test/mid | 0.5 | 0.09838 | 0.0633 (64%) | 0.0351 (36%) | 0.7791 | 0.3157 | 0.0322 | [0.1454; a 76%; b 24%] |
| test/high | 0.2 | 0.04877 | 0.0352 (72%) | 0.0135 (28%) | 0.566 | 0.302 | 0.0403 | [0.0798; a 81%; b 19%] |
| test/high | 0.5 | 0.08898 | 0.0526 (59%) | 0.0364 (41%) | 0.7478 | 0.3462 | 0.0483 | [0.1361; a 69%; b 31%] |

### T5 bootstrap, mean difference over budgets and 95% interval over scenario seeds

| cell | minus scene_only | minus uncertainty_margin | seeds |
|---|---|---|---|
| val/low | +0.0187 [+0.0127, +0.0249] | +0.0988 [+0.0845, +0.1148] | 45 |
| val/mid | +0.0199 [+0.0133, +0.0267] | +0.0844 [+0.0711, +0.0978] | 45 |
| val/high | +0.0250 [+0.0195, +0.0309] | +0.0767 [+0.0631, +0.0918] | 45 |
| test/low | +0.0241 [+0.0188, +0.0297] | +0.0964 [+0.0843, +0.1087] | 45 |
| test/mid | +0.0298 [+0.0237, +0.0360] | +0.0810 [+0.0695, +0.0932] | 45 |
| test/high | +0.0236 [+0.0180, +0.0288] | +0.0763 [+0.0660, +0.0878] | 45 |

### T6 plandiscrim minus scene_only by family, interval over seeds (intervals that include 0 marked *)

| family | val/low | val/mid | val/high | test/low | test/mid | test/high |
|---|---|---|---|---|---|---|
| ambiguous_light | +0.002* | +0.005* | +0.008* | +0.019 | +0.021 | -0.008* |
| lane_blockage | +0.061 | +0.042 | +0.052 | +0.061 | +0.068 | +0.067 |
| lead_brake_cutin | +0.002* | +0.004* | +0.006* | +0.007 | +0.010 | +0.013 |
| merge_closing_speed | +0.001* | +0.018 | +0.027 | +0.008* | +0.032 | +0.016 |
| occluded_cross_traffic | +0.016 | +0.019 | +0.026 | +0.027 | +0.025 | +0.018* |
| occluded_pedestrian | +0.055 | +0.053 | +0.056 | +0.048 | +0.048 | +0.047 |

### T7 permutation importance, drop in mean accuracy over budgets (val / test)

**plandiscrim, mid noise** (base 0.4541 val, 0.4086 test)

| unit | val | test |
|---|---|---|
| group: top_candidate_identity | 0.05733 | 0.05426 |
| group: scene_agnostic_incl_margin | 0.04547 | 0.04459 |
| group: occlusion | 0.02783 | 0.02672 |
| group: candidate_divergence | 0.01657 | 0.02045 |
| group: top_candidate_safety | 0.01733 | 0.01844 |
| group: candidate_spread | 0.01565 | 0.01763 |
| has_stop | 0.02128 | 0.0216 |
| n_visible | 0.02142 | 0.01856 |
| stop_dist | 0.01591 | 0.01645 |
| top_change_left | 0.01524 | 0.01441 |
| top_stop | 0.01441 | 0.01327 |
| occl_max | 0.01369 | 0.01302 |
| range_uncertainty_near_top | 0.0096 | 0.00907 |
| occl_mean | 0.00857 | 0.00885 |
| top_change_right | 0.00877 | 0.00814 |
| nearest_visible | 0.00954 | 0.00707 |

**plandiscrim, high noise** (base 0.3681 val, 0.3329 test)

| unit | val | test |
|---|---|---|
| group: top_candidate_identity | 0.04849 | 0.0427 |
| group: scene_agnostic_incl_margin | 0.0362 | 0.03504 |
| group: occlusion | 0.01816 | 0.021 |
| group: candidate_divergence | 0.01253 | 0.01545 |
| group: candidate_spread | 0.01357 | 0.00863 |
| group: top_candidate_safety | 0.00827 | 0.01154 |
| stop_dist | 0.01555 | 0.01902 |
| n_visible | 0.01486 | 0.01478 |
| top_change_left | 0.0122 | 0.01338 |
| nearest_visible | 0.01266 | 0.00726 |
| top_stop | 0.01054 | 0.00883 |
| occl_max | 0.00892 | 0.00862 |
| top_ttc | 0.00725 | 0.00685 |
| stop_in_reach_light_unknown | 0.00735 | 0.00614 |
| top_keep_fast | 0.0052 | 0.00654 |
| top_change_right | 0.0052 | 0.00522 |

**scene_only, mid noise** (base 0.4325 val, 0.3789 test)

| unit | val | test |
|---|---|---|
| group: scene_agnostic_incl_margin | 0.08098 | 0.0613 |
| n_visible | 0.03058 | 0.02541 |
| margin | 0.02923 | 0.02418 |
| stop_dist | 0.02313 | 0.02564 |
| has_stop | 0.02273 | 0.01948 |
| nearest_visible | 0.02196 | 0.01793 |
| ego_speed | 0.01238 | 0.01203 |
| light_known | 0.00308 | 0.00314 |
| light_green | 0.00143 | 0.00311 |
| light_yellow | 0.00218 | 0.00131 |
| light_red | 0.00099 | 0.00046 |

**scene_only, high noise** (base 0.3424 val, 0.3095 test)

| unit | val | test |
|---|---|---|
| group: scene_agnostic_incl_margin | 0.05502 | 0.04789 |
| margin | 0.02273 | 0.02078 |
| n_visible | 0.01789 | 0.01769 |
| stop_dist | 0.00893 | 0.01708 |
| nearest_visible | 0.00903 | 0.01478 |
| has_stop | 0.00844 | 0.0116 |
| ego_speed | 0.00614 | 0.00871 |
| light_known | 0.0055 | 0.00655 |
| light_green | 0.00156 | 0.00257 |
| light_yellow | 0.0005 | 0.00125 |
| light_red | 0.00035 | 0.00022 |

### T8 divergence features singly, mean of val and test, plandiscrim

| feature | mid | high |
|---|---|---|
| div_time | 0.0067 | 0.0021 |
| div_occl | 0.0014 | 0.0014 |
| div_actor_near | 0.0016 | 0.0011 |
| div_lateral | 0.0002 | 0.0018 |
| div_progress | -0.0006 | -0.0002 |
| runner_safe | 0.0029 | 0.0017 |
| runner_clearance | 0.0011 | 0.0013 |
| runner_ttc | 0.003 | 0.003 |
| runner_is_change | 0.0028 | 0.0007 |
| light_splits_top2 | 0.0016 | 0.0018 |

### T9 per-family tool choice, mid noise, val and test pooled (counts)

| family | n | share where no tool helps | predicted tool counts | best tool counts (argmax, ties to roi first) | exact-argmax agreement | tool-optimal rate (ties count) | mean regret |
|---|---|---|---|---|---|---|---|
| ambiguous_light | 575 | 0.54 | roi 389, depth 173, coll 13 | roi 162, depth 81, coll 22 | 0.72 | 0.78 | 0.055 |
| lane_blockage | 618 | 0.40 | roi 52, depth 419, coll 147 | roi 86, depth 203, coll 80 | 0.39 | 0.60 | 0.087 |
| lead_brake_cutin | 1446 | 0.41 | roi 270, depth 1117, coll 59 | roi 284, depth 418, coll 155 | 0.48 | 0.56 | 0.083 |
| merge_closing_speed | 733 | 0.19 | roi 45, depth 679, coll 9 | roi 72, depth 377, coll 143 | 0.64 | 0.68 | 0.068 |
| occluded_cross_traffic | 471 | 0.74 | roi 141, depth 316, coll 14 | roi 13, depth 89, coll 21 | 0.72 | 0.73 | 0.073 |
| occluded_pedestrian | 614 | 0.21 | roi 191, depth 396, coll 27 | roi 178, depth 202, coll 103 | 0.48 | 0.54 | 0.106 |

### T10 per tool

| cell | tool | decisions where it is the unique-or-first best | predicted tool when it is best (roi, depth, collision) | times predicted | share of predictions that are tool-optimal |
|---|---|---|---|---|---|
| val/mid | roi | 394 | [0.2919, 0.6624, 0.0457] | 578 | 0.6471 |
| val/mid | depth | 649 | [0.0308, 0.8459, 0.1233] | 1514 | 0.6367 |
| val/mid | collision | 272 | [0.0699, 0.8713, 0.0588] | 130 | 0.5308 |
| test/mid | roi | 401 | [0.2918, 0.6334, 0.0748] | 510 | 0.6471 |
| test/mid | depth | 721 | [0.0472, 0.8599, 0.0929] | 1586 | 0.6658 |
| test/mid | collision | 252 | [0.0635, 0.8452, 0.0913] | 139 | 0.4964 |
| val/high | roi | 513 | [0.2515, 0.7466, 0.0019] | 498 | 0.6124 |
| val/high | depth | 668 | [0.0509, 0.9296, 0.0195] | 1681 | 0.6127 |
| val/high | collision | 220 | [0.0727, 0.8909, 0.0364] | 43 | 0.5581 |
| test/high | roi | 532 | [0.218, 0.7744, 0.0075] | 439 | 0.6538 |
| test/high | depth | 701 | [0.0471, 0.9287, 0.0243] | 1740 | 0.6034 |
| test/high | collision | 243 | [0.0494, 0.9177, 0.0329] | 56 | 0.6071 |
