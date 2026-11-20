# Brief for every agent in the 2026-11-19 learned-selector run

Repo: `/home/user/CASS-VLA` (MS course project, CMPE 249). Today is 2026-11-19. The run ends at **20:30 PST**
(`TZ=America/Los_Angeles date`). Write your final report by your own stop time in your prompt.

## The project in one paragraph
A driving planner in MetaDrive has a scene and K candidate trajectories. A selector may call at most one
perception tool (`roi`, `depth`, `collision`) or none, under a call budget; a rule-based ranker then picks the top
candidate, scored against an oracle best candidate. The **learned selector** ("PlanDiscrim", Track A) is a fixed
MLP (`scripts/eval_baselines.py: fit_mlp`, settings frozen) on geometry plus candidate-divergence features
(`cassvla/planning/features.py`), trained on expected-gain targets (mean correctness over 8 noise draws). It is
compared with no tool, always-on, random, an uncertainty (ranker-margin) trigger, a scene-only MLP and a fair
ceiling, as accuracy vs call budget. The professor's test: similar or better safety decisions with far fewer calls
than always-on or generic uncertainty triggers. Read `docs/refined_proposal.md`, `docs/phase5_vlm.md`,
`.agents/skills/doc/references/{DECISIONS,SEEDS,RUNNING}.md` first.

## Data and results that exist
| Path | What |
|---|---|
| `out/v2_dataset/{train,val,test}.jsonl` | main dataset, seeds 100-399, 10,329 / 2,222 / 2,235 rows |
| `out/v2_extra_ds/train.jsonl`, `out/v2_extra_expgain.jsonl` | extra train seeds 460-759 |
| `out/v2_expgain.jsonl` | expected-gain labels for the main dataset |
| `out/v2_sweep`, `out/v2_extra`, `out/v3_extra` | raw sweep records (needed by `flip_features.py`, `label_expected_gain.py`) |
| `out/v3_extra` | swept 2026-11-07, seeds 860-1059, 9,682 retained; no dataset or labels built yet |
| `out/v3_final` | seeds 760-859, sweep **incomplete** (stopped on low memory); resumable, finished chunks are skipped |
| `out/v2_final_ds` | seeds 400-459: already SEEN, never use it as a test |
| `out/v2_eval/vlm*.json` | VLM-feature evals; `vlm_extra_train.json` is the extra-train run |
| `out/v3_eval/triggers.json` | simple triggers vs learned selectors on val/test, with harm/benefit split |
| `scripts/eval_triggers.py`, `scripts/flip_features.py`, `scripts/eval_vlm.py --control` | new scripts, 2026-11-07 |
| `research/2026-11-06_cass_vla_sota/REPORT.md` | literature scan (561 papers); do not redo it |

## Hard rules
- **No git writes** of any kind (commit, add, branch, stash, ...). Read-only git is fine.
- **No ssh, no HPC, no sbatch, no VPN.** No `sudo`. Don't touch `~/.ssh`, git config or tokens.
- **Memory:** the machine has 8 GB RAM, no swap, 16 cores. Only the compute-runner agent starts jobs that use
  more than 1 core or more than 500 MB. Everyone else runs light scripts only (a single eval process is OK only if
  your prompt says so). Always `export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`. Check `free -m` first; never
  start anything that would push available memory below 1.5 GB.
- **`out/v3_final` is the pre-registered final test.** Nobody evaluates on it unless the manager says so in a
  message. Don't open its labels to choose methods.
- Changing the frozen MLP settings or the VLM feature choice is tuning: allowed only as clearly labelled
  exploratory work on val/test, never on the final split.
- Write only to the paths your prompt gives you. Don't delete or move files you did not create in this run.
- Docs (`docs/`, READMEs, `.agents/skills/doc/`) are changed only by the docs agent, using the `xewe_doc` skill
  (which loads `xewe_write`). Prose for humans follows `xewe_write`.
- Never invent a number. Every number in a report must come from a file you can name.
- Report back: what you did, files written, key numbers with their source file, anything that went wrong.
