# Inventory, 2026-11-19 (read-only survey; everything below marked PROPOSAL is for the human)

`out/` is 2.1 GB, 53 top-level entries, and is gitignored (`.gitignore: out/`). No licensed data is in this repo
(Long2RAG absent); nothing in `out/` has licensing concerns. Sources for "produced by": `out/*_run.sh`, `out/*.log`,
`.agents/skills/doc/references/SEEDS.md`, `docs/baseline_results.md` (Data and commands sections), script docstrings.

## 1. out/

### Current (v2/v3 pipeline)
| Entry | Size | Produced by | Note |
|---|---|---|---|
| v2_sweep (+ .log) | 240M | `run_sweep.py --start-seed 100 --seeds 300` via `v2_run.sh` | raw records, seeds 100-399; needed by `flip_features.py`, `label_expected_gain.py` |
| v2_dataset | 60M | `build_dataset.py` on v2_sweep | train/val/test, main dataset |
| v2_expgain.jsonl (+ .log) | 3.2M | `label_expected_gain.py --draws 8` | expected-gain labels, main |
| v2_extra (+ .log) | 241M | `run_sweep.py` seeds 460-759 | raw extra sweep |
| v2_extra_ds | 60M | `build_dataset.py --as-split train` | extra train |
| v2_extra_expgain.jsonl (+ .log) | 3.2M | `label_expected_gain.py` on v2_extra | |
| v2_final (+ .log), v2_final_ds | 48M, 12M | seeds 400-459 via `v2_run.sh`, build_dataset `--as-split final` | SEEN final split; never reuse as a test |
| v2_eval | 304K | `eval_baselines.py`, `eval_vlm.py` | final/test/val.json, vlm*.json, control logs |
| v2_frames (+ .log, guard/run .sh, guard.log) | 96M | `render_frames.py` on v2_final_ds | input to the VLM pass |
| vlm_main | 424M | `vlm_encode.py` (HPC GPU job, copied back) | embed.npz, describe/prompt jsonl; needed by `eval_vlm.py` |
| vlm_extra | 352M | `vlm_encode.py` for extra seeds | extra-train VLM features |
| v3_extra (+ .log) | 160M | `run_sweep.py` seeds 860-1059 via `v3_run.sh` | complete (9,682 retained); no dataset or labels yet |
| v3_final (+ v3_final.log) | 6.6M | `run_sweep.py` seeds 760-859 | INCOMPLETE: stopped at 607 MB free, 15 of 120 chunks in the last log line; 9 `.tmp` partial chunks. Pre-registered final test: do not open labels. |
| v3_eval | 60K | `eval_triggers.py` | triggers.json |
| v2_analysis, v2_audit.json, v2_*_eval.txt, v2_decomp_val.txt, v2_more_data.txt | ~60K | analysis notes from the 2026-11-06 session | small result text; keep (v2_more_data.txt holds the 210 vs 510 seed gaps) |
| v2_windows_tune/val (+ .log) | 16M + 17M | window rule on tuning/validation seeds, v2 | CURRENT-ish: referenced by DECISIONS.md (windows rule); keep until docs agent confirms |

### Superseded (v1 pipeline, before the 2026-11-05/06 fixes)
| Entry | Size | Evidence |
|---|---|---|
| sweep | 242M | v1 `run_sweep.py --out out/sweep` (docstring example); replaced by v2_sweep |
| dataset | 50M | v1 `build_dataset.py --out out/dataset` |
| eval | 100K | v1 `eval_baselines.py --out out/eval` |
| baseline | 2.2M | v1 per-family baseline runs (.jsonl/.log/.time) |
| phase2_tune, phase2_val | 15M + 8.2M | phase 2 tuning/val; no doc mentions them |
| windows_tune, windows_val | 16M + 16M | v1 counterparts of v2_windows_* |
| sweep_stale_lane_blockage, sweep_audit.json | 26M + 60K | audit of a stale lane_blockage sweep, before the stale-cone fix (commit 2ffa54c) |
| bench | 36M | p8/p16/dev throughput benchmarks |
| hpc_test_ds | 48K | small HPC smoke-test dataset (still referenced by HPC notes? grep found no doc mention) |

None of the superseded names appear in docs/*.md, README.md or references/*.md (grep), so deleting them breaks no
documented command. v1 numbers in `docs/baseline_results.md` were replaced by the rewrite on 2026-11-06.

### Scratch
- session_scratch 5.7M (probe*.py, an.py, verify.py, job lists, xargs logs), plus the `.sh` and `.done` files
  (`v2_run.sh`, `v3_run.sh`, `v2_frames_run.sh`, `v2_frames_guard.sh`, `v2_run.done`, `v3_run.done`) and `*.log`. The two
  `*_run.sh` files are the only record of exact sweep seeds/procs; keep them or copy the lines into SEEDS.md/RUNNING.md first.
  `v3_run.done` exists although `v3_final` is incomplete (the script's `echo done` runs after both sweeps return, whatever the
  stop reason), so the `.done` marker is misleading.

## 2. scripts/
Docstrings all hold example command lines (the word "usage" appears only in run_sweep.py), so "has usage" below means an example command.
| Script | Does | In docs? | Example cmd |
|---|---|---|---|
| build_dataset.py | sweep to seed-split dataset | yes (2) | yes |
| check_setup.py | four-step MetaDrive setup check | no | yes |
| eval_baselines.py | accuracy vs budget for all policies, fits frozen MLP | yes (2) | yes |
| eval_triggers.py | simple triggers vs learned selectors, harm/benefit | NO | yes |
| eval_vlm.py | do cached VLM features help the selector; `--control` | yes (1, phase5 only) | yes |
| flip_features.py | counterfactual flip features from sweep | NO | yes |
| label_expected_gain.py | expected-gain labels, 8 draws | yes (3) | yes |
| plot_pareto.py | Pareto plot from eval json | yes (1) | yes |
| probe_state.py | phase-1 MetaDrive state probe | yes (1) | yes |
| probe_window.py | macOS Panda3D window diagnosis | yes (1) | yes |
| render_frames.py | front-camera frame per decision | yes (3) | yes |
| run_oracle.py | candidates + oracle scores over grid | yes (1) | yes |
| run_scenarios.py | run every family headless | yes (2) | yes |
| run_sweep.py | resumable parallel labelling | yes (1) | yes |
| vlm_encode.py | embed/describe/choose with a VLM | yes (2) | yes |
| setup.sh | env setup | not checked | n/a |
| hpc/{render,render_test,vlm}.sbatch | cluster jobs | HPC.md | n/a (untracked) |
Undocumented: eval_triggers.py, flip_features.py, check_setup.py. Neither new script appears in README, RUNNING.md or baseline_results.md.

## 3. Stale docs: edits for the docs agent (use xewe_doc)
1. `docs/phase5_vlm.md`, "Not yet tried", bullet 1: "extra seeds 460-759 ... GPU job was still running" is out of date. Source: `out/v2_eval/vlm_extra_train.json` exists (extra-train run was done). Replace with its result; read the file for the numbers.
2. `docs/phase5_vlm.md`: add the control runs (`out/v2_eval/vlm_control*_*.log`, `eval_vlm.py --control`) and the prompted-choice result; mention `eval_vlm.py` commands for them.
3. `.agents/skills/doc/references/SEEDS.md`: the v3_final row should say the sweep is incomplete (15/120 chunks at last log line, `out/v3_final.log`, stopped on 607 MB free) and resumable; v3_extra row should say swept complete, 9,682 retained (BRIEF.md), no dataset yet.
4. `.agents/skills/doc/references/RUNNING.md`: add `eval_triggers.py` and `flip_features.py` commands (from docstrings), the stop-on-low-memory behaviour of `run_sweep.py` (v3_final.log) and that resuming skips finished chunks; note `v3_run.done` is written even after an early stop.
5. `docs/baseline_results.md`: Commands and Data sections stop at expected-gain and extra seeds; add v3 sweeps (`v3_run.sh`), `out/v3_eval/triggers.json`, and the flip features. Check its headline table vs `out/v3_eval/triggers.json` (no uncertainty-trigger comparison exists in the doc). Its 210 vs 510 seed numbers match `out/v2_more_data.txt`.
6. `docs/phase5_vlm.md` line 4 and `docs/baseline_results.md`: cross-reference each other and the trigger results; neither mentions `eval_triggers.py`.
7. `docs/refined_proposal.md` (last edited 2026-11-04, predates the 2026-11-06 scan): sections 0, 2 (Motivation), 5 (Baselines), 10 (Limitations): apply `research/2026-11-06_cass_vla_sota/RELATED_WORK_DELTA.md` Part 1/2 (novelty claim narrowed to "selector choosing among several perception tools from candidate divergence, scored as accuracy vs budget"). Add the learned-selector baseline names used now (no tool, always-on, random, ranker-margin trigger, scene-only MLP, fair ceiling), as in BRIEF.md.
8. `docs/literature_survey.md` (2026-11-04): replace table rows, "SOTA observations", and "Gap addressed" per RELATED_WORK_DELTA.md (that note was written exactly for this file, plus the two proposal docs).
9. `docs/novelty_feasibility_audit.md` (2026-11-04) and `docs/proposal.md`: RELATED_WORK_DELTA names "two positioning documents"; apply the same weakened claims; mark proposal.md as superseded by refined_proposal.md.
10. `docs/future_steps.md` (2026-11-04): predates phases 3-5; refresh against current status (expected-gain done, VLM done, v3_final pending).
11. `docs/scenarios.md`, `docs/oracle.md`: modified 2026-11-06 and uncommitted; fine, but verify they reflect the 0.8 speed scaling (DECISIONS.md 2026-11-06).
12. `README.md`: no mention of `out/v2_*`/v3 layout or the new scripts; add a short results/layout pointer.
13. `.agents/skills/doc/SKILL.md`: index lists four references, matches the folder; description should add the trigger/flip scripts if RUNNING.md grows.
14. `.agents/skills/doc/references/DECISIONS.md`: add 2026-11-07 decisions if any (v3_final reserved as pre-registered single run; seeds 400-459 burned).

## 4. git
Branch `max`; 16 modified (380+/110-), ~15 untracked repo files, 145 untracked `research/2026-11-06_cass_vla_sota/listing_sweep/html*` files.
Groups:
- A code fixes: `cassvla/planning/{features,oracle,tools}.py`, `cassvla/scenarios/{families,hazards}.py`, `tests/test_hazards.py`, `tests/test_tools.py`
- B pipeline scripts: `scripts/{build_dataset,eval_baselines,plot_pareto}.py` (modified), plus new `label_expected_gain.py`, `render_frames.py`, `vlm_encode.py`, `eval_vlm.py`, `eval_triggers.py`, `flip_features.py`, `scripts/hpc/*.sbatch`
- C results docs: `docs/{baseline_results,oracle,scenarios}.md`, `docs/baseline_pareto.png`, new `docs/phase5_vlm.md`
- D agent notes: `.agents/skills/doc/references/{HPC,DECISIONS,RUNNING,SEEDS}.md`, `.agents/users/maxdokukin/handoffs/*`
- E research: `research/2026-11-06_cass_vla_sota/` small files (not the html), `verify_run*.log`, `research/2026-11-19_learned_selector/`
Proposed messages (PROPOSAL, text only):
1. `fix hazard placement and features, update tests` (A)
2. `add expected-gain labels, vlm and trigger scripts` (B)
3. `update baseline and phase 5 docs` (C)
4. `add agent notes and handoff` (D)
5. `add 2026-11-19 research notes` (E, after the run)
Do NOT commit: `research/2026-11-06_cass_vla_sota/listing_sweep/html*` (361M of fetched HTML, 145 files; not gitignored), `listing_sweep/fetch*.log`, `verify_run*.log`, `verify_cache.json` if large, anything under `out/` (already ignored). Check `papers.csv`/`raw/` (860K) are intended. Order: the `.agents` handoff HANDOFF.md modification should be committed with D.

## 5. Cleanup PROPOSAL (nothing was touched)
| Item | Size | Reason |
|---|---|---|
| out/sweep | 242M | v1 raw sweep, superseded by v2_sweep |
| out/dataset | 50M | v1 dataset |
| out/windows_tune + windows_val | 32M | v1 window runs |
| out/phase2_tune + phase2_val | 23M | undocumented phase 2 |
| out/sweep_stale_lane_blockage | 26M | pre-fix stale data |
| out/bench | 36M | benchmarks, scratch |
| out/baseline + out/eval | 2.3M | v1 |
| out/session_scratch | 5.7M | scratch |
| Subtotal v1 + scratch | about 417M | archive to a tarball outside out/ first, or delete after human review |
| research/2026-11-06_cass_vla_sota/listing_sweep/html | about 361M | regenerable fetches; move out of the repo tree or gitignore |
| out/v3_final/*.tmp | 9 files, small | partial chunks; leave, the resume logic uses them or recreates |
Keep: all v2_*/v3_*, vlm_main (424M) and vlm_extra (352M; large but needed by `eval_vlm.py` and costly to regenerate on the GPU), v2_frames (96M, input to VLM re-runs), `*_run.sh` files.
Suggestion: add a `listing_sweep/html/` line to `.gitignore`.

## 6. Test suite
Run once with `OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q tests` (6.4 GB available beforehand). It was killed by the 5-minute
timeout (user 4m35s) with no summary line, so there is NO pass/fail result. The suite is not light (MetaDrive scenarios); run it
on an idle machine or per file (`tests/test_hazards.py`, `tests/test_tools.py` were the changed ones).
Side note: `out/v3_final/*.tmp` count went 9 to 10 during the survey, so a sweep process may be running; `out/v3_final` may still be growing.
Also: out/v2_analysis holds decomp.py, more_data.py, lcurve.py (small analysis scripts, keep).
