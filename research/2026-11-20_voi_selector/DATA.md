# Data for the VoI selector work (on an Apple Silicon Mac)

Max's `out/` bundle was not on this machine, so the data were regenerated from the code on branch
`eshan/voi-selector` (Max's `max` branch plus the merge) with the commands below, 8 processes.

```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/run_sweep.py --out out/v2_sweep --start-seed 100 --seeds 300 --chunk 5 --procs 8
.venv/bin/python scripts/build_dataset.py --sweep out/v2_sweep --out out/v2_dataset --procs 8
.venv/bin/python scripts/label_expected_gain.py --sweep out/v2_sweep --out out/v2_expgain.jsonl --draws 8 --procs 8
# seeds 460-759 -> out/v2_extra_sweep, out/v2_extra_ds (--as-split train), out/v2_extra_expgain.jsonl
# seeds 860-1059 -> out/v3_extra_sweep, out/v3_extra_ds (--as-split train), out/v3_extra_expgain.jsonl
```

## Counts checked against Max's records

| Item | Regenerated here | Max (`docs/baseline_results.md`, `docs/phase5_vlm.md`) |
|---|---|---|
| `v2_dataset` train rows | 10,329 | 10,329 |
| `v2_dataset` val rows | 2,222 | 2,222 |
| `v2_dataset` test rows | 2,235 | 2,235 |
| Seeds per split | 210 / 45 / 45 | 210 / 45 / 45 |
| `v2_expgain.jsonl` rows | 14,786 (all retained decisions) | — |

| `v2_extra_ds` train rows (seeds 460-759) | 14,707 | 14,707 |
| Train rows for run-1 experiments (main + extra) | 25,036 | 25,036 |

## Reproducing Max's learned-selector numbers

With the run-2 harness on 25,036 training rows (`out/voi_eval/repro_signed_25k.json`, `repro_frozen_25k.json`):

| Validation, mean accuracy over budgets | Low | Mid | High |
|---|---|---|---|
| `signed`, here | 0.5073 | 0.4500 | 0.3762 |
| `signed`, Max (`experiments/res_signed_mse_abstain.json`) | 0.5222 | 0.4648 | 0.3863 |
| `frozen`, here | 0.5023 | 0.4385 | 0.3586 |
| `frozen`, Max (`experiments/res_frozen.json`) | 0.5166 | 0.4543 | 0.3683 |

Row counts match exactly, but both learned selectors come out about 0.010-0.016 lower here. The training code is the
same (both harnesses fit `signed` on all train rows). The likely cause is code drift: Max's commit `cb00257`
("fix hazard placement and features") changed `features.py`, `hazards.py`, `tools.py` and `families.py` and was
committed together with his result files, so his `out/` data may predate it. This is not resolved. Every comparison
in this folder uses the regenerated data and the same code for all methods, so it is internally consistent; to
confirm, rerun `scripts/eval_voi.py` on Max's own `out/` bundle.
