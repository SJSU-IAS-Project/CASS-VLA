# CASS-VLA

CASS-VLA picks the one perception tool that a driving planner should call before it commits to a trajectory. It is for researchers of active perception under a call budget.

## Problem

A planner often has several candidate trajectories that look equally good until one detail is checked, such as an occluded car.

- Calling every tool on every decision costs 3 calls each.
- Calling none leaves the ambiguity in place.
- Triggers based on the scene, or on how confident the planner is, spend calls where no tool helps. On the final split at mid noise and budget 0.1, 0.416 of the margin trigger's calls do harm.

## Solution

CASS-VLA reads the candidates and picks one tool (ROI inspection, depth or collision check) or none. At low and mid noise it matches always-on accuracy with 0.60 calls per decision at low noise and 0.50 at mid.

1. Condition on the candidate trajectories, not only on the scene.
2. Train on oracle labels from MetaDrive ground truth, so every decision has a known best candidate.
3. Score each tool by expected gain, and skip the call when no gain is positive.

## See it

The selector (`plandiscrim`) is scored at mid noise on the final test. That test uses 100 seeds nothing was tuned on. The output is copied from `out/v3_eval/final/triggers_final_mid.log`.

```sh
python scripts/eval_triggers.py --data out/v2_dataset --extra-train out/v2_extra_ds out/v3_extra_ds \
  --expgain out/v2_expgain.jsonl out/v2_extra_expgain.jsonl out/v3_extra_expgain.jsonl out/v3_final_expgain.jsonl \
  --flip out/v3_flip/*.jsonl --test-data out/v3_final_ds --splits final --levels mid \
  --out out/v3_eval/final/triggers_final_mid.json
```

```text
final mid  n=4903  random 0.3265  uncertainty_margin 0.3543  ego_speed 0.3390  candidate_spread 0.3390  fixed_schedule 0.3358  scene_only 0.4123  candidate_only 0.4287  plandiscrim 0.4338  plandiscrim_flip 0.4367  fair_ceiling 0.4726
```

## Why not always-on, a margin trigger or scene-only

Accuracy means the ranker's top candidate equals the oracle's best after the call. Numbers are for mid noise, over 4,903 final decisions.

| Policy | Mean accuracy, budgets 0 to 1 | Calls to reach always-on accuracy (0.486) |
|---|---|---|
| Always-on | n/a | 3 |
| Margin trigger | 0.354 | never |
| Scene-only selector | 0.412 | 0.75 |
| Selector | 0.434 | 0.50 |

At 0.50 calls the selector is unsafe on 0.410 of decisions, as is always-on. It leads the margin trigger by +0.080 and the scene-only selector by +0.021, with 95% intervals above 0.

## Install

You need [uv](https://docs.astral.sh/uv/). From the repository root:

```sh
./scripts/setup.sh
source .venv/bin/activate
```

The first run downloads 200 MB of MetaDrive assets.

## Usage

Run the scenario families:

```sh
python scripts/run_scenarios.py
```

Label decisions and build the splits:

```sh
python scripts/run_sweep.py --out out/sweep --start-seed 100 --seeds 300 --procs 8
python scripts/build_dataset.py --sweep out/sweep --out out/dataset --procs 8
```

Compare the selector with the triggers:

```sh
python scripts/eval_triggers.py --data out/dataset --expgain out/expgain.jsonl --out out/triggers.json
```

## Status

The open-loop pipeline works, with six scenario families, three tools, oracle labels and cached VLM features that add 0.003 to 0.007 accuracy. At high noise the selector matches always-on accuracy at 0.35 calls, but its unsafe rate is 0.537 against 0.494. It needs 0.60 calls to match both. These results match the oracle's choices and are not collisions. Calibration and closed-loop tests are next, see [docs/future_steps.md](docs/future_steps.md).

---

## Development

```sh
python -m pytest tests/test_scenarios.py
```

The full suite takes 5+ minutes. Set `OMP_NUM_THREADS=1` before evaluating, or numpy runs far slower.

## Layout

- `cassvla/`: scenario families, planning, oracle and tools.
- `scripts/`: sweeps, datasets, evaluation and plots.
- `tests/`: checks for scenarios, oracle and tools.
- `docs/`: proposals and results, starting with [docs/baseline_results.md](docs/baseline_results.md).
- `out/`: data and run outputs, ignored by git.

## License

MIT, see [LICENSE](LICENSE).
