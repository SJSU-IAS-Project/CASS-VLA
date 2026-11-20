# Audit of REPORT.md (2026-11-19 learned-selector run)

Auditor: independent, read-only. Sources read: `out/v3_eval/triggers_final.json`, `out/v3_eval/final/*.json|log`, `scripts/eval_triggers.py`, `scripts/merge_trigger_runs.py`, `experiments/exp.py`, `out/v3_eval/triggers.json`, `out/v3_eval/dev/triggers_v2_flip.json`, `analysis*/`, `experiments/`, `inventory/`, `PREREG.md`, `PLAN.md`, `runner_status.md`, `git status`. Every number in sections 1-2 was recomputed from the JSON with a small python read. Key mapping: `results["final/<lv>"]`: `<policy>.mean_acc|curve|unsafe_curve|by_budget|by_family`, `always_on`, `h3_always_on`, `comparisons`; S4 in `s4_signed.json`: `results.signed_mse_abstain|frozen["final/<lv>/plandiscrim"]`.

## Checks you asked for

- (a) Verdicts follow PREREG exactly. H1 lower bounds 0.0849/0.0713/0.0615 and H2 0.0157/0.0181/0.0173 are all above 0, so both hold. S1 lower bounds -0.0022/0.0013/-0.0002 means S1 fails (all three needed). S4 lower bounds at mid 0.0062 and high 0.0141 are above 0, so S4 holds; low is 0.0006 (also above 0, reported only). The merged `hypotheses` key (H1 true, H2 true, S1 false) matches. CONFIRMED.
- (b) H3 recomputed from `curve`/`unsafe_curve` against `always_on` on the 0.05 grid. Accuracy reached at 0.60/0.50/0.35 (acc 0.5937/0.4900/0.3618). Both accuracy and unsafe at 0.60/0.50/0.60 (high at 0.35 has unsafe 0.5367 vs 0.4936, gap 0.0431; at 0.60 unsafe 0.4888). Mid unsafe 0.4103 vs 0.4104 (tie, margin 0.0001). All CONFIRMED. Caveat: the "both" budget is not a PREREG quantity (see item 6).
- (c) Timestamps. PREREG.md mtime 20:33; earliest final artefact `out/v3_final_ds/final.jsonl` 20:34:00, expgain 20:36:12, per-level eval json 20:38:54-56, `s4_signed.json` 20:39:40, `triggers_final.json` 20:41:30. So S4 (amendment 2, written 20:33) precedes every final dataset, label and eval output. The dev "fake final" is a copy of test (`out/v3_eval/dev/fake_final`, 18:19), not v3_final. CONFIRMED. Caveat: PREREG.md is a single mutable file, so the 18:03 and 18:08 stamps (original and amendment 1) cannot be verified from mtimes; `PLAN.md`/`runner_status.md` are consistent with them. Nothing other than S4 chosen on val/test is presented as confirmatory (flip features, signed family variants, H3 budget are all labelled exploratory or descriptive).
- (d) Harm rates, "17 of 18", S4 curve at 1.0 vs always-on, tool-optimal rate: see table, all CONFIRMED except the wording issues in items 2 and 6.
- (e) Git block. All paths exist. Nothing under `out/` is added (`out/` is gitignored, `.gitignore` line 7). `research/2026-11-19_learned_selector` is 1.5 MB with no file over 1 MB and no ignored files. No `listing_sweep/html*` path is added by any `git add`. Messages are one line, lowercase, 5 to 7 words, no attribution. No Long2RAG data: grep finds only mentions (REPORT, INVENTORY, `.agents` rules). The block is safe to paste, with the `.gitignore` problem in item 3.

## Findings table

| Section/line | Claim | Source | Verdict | Fix |
|---|---|---|---|---|
| 1 / L7 | 100 seeds, 4,903 decisions, nothing tuned on them | `n_test.final` 4903; `manifest.json` | CONFIRMED | |
| 1 / L7, 2 / L19-20 | H1 +0.071 to +0.093, H2 +0.020 to +0.021, all CIs above 0 | `comparisons` in 3 levels | CONFIRMED | |
| 1 / L7, 2 / L47-52 | Always-on matched at 0.35 to 0.60 calls vs 3; unsafe matched at low and mid; high needs 0.60 | `h3_always_on`, curves | CONFIRMED | |
| 1 / L7 | Margin trigger never reaches always-on at any level | margin curve max 0.5639/0.466/0.3533 below 0.5841/0.486/0.3586; min unsafe 0.3506/0.435/0.5315 above 0.3286/0.4104/0.4936 | CONFIRMED | |
| 1 / L7 | S1 fails, only mid CI above 0 (+0.0029) | `comparisons` | CONFIRMED | |
| 1 / L7 | S4 +0.0099 mid, +0.0175 high, CIs above 0 | `diff_vs_frozen` | CONFIRMED | |
| 2 / L11 | n_train 34,718, no flip rows missing, 1,000 resamples over seeds | `n_train`; logs ("0 without flip features"); `eval_triggers.py` L21, L220 | CONFIRMED | |
| 2 / L11, Files | S4 numbers come from `s4_signed.json` | file exists; the script that wrote it is not in the repo or the Files table (only a command in `PLAN.md`/`runner_status.md`) | UNSOURCED (producer) | Add the exact command or script path that wrote `s4_signed.json` to section 2 or 6. |
| 2 / L19-22 | All CI numbers in the verdict table | `comparisons`, `diff_vs_frozen` | CONFIRMED | |
| 2 / L24 | Frozen MLP in `s4_signed.json` reproduces plandiscrim means 0.4990/0.4338/0.3588 | `results.frozen` | CONFIRMED | |
| 2 / L28-40 | Mean-accuracy table (all 11 policies x 3 levels) | `<policy>.mean_acc`; S4 `mean_acc` | CONFIRMED | |
| 2 / L42 | "The simple triggers sit 0.01 to 0.03 above random, as on val and test" | low: margin +0.0223, ego +0.0067, spread +0.0068, fixed_schedule -0.0023; mid +0.0093 to +0.0278; high +0.0115 to +0.0176 | WRONG | Write "between 0.002 below and 0.03 above random (fixed_schedule is below random at low noise)". |
| 2 / L42 | knowno calls 99.76% to 100% at every level and alpha | `knowno.<a>.call_rate` 1.0/0.9982/0.9976 | CONFIRMED | |
| 2 / L48-52 | H3 table values (0.5841/0.3286, 0.4860/0.4104, 0.3586/0.4936; reached at 0.60/0.50/0.35; 20%/17%/20%) | `always_on`, `h3_always_on`, curves | CONFIRMED | |
| 2 / L46-52, L55, L58 and 1 / L7 | "First budget with accuracy and unsafe both matched" column, the 0.60 at high noise, and the fixed-budget-0.5 bullet | PREREG H3 defines only the accuracy-match budget and the unsafe rate there; the "both" column and budget 0.5 are post hoc reads of the final curves (Limits L148 admits 0.5 was not pre-registered) | OVERSTATED | Label the "both" column and the 0.5 bullet "post hoc, not in PREREG" in section 2 and in the L7 summary. |
| 2 / L54-55 | Mid margin 0.0001 is a tie; high gap 0.0431 at 0.35 | curves | CONFIRMED | |
| 2 / L56 | candidate_only 0.65/0.65, 0.55/0.60, 0.40/0.65; scene_only 0.75, 0.75, 0.55, unsafe matched only at low (0.75) | curves | CONFIRMED | |
| 2 / L57 | Margin accuracy at budget 1.0 is 0.5639 (low) vs 0.5841 | `curve[20]`; equals knowno acc | CONFIRMED | |
| 2 / L58 | At 0.5: acc 0.5647/0.4900/0.3935, unsafe 0.3490/0.4103/0.5030 vs 0.3286/0.4104/0.4936 | curves | CONFIRMED | |
| 2 / L59 | Peak at 0.65 at every level (0.5996/0.5146/0.4113), then 0.5763/0.4726/0.3613 at 1.0 | `curve` | CONFIRMED | |
| 2 / L65-75 | S2 harm/benefit table, 36 cells x 2 numbers | `by_budget.<b>.harm_rate|benefit_captured` | CONFIRMED | |
| 2 / L63 | Harm rate = share of made calls whose chosen tool has negative expected gain | `eval_triggers.py` L14, L97 | CONFIRMED | |
| 2 / L77 | Margin 41.6% harmful at mid, budget 0.1, vs 4.6%; plandiscrim high 5.8% to 11.5% vs 3.7% to 4.9% on test | final `by_budget`; `analysis/RESULTS.md` harm tables | CONFIRMED | |
| 2 / L85-90 | S3 per-family table (54 values) | `by_family` | CONFIRMED | |
| 2 / L92 | plandiscrim above scene_only in 17 of 18 cells, exception lead_brake_cutin low (0.300 vs 0.301) | `by_family` | CONFIRMED | |
| 2 / L92 | Gain largest for lane_blockage (+0.052 to +0.058) and occluded_pedestrian (+0.040 to +0.048) | `by_family` | CONFIRMED | |
| 2 / L100-105 | S4 table: mean acc, acc at 1.0, drop_after_0.65, harm at 0.1, mean unsafe, tool-optimal rate (S4 and frozen) | `s4_signed.json` | CONFIRMED | |
| 2 / L107 | S4 at budget 1.0 above always-on: 0.6024 vs 0.5841, 0.5205 vs 0.4860, 0.4293 vs 0.3586 | `acc_at_1.0`, `always_on` | CONFIRMED (at most one call per decision, since call needs predicted gain above 0; budget 1.0 is flat from 0.85/0.75) | |
| 2 / L108 | S4 spreads calls to collision "(0.352, 0.216 and 0.230 of calls, against 0.205, 0.081 and 0.064)" | `tool_share`; in `exp.py` L173 it is the share of all decisions whose argmax tool is collision, before any budget or abstain, so it is not a share of calls made | OVERSTATED | Say "collision is the predicted tool on 0.352, 0.216, 0.230 of decisions (frozen: 0.205, 0.081, 0.064)". |
| 2 / L108 | Tool-optimal rate lower than frozen at every level, as on val and test | 6 val/test cells in `experiments/tables.md`; 3 final | CONFIRMED | |
| 2 / L109 | S4 chosen on val/test, final test is its confirmation | PREREG amendment 2; timestamps | CONFIRMED | |
| 2 / L113 | Lead over scene_only inside val/test range +0.019 to +0.030 | `analysis2/FAILURES.md` T5 | CONFIRMED | |
| 3 / L120-123 | plandiscrim 0.333 to 0.517 vs margin 0.256 to 0.418; leads +0.076 to +0.099 and +0.019 to +0.030; 68% to 75% of gap closed; knowno 99.7% to 100% | `RESULTS.md` headline and gap tables; `FAILURES.md` T5; PREREG amendment 1 | CONFIRMED | |
| 3 / L126-129 | candidate_only beats scene_only by 0.011-0.026; scene adds 0.004-0.009; noise +-0.006; permutation drops 0.056/0.046, 0.045/0.036, 0.019/0.014; div_time 0.0067; flip -0.0004 to +0.0029, only test/low CI above 0 | `RESULTS.md`, `FAILURES.md` T7/T8/T5, `dev/triggers_v2_flip.json` (recomputed) | CONFIRMED | |
| 3 / L131 | Test harm 2.3-3.6% mid, 3.7-4.9% high; margin 17-37% and 20-45%; 3% vs 20.6% at 0.1 mid | `RESULTS.md` harm tables | CONFIRMED | |
| 3 / L134-137 | Peak near 0.65, 0.483 to 0.445; late calls harmful 26-46%, 4-10% of gain; 55-76% wrong decisions; depth 1,514 of 2,222, collision 130 vs best on 272; ambiguous_light loss inside CI | `FAILURES.md` T1, T4, T6, T10; `RESULTS.md` | CONFIRMED | |
| 3 / L139 | Professor's criterion on val/test: both matched at 0.50-0.65 calls, 17%-22% | `analysis3/SAFETY.md` T2c/T2d | CONFIRMED | |
| 3 / L141 | VLM +0.005 to +0.010 (25,036 rows), +0.003 to +0.007 (10,329); positive for all seeds; controls have logs only | `RESULTS.md` VLM table; `out/v2_eval/vlm_control_*.log` exist, no json | CONFIRMED | |
| 3 / L143 | signed_mse_abstain +0.010 mid, +0.018 high, CIs above 0; low unreliable; harm 0.036 to 0.003; calibration/softmax/toolw null; pairwise +0.004-0.005 high only; trees not run; nine variants | `experiments/EXPERIMENTS.md`, `tables.md` | CONFIRMED (the "nine" counts the 80% control as a variant) | |
| 4 / L147-156 | Limits (metric is not safety, same-split optimism, no unsafe CIs, VLM controls, tests killed at 5 minutes, README 585 words, audit found 15) | `SAFETY.md`, `INVENTORY.md` L125, `wc -w README.md` = 585, `AUDIT_docs.md`, `PLAN.md` 18:18 | CONFIRMED | |
| 5 / L161 | "The frozen model loses up to 0.07 accuracy by calling too much" | peak minus budget-1.0 for plandiscrim: val/test 0.022 to 0.063 (`triggers.json`), final 0.023 to 0.050 | OVERSTATED | "up to 0.06". |
| 5 / L163 | 24% to 45% of the gap to ceiling is wrong tool | `FAILURES.md` T4 part (b) | CONFIRMED | |
| 5 / L164 | Flip features "add nothing measurable" | final mid +0.0029 [0.0013, 0.0045], test/low CI above 0 on val/test | OVERSTATED | "add at most +0.003 and fail S1." |
| 5 / L166 | `lead_brake_cutin` is "the only one where a simple trigger can win" | `RESULTS.md`: occluded_cross_traffic loses to ego_speed at test/low (0.327 vs 0.334) and ties at test/mid; "largest family" and "lowest ceiling" are right | WRONG | "one of two families where a simple trigger can win (the other is occluded_cross_traffic)". |
| 6 | Files table paths | all listed paths exist (`out/v3_final_ds`, `v3_final_expgain.jsonl`, `v3_extra_ds`, `v3_flip`, scripts) | CONFIRMED | |
| 7 / L198 | About 417 MB of v1 outputs, `v3_run.done` is misleading | `INVENTORY.md` L118, L49; `out/v3_run.done` exists | CONFIRMED (not re-measured in full; spot du sweep 242M, dataset 50M, bench 36M, windows/phase2 about 56M) | |
| 7 / L199 | "`listing_sweep/html` holds about 361 MB ... not gitignored" and the `.gitignore` line `.../listing_sweep/html/` | `du`: `html` is 109 MB (45 untracked files); 361 MB is all of `listing_sweep`, whose other big folder `html_early` is 252 MB (100 untracked files) and is not covered by the line | WRONG | Say "`html` (109 MB) and `html_early` (252 MB)". Use `echo 'research/2026-11-06_cass_vla_sota/listing_sweep/html*/' >> .gitignore`. (No `git add` in the block picks them up, but `git status` would keep listing `html_early`.) |
| 7 / L202 | Commit list and "Long2RAG data is not in this repo" | no longrag data under `.agents`, `scripts/hpc`, `docs`, research folder (mentions only) | CONFIRMED | |
| 7 / L206-225 | Git block: paths exist, nothing under `out/` or `html*` added, messages lowercase one line <=10 words, no attribution | `ls`, `git status --short`, `git check-ignore` | CONFIRMED | Only fix is the `.gitignore` line above. |

## Tally

About 60 claims checked (table rows group related numbers; sections 1-2 numbers were each recomputed).

- CONFIRMED: 49 rows (including the hypothesis verdicts, H3 numbers, harm/benefit table, per-family table, S4 table, timestamps, git block paths and messages)
- WRONG: 3 (L42 "0.01 to 0.03 above random"; L166 "only one"; L199 "html holds 361 MB" plus the incomplete `.gitignore` line)
- OVERSTATED: 4 (L46-58/L7 post hoc "both" and 0.5 budget not labelled; L108 "of calls"; L161 "up to 0.07"; L164 "nothing measurable")
- UNSOURCED: 1 (producer script of `s4_signed.json`)

No verdict in section 1 or 2 changes after these fixes: H1, H2, S4 hold, S1 fails, H3 numbers stand.
