# Test run, run 2 (2026-11-19)

Command per file: `OMP_NUM_THREADS=1 timeout 900 .venv/bin/python -m pytest -q -x --durations=5 tests/<file>`, one file at a time, `free -m` available memory above 2 GB before each (5234 MB before test_hazards; 2434-2634 MB before the others). No conftest.py, pytest.ini or pyproject.toml; no slow/skip markers (only `parametrize`). No code or tests modified.

| File | Collected | Passed | Failed | Errors | Duration |
|---|---|---|---|---|---|
| tests/test_hazards.py | 11 | 11 | 0 | 0 | 600.7 s |
| tests/test_oracle.py | 4 | 4 | 0 | 0 | 27.2 s |
| tests/test_scenarios.py | 7 | 7 | 0 | 0 | 11.9 s |
| tests/test_tools.py | 6 | 6 | 0 | 0 | 21.0 s |
| tests/test_windows.py | 2 | 2 | 0 | 0 | 17.1 s |
| Total | 30 | 30 | 0 | 0 | about 678 s |

## Slowest tests
- test_hazards: `test_label_does_not_depend_on_history` 550.8 s; `test_reused_cones_start_at_rest` 21.0 s; `test_cut_in_reaches_ego_lane` 18.6 s; `test_record_logs_actor_state` 4.0 s.
- test_oracle: `test_label_is_repeatable` 16.2 s; `test_label_ranks_safe_first` 8.1 s.
- test_scenarios: `test_replay_is_deterministic` 2.1 s; the family build tests 1.0-1.7 s each.
- test_tools: setup of `test_perfect_tools_return_ground_truth` 18.4 s (fixture builds the oracle); calls under 0.5 s.
- test_windows: `test_lead_brake_window_reaches_hazard` 15.1 s.

## Failures
None, so no stale-test or real-bug diagnosis is needed. The code and tests changed last in commit cb00257 ("fix hazard placement and features, update tests"; touched cassvla/planning/{features,oracle,tools}.py, cassvla/scenarios/{families,hazards}.py, tests/test_hazards.py, tests/test_tools.py), and the suite passes against it.

## Note
`test_label_does_not_depend_on_history` took 550 s, close to the 900 s timeout. It labels a grid of 24 horizons on a reused env. The machine was shared with a 12-process sweep, so the time is likely inflated by load; on an idle machine expect it to be much faster. If the sweep keeps running, a loaded run could hit the timeout. I did not measure it idle.
