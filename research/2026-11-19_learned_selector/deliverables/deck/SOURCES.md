# Deck sources

Each slide lists where its numbers come from. Paths are relative to `research/2026-11-19_learned_selector/` unless they start with `out/`, `docs/` or `deliverables/`.
Numbers on slides 8, 9, 11 to 13 and the second-final backups are read from `out/v4_eval/final_geom.json` by `slides.py` when the deck is built. Other numbers are copied from the cited reports.

Q1 (signed plus VLM on the second final test) passes at all three levels. Source: `out/v4_eval/final_vlm.json`, `hypotheses.final.Q1.cells.<level>` (mean_diff, ci95); signed_vlm mean accuracy 0.5163 / 0.4589 / 0.3851 is in `results.final/<level>.signed_vlm.mean_acc`.

## Slide 1: Title

Title text: docs/refined_proposal.md (team, tracks).

## Slide 2: The question: cheaper perception checks, without losing safety

Question and motivation text: docs/refined_proposal.md, sections 0 and 1 (Research question; Domain problem).

## Slide 3: Setup: three tools, a few candidates, a call budget

Families, K, tools, noise (K up to 6 maneuvers over a 5 s horizon: cassvla/planning/features.py CANDIDATE_NAMES, docs/oracle.md): docs/refined_proposal.md (three tools; budget a=one query or none), docs/baseline_results.md (tool noise low/mid/high), REPORT.md section 3 (budget definition, always-on 3 calls), run2/PREREG2.md (metric). Family names: out/v4_eval/final_geom.json results.final/<level>.signed.by_family keys.

## Slide 4: Method: pick the tool from the candidates

Model description: research/2026-11-19_learned_selector/run2/PREREG2.md (Methods: signed, frozen; 32 hidden units, MSE on unclipped expected gain, linear output, call only if largest predicted gain above 0), REPORT.md section 3 (Learner variants). Expected-gain labels: docs/baseline_results.md (8 extra noise draws per tool).

## Slide 5: Baselines: what the selector has to beat

Policies: PREREG.md (Methods), PREREG2.md (Methods). KnowNo 99.76% to 100%: REPORT.md section 2 (Mean accuracy table note, knowno.<alpha>.call_rate). Simple triggers vs random: REPORT.md section 2 (same note).

## Slide 6: How we tested: two pre-registered final tests on fresh seeds

First final: REPORT.md section 2 (seeds 760-859, 4,903 decisions, 34,718 training rows). Second final: out/v4_eval/final_geom.json (n_train, n_test, seeds); run2/PREREG2.md (seeds 1060-1159, written before evaluation, no correction). Pre-registration meaning: PREREG.md and PREREG2.md headers.

## Slide 7: First final test: the candidate-based selector beats both rivals

REPORT.md section 2, Verdicts table (source keys: results.final/<level>.comparisons in out/v3_eval/triggers_final.json; S4 from diff_vs_frozen in out/v3_eval/final/s4_signed.json). Values rounded to 3 decimals from the 4-decimal table.

## Slide 8: Second final test: all four pre-registered hypotheses pass

out/v4_eval/final_geom.json hypotheses.final.P1/P2/P3 cells (mean_diff, ci95); P4 status. Q1 row: out/v4_eval/final_vlm.json hypotheses.final.Q1.cells.<level> (mean_diff, ci95), status pass; n_train 34,718, n_test 4,922.

## Slide 9: At 0.6 calls per decision, signed is within the accuracy margin of always-on and safer

out/v4_eval/final_geom.json hypotheses.final.P4.cells.<level> (acc_diff, acc_diff_ci95, unsafe_diff, unsafe_diff_ci95); absolute values: results.final/<level>.signed.at_budget_0.6 {acc, unsafe} and results.final/<level>.always_on {mean_acc, mean_unsafe}. 0.6 budget: run2/PREREG2.md (P4, chosen post hoc from first final, fresh seeds here).

## Slide 10: Accuracy against calls: signed reaches always-on early

Figure: deliverables/figures/f1_pareto_mid.png (see figures/INDEX.md; source out/v4_eval/final_geom.json results.final/mid.<method>.curve and always_on.mean_acc). First-reach budgets 0.60/0.50/0.35: computed from out/v4_eval/final_geom.json results.final/<level>.signed.curve (21 points, step 0.05) against always_on.mean_acc, first index at or above (post hoc, descriptive). Frozen peak/drop: results.final/<level>.frozen.drop_after_0.65.

## Slide 11: Safety: always-on’s unsafe rate reached by 0.45 to 0.55 calls

Figures: deliverables/figures/f2_unsafe_mid.png and f2_unsafe_high.png (see figures/INDEX.md; source out/v4_eval/final_geom.json results.final/<level>.<method>.unsafe_curve and always_on.mean_unsafe; first-match budgets 0.55/0.50/0.45 (low/mid/high) computed from signed.unsafe_curve, 0.05 grid, first index at or below always_on.mean_unsafe; post hoc, descriptive).

## Slide 12: What drives it: knowing which candidate is on top

REPORT.md section 3 (Which features carry the lead: candidate_only vs scene_only 0.011-0.026; permutation drops 0.056/0.046, 0.045/0.036, 0.027/0.020 from analysis2/FAILURES.md section 3, 0.019/0.014 divergence). P2 values: out/v4_eval/final_geom.json hypotheses.final.P2. Family gains: REPORT.md section 2 (S3, lane_blockage +0.052 to +0.058, occluded_pedestrian +0.040 to +0.048; first final).

## Slide 13: Where it goes wrong: late calls and wrong decisions

Harm and drop: out/v4_eval/final_geom.json results.final/<level>.{signed,frozen,uncertainty_margin}.harm["0.1"] and .drop_after_0.65. Late calls, wrong decision vs wrong tool, depth collapse: REPORT.md section 3 (Failure modes), analysis2/FAILURES.md.

## Slide 14: VLM features: a small gain, about half beyond scene family

Frozen-MLP gain: REPORT.md section 3 (VLM features), docs/phase5_vlm.md Controls (shuffle at or below geometry in 5 of 6 cells; family recovers 20% to 77%, 49% overall). Signed + VLM +0.008 to +0.015: run2/experiments/EXPERIMENTS2.md section B table (cells +0.0084 to +0.0149). Q1 box: out/v4_eval/final_vlm.json hypotheses.final.Q1.cells.<level> (mean_diff, ci95), status pass.

## Slide 15: Limits: what these numbers do and do not show

REPORT.md section 4 (Limits); run2/PREREG2.md (P4 note on 0.6 budget; multiple comparisons paragraph); run2/experiments/EXPERIMENTS2.md (header: about a dozen variants, multiple-comparisons caveat). Nine variants in run 1: REPORT.md section 3 (Learner variants).

## Slide 16: Next steps

REPORT.md section 5 (next steps 1, 2, 3, 4, 6, 7). Offsets and thresholds null: run2/experiments/EXPERIMENTS2.md sections A and D. Real tools / second simulator: our addition from the limits (no file source).

## Slide 17: Summary

Slide 7 (H1 range +0.071 to +0.093) and slide 8 (P3 +0.091 to +0.103), see their sources; P4 unsafe differences: out/v4_eval/final_geom.json hypotheses.final.P4.cells.<level>.unsafe_diff.

## Backup B1: Backup: first final test, mean accuracy by policy

REPORT.md section 2, "Mean accuracy over budgets" table (results.final/<level>.<policy>.mean_acc in out/v3_eval/triggers_final.json; signed_mse_abstain from s4_signed.json).

## Backup B2: Backup: second final test, all methods

out/v4_eval/final_geom.json results.final/<level>.<method>.mean_acc and mean_unsafe; always_on.mean_acc and mean_unsafe.

## Backup B3: Backup: second final test, harm rate and benefit captured

out/v4_eval/final_geom.json results.final/<level>.<method>.harm and .benefit (keys "0.1", "0.2", "0.3", "0.5").

## Backup B4: Backup: second final test, accuracy by scenario family

out/v4_eval/final_geom.json results.final/<level>.{signed,signed_scene}.by_family.<family>.

## Backup B5: Backup: first final test, post hoc unsafe rate against always-on

run2/analysis4/H3_POSTHOC.md sections 1 and 2 (values rounded to 3 decimals; data in run2/analysis4/h3_posthoc.json).

## Backup B6: Backup: signed plus VLM features, val and test (exploratory)

run2/experiments/EXPERIMENTS2.md results table, rows B and C (CIs in the same table).

## Backup B7: Backup: accuracy against calls at low and high noise

Figures: figures/f1_pareto_low.png, f1_pareto_high.png (source out/v4_eval/final_geom.json results.final/<level>.<method>.curve).

## Backup B8: Backup: the 0.6-call test against its pass margins

Figure: figures/f3_p4.png (source out/v4_eval/final_geom.json hypotheses.final.P4.cells).

## Backup B9: Backup: every pre-registered difference, both final tests

Figure: figures/f4_hypotheses.png (sources in figures/INDEX.md: triggers_final.json comparisons, s4_signed.json diff_vs_frozen, out/v4_eval/final_geom.json hypotheses).

## Backup B10: Backup: harm rate by budget at mid noise

Figure: figures/f5_harm.png (source out/v4_eval/final_geom.json results.final/mid.<method>.harm).

## Backup B11: Backup: wrong decision against wrong tool

Figure: figures/f6_gap_split.png (source analysis2/results.json cells.<split>/<level>.q2.plandiscrim; table T4 of analysis2/FAILURES.md).

## Backup B12: Backup: VLM controls

Figure: figures/f7_vlm_controls.png (source out/v2_eval/vlm_extra_train.json and vlm_control_*.json; table in docs/phase5_vlm.md Controls).
