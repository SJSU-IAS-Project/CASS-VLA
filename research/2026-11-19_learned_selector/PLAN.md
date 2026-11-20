# Schedule and log, 2026-11-19 learned-selector run (18:00 to 20:30 PST)

Manager: main session (no hands-on work). Workers: Sonnet agents. Shared brief: `BRIEF.md`; final test rules: `PREREG.md`.

## Wave 1 (18:05)
| Agent | Job | Writes | Stop |
|---|---|---|---|
| runner | the only heavy CPU user: finish the v3_final sweep, the VLM controls, the flip features, labels and datasets | `out/v3_*`, `out/v2_eval/vlm_control_*`, `out/v3_flip/` | 20:15 |
| evaldev | extend `eval_triggers.py`: unsafe rate, always-on, calls to match always-on, bootstrap CIs, multiple extra-train sets | `scripts/eval_triggers.py`, `out/v3_eval/dev/` | 19:00 |
| analyst1 | analyse `out/v3_eval/triggers.json` and the earlier evals | `research/2026-11-19_learned_selector/analysis/` | 19:10 |
| researcher | literature on learned query selection and active feature acquisition, turned into testable changes | `research/2026-11-19_learned_selector/lit/` | 19:15 |
| organizer | inventory of `out/`, `scripts/` and the tests, plus a cleanup proposal | `research/2026-11-19_learned_selector/inventory/` | 19:00 |

## Wave 2 (about 19:10)
- **analyst2:** controls and flip features on val and test.
- **experimenter:** exploratory variants from the literature, on val and test only.
- **docs:** updates via `xewe_doc`.

## Wave 3 (about 19:50)
- **runner:** the pre-registered final run.
- **auditor:** checks the numbers.
- **synthesis:** writes `REPORT.md`.

## Log
- 18:00 Machine idle, 7.6 GB free. The HPC link is down, so the run stays local.
- 18:03 Wrote `BRIEF.md` and `PREREG.md`.
- 18:05 Launched wave 1: runner, evaldev, analyst1, researcher, organizer (all Sonnet). Stop moved to 20:30 by the user.
- 18:08 analyst1 done (`analysis/RESULTS.md`, figures, `tables.csv`).
  - PlanDiscrim closes 68 to 75% of the gap from the best simple trigger to the ceiling.
  - The candidate-only MLP carries most of the lead over scene-only.
  - Harm rate at mid noise is 2 to 4%, against 17 to 37% for the margin trigger.
  - The curve peaks at budget 0.65, then falls.
  - knowno is degenerate: with no-tool accuracy about 0.2, the threshold calls 99.7 to 100% of decisions.
- 18:10 researcher done (`lit/LIT.md`: 25 papers, 8 ranked experiments; the selector is one-step greedy AFA). Launched the experimenter on experiments 1-5, on val and test only.
- 18:11 organizer done (`inventory/INVENTORY.md`).
  - The test suite took more than 5 minutes and was killed with no result.
  - Cleanup proposal: about 417 MB of v1 outputs in `out/`, and 361 MB of listing html in research that could be committed by mistake.
  - Docs edit list has 11 items. Launched the docs agent.
- 18:12 The final sweep is at 10 of 105 chunks, about 45 s per chunk, so it should finish around 19:20. The runner's VLM controls peaked at 3.7 GB, so they are deferred until the sweep ends. (Corrected log times: entries above were first written with guessed clock times.)
- 18:13 docs agent done (`docs_changes.md`). It updated 7 docs and the agent notes.
  - No Controls section yet: the control runs don't exist.
  - README is at 628 words, over the 600 limit, and still the old proposal text, so it needs a human rewrite.
  - Skipped the "needs bib" rows. The docs agent stays available for the controls and the final results.
- 18:14 Launched analyst2 (failure modes, feature importance, CIs) and a docs auditor. Resumed the docs agent on the skipped items: novelty audit, proposal note, scenarios and oracle check, README length.
- 18:15 docs agent round 2 done.
  - Applied novelty audit A1-A6 and added the superseded note to the proposal.
  - Scenarios and oracle docs already match.
  - README is down to 585 words.
  - The heading "Final AI critique" in the novelty audit is for the human to rename.
- 18:18 Docs auditor done: 15 items to fix (5 WRONG, 8 OVERSTATED, 2 UNSOURCED), about 400 numbers confirmed. The main ones: '510 seeds on the test split' (it is training seeds), 'goal met' overclaimed (the metric is top-1 match, not safety), harm ranges hold on test only. Sent the fixes to the docs agent.
- 18:18 evaldev done. eval_triggers.py now has unsafe rates, always-on, H3, seed-bootstrap CIs and a hypotheses summary. Old numbers reproduce exactly.
  - Val/test results: H1 and H2 hold on both. At val/mid, plandiscrim minus margin is +0.084 [0.071, 0.098] and minus scene_only is +0.020 [0.013, 0.027]. It reaches always-on accuracy at budget 0.5.
  - A full run takes about 20 minutes.
  - Sent it back to make missing flip rows an error, to test the final-split path on a copy of test, and to run the flip val/test check (S1).
- 18:19 docs agent fixed all 15 audit items, including '510 seeds' in the 2026-11-06 REPORT and DELTA. Look Again Before You Abstain (2606.16667) is now a survey row; ETM is dropped from the proposal.
- 18:27 analyst2 done (`analysis2/FAILURES.md`).
  - Calls past budget 0.65 are 26 to 46% harmful, which is why the curve falls.
  - 55 to 76% of the gap to the ceiling is calling the wrong decisions; the rest is the wrong tool.
  - The model collapses onto depth.
  - Permutation importance: the top-candidate identity and scene groups rank above the divergence group; div_time is the strongest divergence feature.
  - CIs: plandiscrim beats scene_only by +0.019 to +0.030 and the margin trigger by +0.076 to +0.099, clear of zero in all 6 cells.
  - Forwarded the depth-collapse and harm findings to the experimenter.
- 18:27 Launched analyst3: the professor's safety criterion (calls to match always-on accuracy and unsafe rate), from dev/triggers_v2.json.
- 18:29 analyst3 done (`analysis3/SAFETY.md`).
  - Exploratory, val/test: plandiscrim matches always-on on both accuracy and unsafe rate at 0.50 to 0.65 calls per decision, which is 17 to 22% of always-on's 3 calls.
  - uncertainty_margin never matches always-on; scene_only matches it on both only in val/low and val/mid.
  - Caveats: the crossing is read on the same split, so it is optimistic; there are no CIs on the unsafe rate; 'unsafe' is the oracle's label for the chosen candidate.
- 18:43 evaldev round 2 done.
  - Missing flip rows are now an error.
  - The final-split path is verified on a copy of test.
  - Flip val/test run: S1 false on val and test. plandiscrim_flip minus plandiscrim is -0.0004 to +0.0029; only test/low's CI is above 0.
  - The final run would take about 40 minutes, so I asked for a --levels flag and a merge step to run the levels in parallel.
- ~19:00 to 20:30 The runner, evaldev and experimenter stopped on an API rate limit, which reset at 20:30. In that window the v3_final sweep finished (120 chunks, 6,545 decisions), and v3_extra_ds, v3_extra_expgain and all v2/v3_extra flip files were built.
- 20:31 The user said carry on. New stop 21:45. Resumed the runner (v3_final dataset, labels and flip), evaldev (finish the --levels check and give the final commands) and the experimenter (write EXPERIMENTS.md).
- 20:32 evaldev: split-by-level plus merge is identical to the single run. The final commands are ready (three levels in parallel, about 15 to 25 min). Waiting on the runner.
- 20:33 experimenter done (`experiments/EXPERIMENTS.md`). signed_mse_abstain gives mid +0.010 and high +0.018 on val and test (CI above 0), with low noise null; the curve no longer falls; harm at budget 0.1 drops from 0.036 to 0.003. Calibration, softmax-none and tool weights add nothing; pairwise is a weak maybe; trees not run (no sklearn). Added S4 to PREREG (amendment 2) before any final output.
- 20:36 The v3_final inputs are complete (4,903 rows each). The experimenter's S4 command is ready, and it reproduces its val/test numbers exactly. Told the runner to launch the final runs: three eval levels plus S4 in parallel, then the merge, then the VLM controls one at a time.
- 20:37 Launched synthesis (REPORT.md). It drafts now and fills the final numbers when they land, or marks them pending at 21:30.
- 20:41 **Final test done** (`out/v3_eval/triggers_final.json`, `final/s4_signed.json`). n_train 34,718; final split 4,903 rows.
  - **H1 holds.** plandiscrim minus margin: +0.093 [0.085, 0.101] low, +0.080 [0.071, 0.088] mid, +0.071 [0.062, 0.079] high.
  - **H2 holds.** plandiscrim minus scene_only: +0.020 [0.016, 0.025], +0.021 [0.018, 0.025], +0.021 [0.017, 0.025].
  - **H3, descriptive.** plandiscrim reaches always-on accuracy at budget 0.60 (low), 0.50 (mid) and 0.35 (high).
    - Unsafe rate there against always-on: 0.324 vs 0.329 at low, 0.410 vs 0.410 at mid, 0.537 vs 0.494 at high. At high noise, accuracy is matched but the unsafe rate is worse.
  - **S1 false.** flip minus plandiscrim: 0.000 low, +0.003 [0.001, 0.005] mid, +0.001 [-0.000, 0.002] high.
  - **S4 holds.** signed_mse_abstain minus frozen: +0.010 [0.006, 0.014] mid, +0.018 [0.014, 0.021] high; low +0.004 [0.001, 0.007] is reported only.
  - The VLM controls are running in the background chain (/tmp/vlm_chain2.sh); the runner has finished.
- 20:42 docs agent added the final test to baseline_results.md, future_steps, SEEDS (760-859 now seen) and DECISIONS.
- 20:44 The synthesis agent's Write was refused for REPORT.md, so the manager assembled it from its two scratchpad drafts and fixed the repo path in the git block (~/CASS-VLA). Launched the report auditor.
- 20:48 Report audit: 49 confirmed, 3 wrong, 4 overstated, 1 unsourced; all verdicts and H3 numbers hold. Sent the fixes to the docs agent.
- 20:48 Report audit fixes applied (all 8). Waiting on the VLM controls.
- 21:10 VLM controls done.
  - shuffle: geometry+VLM beats geometry in 1 of 6 cells, so the gain disappears.
  - shuffle_family: 5 of 6 cells, small gains.
  - family one-hot: 6 of 6, with about a third to a half of the real gain.
  - Reading: part of the VLM gain is scene-family identity, and about half or more is extra image information. No CIs. Sent to the docs agent for phase5_vlm.md and REPORT.md.
- 21:11 Docs agent added the Controls section. The family label recovers 20 to 77% of the VLM gain by cell (49% overall), so about half is beyond family identity. Run complete; no jobs left running.
