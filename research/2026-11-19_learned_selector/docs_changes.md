# Docs changes, 2026-11-19

- docs/phase5_vlm.md: replaced the "Not yet tried" extra-seed bullet with a section "Training on the extra seeds" (exploratory, not pre-registered; numbers from out/v2_eval/vlm_extra_train.json vs vlm.json); cross-reference to the trigger comparison. No Controls section: out/v2_eval/vlm_control_*.json do not exist (only logs).
- docs/baseline_results.md: new section "Comparison with simple call triggers" (out/v3_eval/triggers.json, 25,036 training rows, budget scale vs always-on's 3 calls, knowno degenerate); Data table rows and commands for v3 sweeps, flip features, eval_triggers.
- docs/refined_proposal.md: delta P1-P7 (domain problem, motivation, no tool, uncertainty rival, always-on), scene-only MLP baseline, fair ceiling, narrowed novelty paragraph, new limitation bullet.
- docs/literature_survey.md: delta S1-S3, 12 new table rows (only those whose bib key exists), new SOTA observations, rewritten gap and relevance sections.
- docs/future_steps.md: added "Where Phase 1 stands".
- README.md: Project Status replaced by a short results/out-layout pointer (README is 628 words, already over 600 before; needs a human rewrite).
- .agents/skills/doc/references/SEEDS.md, RUNNING.md, DECISIONS.md, SKILL.md: status of v3_final/v3_extra, new commands and gotchas, two dated decisions, description updated.

Skipped: delta rows marked "needs bib" (FD-WAM, ETM, Learning When to Search, DynaChain, MosaicDrive, Best-of-Evidence, Auditing Latent-Space Monitors, DriveBench) and the observation/gap sentences that depend on them; docs/novelty_feasibility_audit.md and docs/proposal.md (delta A1-A6, supersede note); verification of scenarios.md/oracle.md against the 0.8 speed scaling; VLM controls section; final-test results (none received).

## Second round (skipped items done)

- docs/novelty_feasibility_audit.md: delta A1-A6 applied (Phase 1 claim with the shield kept as long-term goal, tool-use bullet, contributions 1 and 2, summary judgment, final critique). The heading "Final AI critique" still mentions AI; a human doc should rename it.
- docs/proposal.md: superseded note at the top, rest unchanged.
- docs/scenarios.md, docs/oracle.md: checked against DECISIONS.md (0.8 scaling) and cassvla/scenarios/families.py. Family speed and distance ranges in scenarios.md match the code and the 0.8 note is correct; oracle.md quotes no speed ranges. No edits.
- README.md: 628 to 585 words by removing "Initial References", whose three papers are already rows in docs/literature_survey.md. No other facts removed.
- A full xewe README rewrite needs: title plus one sentence; Problem (2-3 faults); Solution with three ideas; See it (one command and output, for example scripts/eval_triggers.py); Why not X (always-on, scene-uncertainty trigger, numbers from docs/baseline_results.md); Install (scripts/setup.sh); Usage (three tasks); Status; then Development (tests take over 5 minutes), Layout pointing to directory READMEs, and License by SPDX id (no LICENSE file checked; ask the human). The current abstract, system diagram, inputs/outputs, hypothesis and baselines describe the original CASS-VLA proposal and live in docs/proposal.md.

## Audit fixes

- analysis/RESULTS.md: "2.9 to 3.6" to "2.9 to 3.9" points below the ceiling; margin harm rate 0.371 to 0.370; "at most 0.03" to "at most 0.032"; VLM table val/low 0.514 to 0.515 (tables.csv has no such value, no change); PlanDiscrim-vs-candidate-only gap now backed by by_seed (lowest PlanDiscrim seed beats highest candidate-only seed in all six cells, by 0.002 to 0.008); "project goal met" replaced by exploratory wording and H3 left to the final test; harm ranges labelled "on test, at budgets 0.1 to 0.5".
- docs/baseline_results.md: harm bullet labelled test and budgets 0.1 to 0.5; "fixed 2026-11-07" now cites the eval_triggers.py docstring and the section is called exploratory.
- docs/literature_survey.md: 510 is now training seeds (25,036 rows) in both bullets; "1 to 2 points" labelled 10,329 rows, "2 to 3" for 25,036; DriveVer comparison no longer says same size (different scales); added Look Again Before You Abstain row (arXiv 2606.16667, in papers.csv, abstract only).
- docs/refined_proposal.md: ETM dropped, BLUE now "realized benefit"; "1 to 2 points" labelled by training size.
- docs/future_steps.md: Stage B sentence softened.
- .agents/skills/doc/references/RUNNING.md: out-of-memory date 2026-11-19.
- research/2026-11-06_cass_vla_sota/REPORT.md (lines 54, 58, 247, 272) and RELATED_WORK_DELTA.md (184, 186): "510 seeds" now says training seeds.

## Final results

- docs/baseline_results.md: new section "Pre-registered final test (seeds 760-859)" (hypothesis table H1, H2, S1, S4 with mean diff and 95% CI; accuracy table for all policies; H3 vs always-on with the high-noise caveat 0.537 vs 0.494; n_train 34,718; S4 method chosen on val/test). Numbers read from out/v3_eval/triggers_final.json and out/v3_eval/final/s4_signed.json. Stale "still being swept" lines and the Data row updated.
- docs/future_steps.md: Stage A bullet now cites the final test.
- .agents/skills/doc/references/SEEDS.md: 760-859 marked SEEN, fresh seeds from 1060 (already stated at the top).
- .agents/skills/doc/references/DECISIONS.md: dated line, H1 and H2 passed, S4 candidate needs fresh seeds from 1060.
- Not done: VLM controls section (jsons not checked), README and refined_proposal pointers.

## Report audit fixes

- REPORT.md: simple triggers vs random now "0.002 below to 0.03 above"; "both matched" column, the 0.60 high-noise claim and the fixed-budget-0.5 bullet labelled post hoc (summary, section 2, section 4 line); S4 producer command and log added to section 2 and the Files table; "of calls" for collision changed to "of decisions"; "up to 0.07" to "up to 0.06"; flip features "add at most +0.003, and S1 failed"; lead_brake_cutin "one of two families" (other is occluded_cross_traffic); listing html 109 MB and html_early 252 MB, ignore line `listing_sweep/html*/`.
- docs/baseline_results.md final-test section: H3 sentence marked descriptive with matching budgets read off the final curves, not pre-registered. Flip wording already gave +0.003 and no "nothing" claim, no "both matched" column there.

## VLM controls

- docs/phase5_vlm.md: new "Controls" section (real, shuffle, shuffle within family, family; gain over geometry per cell, from out/v2_eval/vlm_extra_train.json and vlm_control_*.json; exploratory, 25,036 rows, no CIs). Manager's reading checked: full shuffle at or below geometry in 5 of 6 cells (test/high +0.0001) confirmed; family one-hot recovers 20% to 77% per cell (49% of the summed gain), not "a third to a half" in every cell; within-family shuffle at most +0.0014 in five cells, +0.0047 test/high; so about half of the gain is beyond scene family (23% to 80% by cell).
- research/2026-11-19_learned_selector/REPORT.md: Limits "VLM controls" bullet replaced with the result and a pointer; next step 3 reworded.

## Second final

- docs/baseline_results.md: new section "Second pre-registered final test (seeds 1060-1159)" (P1-P3 and Q1 table, accuracy table, P4 table, caveats: 0.6 chosen post hoc, 0.01 margin ours, no multiple-comparison correction, controls not repeated on signed) and a Data row. Numbers read from out/v4_eval/final_geom.json and final_vlm.json.
- docs/phase5_vlm.md: short Q1 section (+0.016, +0.012, +0.010; at 0.6 calls accuracy +0.016/+0.012/+0.012, unsafe -0.012/-0.004/-0.003).
- DECISIONS.md: dated 2026-11-20 line, signed-gain abstain selector is the main method.
- RUNNING.md: headless Chromium PDF needs (LD_LIBRARY_PATH, FONTCONFIG_FILE) and deliverables build commands.
- Not edited: SEEDS.md (already updated). I did not run the build commands.
