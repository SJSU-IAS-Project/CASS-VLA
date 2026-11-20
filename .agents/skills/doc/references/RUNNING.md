# Running jobs on this machine

The machine has 16 usable cores, 8 GB of RAM and no swap.

- Export `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1` before sweeps and `eval_baselines.py`. Without them, one
  evaluation took more than 5 cores and ran many times slower.
- Sweeps use about 230 MB per process. 16 processes give about 12,500 decisions per hour.
- Frame rendering needs an X server: `Xvfb :99 -screen 0 1280x720x24 &`, then `DISPLAY=:99`.
- One `render_frames.py` worker peaks at about 4 GB. Three workers left 244 MB available, so run one worker.
  `out/v2_frames_guard.sh` stops the chain in `out/v2_frames_run.sh` below 700 MB available. It fired twice on 2026-11-06, next to one eval process and next to 8 `label_expected_gain.py` processes, so render alone.
- `camera.perceive(new_parent_node=...)` renders twice and took 4.3 s. `track` plus one `taskMgr.step()` plus
  `get_rgb_array_cpu()` gives the same image in about 1 s. Each `env.reset` with a camera costs about 2.3 s.
- A camera env did not finish building in 10 minutes while 16 sweep processes ran. Render on an idle machine.
- Stop a process pool by PID: `kill $(pgrep -P <parent>)`, then the parent. `pkill -f <pattern>` also matches
  the shell that runs it, which kills the command partway, and the pool workers are left orphaned.
- `scripts/run_sweep.py` stops starting work when available memory falls below `--min-free-mb` (default 800) and
  exits with "stopped: only N MB available". Finished chunks are kept, and running the same command again skips them,
  so a stopped sweep resumes in place. `out/v3_run.sh` writes `out/v3_run.done` after each command ends, even after an
  early stop, so the file does not mean that the sweep finished. Count `out/v3_final/*.jsonl` against 120 chunks instead.
- Simple triggers against learned selectors, with harm and benefit per budget:
  `python scripts/eval_triggers.py --data out/v2_dataset --expgain out/v2_expgain.jsonl --out out/v3_eval/triggers.json`.
  Add `--extra-train out/v2_extra_ds` and `--expgain out/v2_expgain.jsonl out/v2_extra_expgain.jsonl` to train on all
  25,036 rows, and `--flip out/v3_flip/*.jsonl` for the flip features. The docstring lists the final-test options.
- Counterfactual flip features: `python scripts/flip_features.py --sweep out/v2_sweep --out out/v3_flip/v2_sweep.jsonl --procs 8`.
  It reads the raw sweep records, so run it once for each of `out/v2_sweep`, `out/v2_extra` and `out/v3_extra`.
- Run the `eval_vlm.py --control` variants (`shuffle`, `shuffle_family`, `family`) one at a time. Three together next
  to a sweep ran out of memory on 2026-11-19, and one peaked at 3.7 GB resident.
- The pytest suite takes more than 5 minutes. Run it in the background or pick single test files.
