# Phase 2: candidate generator and oracle scoring

Code in `cassvla/planning/`; CLI `scripts/run_oracle.py`; tests `tests/test_oracle.py`.

```python
from cassvla.planning import Oracle
oracle = Oracle("lane_blockage", start_seed=0, num_scenarios=4)
rec = oracle.label(seed=2, t_dec=1.5)     # one decision point
rec["c_star"], rec["oracle_order"], rec["metrics"]["keep"], rec["retained"]
```

## Decision point

A decision point is `(family, seed, t_dec)`. The ego reaches it by driving a
hazard-blind **cruise prefix** (lane keep, accelerating at 2 m/s² towards
8 m/s), and the prefix actions are recorded. If the prefix itself ends the
episode (e.g. it drives into the stalled car), the decision is skipped.

## Candidates (`candidates.py`)

| name | maneuver |
|---|---|
| `keep` | hold current speed (min 3 m/s) |
| `keep_fast` | +3 m/s (cap 15) at 2 m/s² |
| `decelerate` | to half speed at 2.5 m/s² |
| `stop` | to 0 at 4 m/s² |
| `change_left` / `change_right` | adjacent lane, current speed, 3 s smoothstep blend; only if the lane exists |

Each is a time-indexed reference (t, xy, heading, speed) at 0.1 s over a 5 s
horizon. Paths follow lane "chains": the current lane index carried along
`navigation.checkpoints`, so they go through intersections on the ego's route.

## Execution (`control.py`)

Candidates are driven, not teleported: pure pursuit for steering plus a speed
P controller with feed-forward and along-track correction. On straight roads
tracking error is under 0.5 m along-track and 0.35 m laterally (lane change).
Each rollout reports its tracking error so a badly tracked candidate is visible.

## Oracle (`oracle.py`)

Each candidate is scored by **re-simulation**: reset the seed, replay the
prefix actions, drive the candidate. A single logged actor future would be
wrong here because the hazard triggers react to the ego (pedestrian distance
trigger, the runner's ETA match, `ego_within` brakes and cut-ins).

Per step, against every non-ego object except traffic lights: polygon
clearance, constant-velocity TTC, MetaDrive crash flags, `red_light`, and
out-of-road / sidewalk.

- **safe**: no collision, red light or off-road, clearance ≥ 0.5 m, TTC ≥ 1.0 s
- **score**: progress (m along the candidate path) − 1000·collision −
  500·red − 500·off-road − 20·max(0, 1.5 − TTC) − 20·max(0, 1.0 − clearance)
- **oracle order**: safe candidates first, then by score; `c*` is the first
- **retained**: at least one safe and one unsafe candidate (refined proposal §3)

Each record also logs the ego state, hazard and signal state, prefix actions,
and all candidate paths, per the "log everything per decision" note in
`future_steps.md`. About 0.5 s per decision (6 rollouts), about 11 KB of JSON.

## First sweep (seeds 0–1, t_dec 0.5–6.0 s)

As the ego approaches the hazard, `c*` moves from `keep_fast` to a lane
change or `decelerate`, then to `stop`, and finally to no safe candidate. Only
the middle of that range is retained, which is the intended behaviour.

## Known gaps

- `lead_brake_cutin` seed 1 never produces an unsafe candidate before 6 s,
  because the slow cruise prefix keeps the gap open. Per-family decision
  windows (or a faster prefix) are needed before generating the dataset.
- Rule compliance covers only red lights. There are no lane-line or
  speed-limit rules, and no comfort term.
- Resetting the same env is not bit-identical (about 1e-5 m drift after 50
  steps; a fresh env is). All rollouts of a decision share one env, and
  repeated labels agree to within 0.05 in score.
- TTC is constant-velocity, measured edge to edge, and is a proxy only.
