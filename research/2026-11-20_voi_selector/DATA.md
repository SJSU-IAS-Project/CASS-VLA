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

The main dataset matches exactly. The extra-seed counts and the check that the harness reproduces Max's `signed`
numbers are added below once those runs finish.
