# Audit of docs edits and RESULTS.md, 2026-11-19

Scope: today's changes listed in docs_changes.md, plus analysis/RESULTS.md. Every number was re-read from
`out/v3_eval/triggers.json`, `out/v2_eval/vlm.json`, `out/v2_eval/vlm_extra_train.json`, `out/eval/test.json`,
`wc -l` of the train files, `out/v3_extra`, `out/v3_final`, and the literature claims against
`research/2026-11-06_cass_vla_sota/RELATED_WORK_DELTA.md` and `REPORT.md`. I did not re-check the papers themselves.
Older rewrites of `docs/baseline_results.md` (10,329-row tables, 2,909-decision final split) are outside today's change list and were only spot-checked.

## Findings that need a fix (WRONG / OVERSTATED / UNSOURCED)

| file:line | claim | source | verdict | fix |
|---|---|---|---|---|
| RESULTS.md "What is still weak" item 1 | selector is "2.9 to 3.6 points below the fair ceiling" | triggers.json mean_acc: gaps 0.0362, 0.0387, 0.0292, 0.0319, 0.0339, 0.0322 | WRONG (contradicts RESULTS' own "0.029 to 0.039") | "2.9 to 3.9 points" |
| RESULTS.md harm section bullet 2 | ranker margin harm rate at budget 0.1, test/mid "0.371" | `by_budget.0.1.harm_rate` = 0.3705; table in same file shows 0.370 | WRONG (rounding mismatch inside the file) | use 0.370 (or 0.371 in both places) |
| RESULTS.md families bullet 2 | "Ambiguous light, merge closing speed, lead_brake_cutin gain at most 0.03 over scene-only" | merge_closing_speed test/mid +0.032 | WRONG | "at most 0.032" (or "about 0.03") |
| RESULTS.md VLM table, val/low geometry 10,329 | 0.514 | vlm.json 0.5145; phase5_vlm.md prints 0.515 | OVERSTATED (rounding differs between the two files) | print 0.515 (or 0.5145) so both files agree |
| RESULTS.md "Candidate-only against scene-only" | PlanDiscrim-minus-candidate gap "also above" seed spread | only plandiscrim by_seed ranges were checked (val/mid spread 0.0049 vs gap 0.0074); candidate_only seed spread not examined | OVERSTATED | say "above the PlanDiscrim spread; candidate_only spread not checked", or compute it |
| RESULTS.md "How much of the gap" | "the project goal, equal safety with fewer calls, is met on this metric" | metric is exact top-1 match, not safety (RESULTS item 9 says so); 0.458 at budget 0.5 vs 0.441 single-tool always-on is one test split, one seed set, exploratory; the 0.452 3-tool figure is from a different test set | OVERSTATED | "PlanDiscrim at 0.5 calls per decision reaches higher accuracy than calling the best single tool on every decision (exploratory, test/mid). Not a safety claim. H3 is left to the final test." |
| baseline_results.md:~226 harm bullet (also RESULTS harm bullet 1) | harm ranges "at mid noise" / "at high noise" (2.3% to 3.6%, 6.9% to 11.0%, 17% to 37% ...) | true only for test/mid and test/high, budgets 0.1-0.5; val differs (val/high PlanDiscrim up to 9.2%, val/mid scene_only 5.4% to 10.4%) | OVERSTATED (split not named) | add "on test" and "at budgets 0.1 to 0.5" |
| baseline_results.md:186 | "All trigger policies were fixed on 2026-11-07, before this evaluation" | only the `eval_triggers.py` docstring says so; triggers.json is dated 2026-11-07 11:11, but the script on disk was edited today 18:03 and no earlier copy is kept; the learned ablations are not covered | UNSOURCED beyond the docstring | "The docstring of `scripts/eval_triggers.py` records the triggers as fixed on 2026-11-07." Keep the section labelled exploratory (it ran on val and test, not on the pre-registered final split) |
| literature_survey.md:69-71 (also REPORT.md:54, DELTA:184) | "With 510 seeds on the test split ... it leads there (0.297 against 0.272)", "with expected-gain targets and 510 seeds the lead grows" | 510 is the number of TRAINING seeds (210 main + 300 extra); the test split has 45 seeds. Numbers 0.297 / 0.272 match triggers.json test/mid by_family, training size 25,036 rows | WRONG label (training-size mislabelled as test-split size) | "trained on 510 seeds (25,036 rows), on the test split, averaged over budgets, it leads there (0.297 against 0.272)" |
| literature_survey.md:67, refined_proposal.md:340 | "leads the scene-only MLP by only 1 to 2 points" | that is the 10,329-row run (baseline_results CIs +0.011 to +0.017). The 25,036-row triggers.json run gives +0.019 to +0.030 | OVERSTATED as written (training size not labelled; next bullet in the survey says the lead grows) | "1 to 2 points with 10,329 training rows and 2 to 3 points with 25,036" |
| literature_survey.md:22 | DriveVer's +0.9 PDMS is "the same size as our frozen-embedding gain" | our gain is +0.005 to +0.010 in top-1 accuracy averaged over budgets; PDMS is a different scale (and DELTA row calls it only a comparison) | OVERSTATED (unlike units) | "gains from learned ranking are small, under one PDMS point; our frozen-embedding gain is also small (+0.005 to +0.010 accuracy)" |
| RUNNING.md:27 | VLM control run "ran out of memory on 2026-11-07, and one peaked at 3.7 GB" | runner_status.md: the 3.7 GB peak and the kill happened 2026-11-19 18:09; vlm_control_shuffle.log is dated 2026-11-19 18:04; the 2026-11-07 logs are empty | WRONG date (unless an earlier event exists; none is recorded) | "on 2026-11-19" |
| refined_proposal.md:57 | ETM and BLUE named as examples of expected-effect / information-gain triggers | DELTA says ETM and BLUE: ETM was read as abstract only; BLUE's label is realized benefit, not expected effect on the plan | OVERSTATED (minor) | say "realized benefit (BLUE)" and add "(abstract only)" after ETM, or drop ETM, which has no bib entry |
| literature_survey.md:67-ish / :75 | "We expect to start from ... Look Again Before You Abstain" | no survey row or bib entry exists for it; DELTA lists it as a not-yet-added paper | UNSOURCED inside the survey | add the row or drop the name |
| future_steps.md:38 | "That is evidence about the ceiling Stage B would address" | curve peak at 0.65 is measured; the Stage B link is an interpretation | OVERSTATED (soft) | "Stage B is the stage that would address it" or cut |

## Confirmed claims (summary)

| area | claims checked | verdict |
|---|---|---|
| Headline table, baseline_results.md:~195-210 and RESULTS.md | all 9 policies x 6 cells of `mean_acc` | CONFIRMED (3 d.p.) |
| "beats every simple trigger in all six cells; smallest margin test/high 0.333 vs 0.264" | recomputed | CONFIRMED |
| "simple triggers 0 to 0.03 above random" | max 0.029 (val/mid margin) | CONFIRMED |
| "closes 68% to 75% of the gap; scene-only 45% to 59%; candidate-only 63% to 68%" | recomputed per cell with the best simple trigger (margin, ego_speed in test/high) | CONFIRMED |
| "ranker margin best in five of six cells" | test/high ego_speed (tied with candidate_spread) | CONFIRMED |
| PlanDiscrim vs ceiling gap per cell | 0.029 to 0.039 | CONFIRMED |
| candidate-only beats scene-only 0.011 to 0.026; PlanDiscrim adds 0.004 to 0.009; lead over scene 0.019 to 0.030 | recomputed | CONFIRMED |
| by_seed ranges table | all six | CONFIRMED |
| curve peaks: 0.65 except test/low 0.75; test/mid 0.483 at 0.65, 0.445 at 1.0; falls below scene-only at 0.9-1.0 in val/low, val/mid, test/low and at 1.0 in test/mid, test/high | `curve` keys | CONFIRMED (val/high never falls below, not claimed) |
| "never below best simple trigger at any budget" | worst difference is 0.0 at budget 0 | CONFIRMED (ties at 0) |
| harm/benefit tables, test/mid and test/high, budgets 0.1/0.2/0.3/0.5 | 56 cells re-read | CONFIRMED |
| harm ranges for test (2.3-3.6, 3.7-4.9, 6.9-11.0, 11.2-16.1, 15, 18, 17-37, 20-45) | min/max over report budgets | CONFIRMED (test only) |
| margin captures 3% vs 20.6% benefit at budget 0.1, test/mid | 0.030 / 0.206 | CONFIRMED |
| candidate-only 1 to 3 points less benefit at 0.3 and 0.5 | 0.016-0.031 | CONFIRMED |
| per-family tables and the four-row "loses" list | all 24 family cells recomputed; list is complete | CONFIRMED |
| lane_blockage +0.04 to +0.07; occluded_pedestrian +0.047 to +0.056; low-noise gains under 0.02 for the three weak families | recomputed | CONFIRMED |
| lead_brake_cutin has the lowest ceiling (0.318 at mid) | baseline_results family table | CONFIRMED |
| knowno: threshold 6.9299/6.9228/inf, call rate 0.9968 to 1.0, acc values, PlanDiscrim at budget 1.0; gap "0.004 to 0.023" | all six cells | CONFIRMED |
| "no-tool 0.2045 on test (curve[0]), 0.2498 on val" | curve[0] | CONFIRMED |
| knowno degenerate because only top-two margin stored | eval_triggers.py docstring, DECISIONS.md, PREREG amendment | CONFIRMED |
| 25,036 = 10,329 + 14,707; val 2,222, test 2,235; 3 init seeds | `wc -l`, triggers.json n_train | CONFIRMED |
| budget definition: one call per called decision vs always-on 3 calls, "factor of three" | docs and RESULTS state both consistently | CONFIRMED |
| older always-on 0.452 mid, no-tool 0.2006, n=2288, 45 seeds | out/eval/test.json | CONFIRMED |
| phase5_vlm.md extra-seed table (all 24 cells), ranges +0.003-0.007 -> +0.005-0.010, 13%-31% vs 7%-20%, five of six cells grew, geometry change at most 0.005, 0.416 test/mid, 0.025 below ceiling, positive in all 3 seeds in all cells, decision_rule_met true in both | vlm.json, vlm_extra_train.json | CONFIRMED |
| "0.038 above scene-only" at test/mid (25,036 rows) | vlm_extra scene_only 0.3775 vs 0.4159 | CONFIRMED (0.037 with the 10,329-row scene-only) |
| prompted variant: 7.7% to 8.2% called, 0.208 vs no-tool 0.2045 (test/mid); val 0.261 vs 0.250 | vlm.json | CONFIRMED |
| phase5 section marked exploratory and not pre-registered | BRIEF (extra-train run is outside the pre-registered final test) | CONFIRMED |
| 10,329 vs 25,036 labelling in baseline_results, phase5_vlm, RESULTS | consistent in every table header | CONFIRMED (except items in the fix table) |
| README Project Status pointer; docs/future_steps "as of 2026-11-19" status bullets (six-cell win, Stage A not run because 760-859 sweep unfinished, +0.005 to +0.010) | triggers.json; `ls out/v3_final` = 30 of 120 chunks, log "105 chunks left" | CONFIRMED |
| SEEDS.md rows (760-859 incomplete, 860-1059 9,682 retained) | 14,552 decisions, 9,682 with `retained`; v3_extra.log | CONFIRMED |
| DECISIONS.md 2026-11-19 knowno line; RUNNING.md eval_triggers, flip_features, sweep-resume and chunk-count notes | docstring, run_sweep behavior as described in BRIEF | CONFIRMED (not re-run) |
| refined_proposal.md and literature_survey.md literature claims: DEEP 34% to 54% (monocular-geometry only), DEEP uncertainty heuristics not better than random at 20% budget, learned allocators "about a third of the oracle's value, nearly as much harm", off-road paper rule-based and the one candidate-set precedent, DriveAgent-R1 learned mode token, BLUE "struggle to predict", RRDrive 33.9 -> 27.7, TooGate 78.3%/9.9%, "absence over the papers we found" wording | match DELTA rows P1-P7, S1-S8, Part 4 and REPORT.md lines 54-59, 137, 263 | CONFIRMED against DELTA (no claim stronger than DELTA allows, except the items in the fix table) |

## Other checks

- Pre-registered vs exploratory: phase5 extra-seed section and the triggers section are not presented as pre-registered. Only fix is the "fixed on 2026-11-07" sentence above. The pre-registered final test (seeds 760-859) has no results, and no doc claims one.
- val/test mix-ups: none in the tables. Only the unlabelled split in the harm ranges (fix table).
- Training-size labels: the tables are labelled correctly. Two prose spots lack the label (survey line 67, proposal line 340) and one mislabels it (survey line 71).
- Agent/model/prompt rules for human docs: no mention of coding agents, Claude or authoring prompts in README, docs/*.md or the survey. Mentions of "Qwen3.5-9B", "prompted variant" and paper names (DriveAgent-R1, "LLM Agents Already Know When to Call Tools") are project subject matter, not workflow. `.agents/` files may name agents.
- README: docs_changes.md says it is 628 words, over the 600-word limit; I did not recount. It needs the human rewrite already noted.
- Not audited: the untouched older rewrites in baseline_results.md (2,909-decision final split, 40 runs over five seeds, CIs), HPC.md, hazards/scenarios docs.

## Tally

| verdict | count |
|---|---|
| CONFIRMED (grouped rows above) | 30 groups, covering about 400 individual numbers |
| WRONG | 5 (RESULTS 2.9-3.6; RESULTS 0.371; RESULTS "at most 0.03"; survey "510 seeds on the test split"; RUNNING.md date) |
| OVERSTATED | 8 |
| UNSOURCED | 2 (fixed-on-2026-11-07 beyond docstring; Look Again Before You Abstain in survey) |
