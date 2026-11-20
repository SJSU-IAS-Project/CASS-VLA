# Run 2 schedule and log (started 2026-11-19 22:45 PST, 3 h of active work)

Goal: a second pre-registered test on fresh seeds 1060-1159, with the signed-gain abstain selector as the
primary method and VLM features computed on HPC. After that, a slide deck and a report.

**Rules:** BRIEF.md applies, with these changes.
- HPC is allowed only for the hpc agent: one ControlMaster at `/tmp/claude-1000/cm-hpc1`, and g17 through `/tmp/cm-$USER/g17`.
- At most one GPU job, logged in `~/sjsu-hpc/communication/resources_sharing/CASS_VLA_GPU_JOBS.md`.
- No GitHub, no git writes.

| Agent | Job |
|---|---|
| runner | sweep seeds 1060-1159 into `out/v4_final`, then build the dataset, labels and flip features (local, heavy) |
| hpc | sync the code; render frames for `v3_extra` (train) and `v4_final`; one GPU job (embed and describe); pull `out/vlm_v3extra`, `out/vlm_v4final` |
| experimenter | on val and test only: signed-abstain fixes (tool offsets, VLM features, scene-only signed twin) |
| analyst | unsafe-rate CIs at the H3 points on the first final split; whether the signed model matches always-on at high noise |
| tester | the test suite, one file at a time |
| docs | a draft README in the required layout, in `run2/README_DRAFT.md` |

## Log
- 22:45 ControlMaster up; no CASS jobs queued. 7 GB available locally.
- 22:46 Launched runner (sweep 1060-1159), hpc, experimenter, analyst4, tester, docs (README draft).
- User rules for this run:
  - If the 5-hour limit hits, resume the agents after it resets.
  - Keep the weekly usage below 80%. The manager can't read the meter, so it keeps the agent count lean: no new fan-out beyond this schedule, the deck and the report.
- 22:49 README draft done: 600 words, 0 lint hits. To fix in the final docs pass: its See-it command uses the glob out/v3_flip/*.jsonl. The exact flip list is the four files v2_sweep, v2_extra, v3_extra and v3_final; the glob would also catch v4_final.
- 22:56 analyst4 done (`analysis4/H3_POSTHOC.md`). Post hoc, on the first final split:
  - plandiscrim's unsafe rate at the accuracy-match budget, minus always-on: -0.005 at low, 0.000 at mid, +0.043 [0.030, 0.056] at high.
  - signed_mse_abstain matches always-on's unsafe rate at high noise from 0.45 calls, and is clearly safer from 0.5.
  - At 0.6 calls it is safer at all three levels (low -0.014 [-0.022, -0.006]; mid and high negative at 0.5 and 0.7).
  - Its accuracy match is stable (0.57/0.48/0.33 on a 0.01 grid); the unsafe match is more fragile for plandiscrim.
  - Plan: PREREG2 gets a fixed-budget H3 for the signed model at 0.6 calls per decision (20% of always-on).
- 22:58 tester: all 30 tests in 5 files pass. test_label_does_not_depend_on_history took 551 s under load.
- 01:31 Resumed after the 5-hour limit (it hit about 23:20 and reset at 01:30). The v4_final sweep is done (4,922 retained). Resumed the runner (dataset, labels, flip), hpc (check render 158982, then the v4 render and GPU) and the experimenter (finish B, write EXPERIMENTS2). The tester and analyst4 were stopped after finishing.
- 01:37 runner: v4_final_ds, expgain and flip all have 4,922 rows. Waiting on the experimenter's report before writing PREREG2. The HPC agent is rendering v4.
- 01:39 experimenter2 done (`experiments/EXPERIMENTS2.md`).
  - A (tool offsets, hybrid) and D (eps threshold) are null.
  - B (signed + VLM) is +0.008 to +0.015 in all 6 cells, CI above 0.
  - C (scene-only signed) is 0.023 to 0.036 worse.
  - Wrote PREREG2.md (P1-P4, Q1, Q2) before any v4_final evaluation. Asked the experimenter for the final harness and the commands.
- 01:51 Final harness ready (final.py): neutral on val/test (27/27 cells), fake-final path checked, refuses missing embeddings. Told the runner to launch the geometry final (P1-P4). Q1 waits for out/vlm_v3.
- 01:55 **PREREG2 geometry final: all four primary hypotheses pass** (`out/v4_eval/final_geom.json`; n_train 34,718, n_test 4,922).
  - **P1**, signed minus frozen: +0.009 [0.006, 0.012] mid, +0.019 [0.016, 0.023] high.
  - **P2**, signed minus signed_scene: +0.017, +0.023, +0.026, all CIs above 0.
  - **P3**, signed minus margin: +0.103, +0.096, +0.091.
  - **P4**, at 0.6 calls (20% of always-on):
    - accuracy minus always-on: +0.006 [-0.002, 0.016] low, +0.031 mid, +0.066 high;
    - unsafe minus always-on: -0.013 [-0.021, -0.005] low, -0.025 mid, -0.034 high;
    - so it is safer at every level.
  - Q1 is waiting for the VLM embeddings.
- 01:56 Publishing the deck to claude.ai was denied by the permission check, so the deliverables are built as local files in `deliverables/` (pptx and PDF). Launching the figures, deck and report agents.
- 02:01 Figures done. The x-axis bug (budget x 3) was caught by the manager, fixed by the agent and checked visually by the manager on f1_pareto_mid.
- 02:01 The report agent's Write was blocked, so it returns the template text and the manager writes it. SEEDS.md: 1060-1159 marked seen.
- 02:04 Manager extracted the report template from the agent's transcript to deliverables/report/report.tmpl.md (5,825 words) and fixed the seeds row. Resumed the report agent to build the HTML and PDF.
- 02:05 Deck built: 29 slides (17 main, 12 backup) as HTML, PDF and pptx. Manager checked slide 9. Sent the K fix (up to 6 candidates, not 3 to 5) and asked for conservative pptx text boxes.
- 02:05 Deck K fix rebuilt (29 slides; pptx boxes wrap and shrink).
- 02:09 Report built: 12 A4 pages (report.md, html, pdf). Agent fixed the f4 and f5 captions. Launched the deliverables auditor (report and deck).
- 02:13 Deliverables audit: 4 wrong, 17 overstated, 1 unsourced; all pre-registered numbers and verdicts confirmed. Fixes sent to the report and deck agents.
- 02:14 Report audit fixes applied (12 items), rebuilt, still 12 pages.
- 02:14 Deck audit fixes applied and rebuilt (29 slides). Waiting on GPU job 159857 for Q1.
- 02:35 hpc done. GPU job 159857 ran 32 min on cs001 with exit 0; out/vlm_v3 is pulled (14,604 rows) and logged in CASS_VLA_GPU_JOBS.md. Told the runner to run Q1.
- 02:40 **Q1 passes** (out/v4_eval/final_vlm.json): signed_vlm minus signed is +0.016 [0.013, 0.020] low, +0.012 [0.008, 0.015] mid, +0.010 [0.007, 0.013] high. Sent to the deck, report and docs agents.
- 02:40 Deck updated with Q1 (slides 8 and 14, caveat kept), rebuilt.
- 02:41 Docs updated for the second final and Q1 (baseline_results, phase5_vlm, DECISIONS, RUNNING).
