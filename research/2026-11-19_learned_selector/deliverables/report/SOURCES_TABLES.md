# Generated tables and where their numbers come from

Made by `build.py`. Each table is computed from the file and keys below when the report is built.

| Table id | File | Keys |
|---|---|---|
| T-counts | `out/v2_dataset/manifest.json; out/v3_final_ds/manifest.json; out/v4_final_ds/manifest.json` | counts.<split>.<family>, summed over train, val and test for the main dataset |
| T-first-verdicts | `out/v3_eval/triggers_final.json; out/v3_eval/final/s4_signed.json` | results.final/<level>.comparisons.*.{mean_diff,ci95_by_seed}; hypotheses.final.{H1,H2,S1}; results.signed_mse_abstain.final/<level>/plandiscrim.diff_vs_frozen.{mean,ci95} |
| T-first-means | `out/v3_eval/triggers_final.json; out/v3_eval/final/s4_signed.json` | results.final/<level>.<policy>.mean_acc; results.signed_mse_abstain.final/<level>/plandiscrim.mean_acc |
| T-first-h3 | `out/v3_eval/triggers_final.json` | results.final/<level>.{always_on,h3_always_on.plandiscrim}; the both-matched budget is computed here from plandiscrim.curve and .unsafe_curve (post hoc) |
| T-first-s2 | `out/v3_eval/triggers_final.json` | results.final/<level>.<policy>.by_budget.<budget>.{harm_rate,benefit_captured} |
| T-first-s4 | `out/v3_eval/final/s4_signed.json; out/v3_eval/triggers_final.json` | results.signed_mse_abstain.final/<level>/plandiscrim.{mean_acc,acc_at_1.0,tool_optimal_rate}; results.final/<level>.plandiscrim.curve[-1]; .always_on.acc |
| T-fam1 | `out/v3_eval/triggers_final.json` | results.final/<level>.<policy>.by_family.<family> |
| T-final2-means | `out/v4_eval/final_geom.json` | results.final/<level>.<method>.{mean_acc,mean_unsafe}; always_on mean_acc and mean_unsafe are its constant accuracy and unsafe rate |
| T-P123 | `out/v4_eval/final_geom.json` | hypotheses.final.{P1,P2,P3}.cells.<level>.{mean_diff,ci95}, .status |
| T-P4 | `out/v4_eval/final_geom.json` | hypotheses.final.P4.cells.<level>.{acc_diff,acc_diff_ci95,unsafe_diff,unsafe_diff_ci95,acc_lower_above_minus_0.01,unsafe_upper_below_plus_0.01} |
| T-at06 | `out/v4_eval/final_geom.json` | results.final/<level>.<method>.at_budget_0.6.{acc,unsafe}; always_on mean_acc, mean_unsafe |
| T-q1 | `out/v4_eval/final_vlm.json` | hypotheses.final.Q1.cells.<level>.{mean_diff,ci95}; results.final/<level>.{signed_vlm,signed}.{mean_acc,mean_unsafe,at_budget_0.6} |
| T-s2-2 | `out/v4_eval/final_geom.json` | results.final/<level>.<method>.{harm,benefit}.<budget> |
| T-shape2 | `out/v4_eval/final_geom.json` | results.final/<level>.<method>.{acc_at_1,drop_after_0.65,tool_optimal,tool_share} |
| T-fam2 | `out/v4_eval/final_geom.json` | results.final/<level>.<method>.by_family.<family> (point estimates, no CIs) |
| T-reach2 | `out/v4_eval/final_geom.json` | computed here from results.final/<level>.<method>.{curve,unsafe_curve} (21 budgets, step 0.05) against always_on mean_acc and mean_unsafe; first budget at which the curve is at least always-on accuracy, at most its unsafe rate, and both on the same budget |
