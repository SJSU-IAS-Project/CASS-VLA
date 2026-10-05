# Scenario suite (Phase 1)

`cassvla/scenarios/` scripts the six scenario families from
[`refined_proposal.md`](refined_proposal.md) section 4 on top of MetaDrive's
procedural maps, and adds the two things PG maps lack: traffic signals and
scripted hazards. Everything runs headless, is seeded per episode, and exposes
its state through plain dicts so the oracle labeller (Phase 2/4) never has to
touch Panda3D objects.

```python
from cassvla.scenarios import make_env, FAMILIES

env = make_env("occluded_cross_traffic", seed=0, num_scenarios=50)
obs, info = env.reset(seed=7)           # start_seed <= seed < start_seed + num_scenarios
obs, r, term, trunc, info = env.step([steer, throttle])
env.signals.get_state()                 # light phases, see below
env.hazards.get_state()                 # scripted actors, triggers fired
```

```bash
python scripts/run_scenarios.py                       # every family, 3 seeds, summary table
python scripts/run_scenarios.py --family ambiguous_light --seeds 10 --frames   # + PNGs in out/scenarios/
python -m pytest tests/test_scenarios.py              # 7 fast headless checks
```

## Families

| family | map | hazard script | signals |
|---|---|---|---|
| `occluded_pedestrian` | SS | car parked in the right lane at 20–30 m; a pedestrian hidden on its far side walks left across the road once the ego is within 12–20 m | none |
| `occluded_cross_traffic` | X | large truck parked at the near-right corner hides the south arm; a red-light runner launches from the south arm so that its arrival at the conflict point matches the ego's (lead ±1.2 s); 50% also a law-abiding IDM car queued on the north arm | ego axis green, cross axis red |
| `ambiguous_light` | X | 50% an IDM lead car; the ego light goes green→yellow→red (or red→green) at a random time 2.5–8 s, i.e. around the ego's arrival at the stop line | scripted per seed |
| `lead_brake_cutin` | SS | 50% a lead in the ego lane brakes to a stop (5–8 m/s²) when the ego is within 10–16 m; 50% a neighbour cuts into the ego lane and slows | none |
| `lane_blockage` | SS | stalled car + cones in the ego lane at 26–36 m; an overtaker closes in the left lane at 11–15 m/s; 40% the right lane is blocked by a truck too | none |
| `merge_closing_speed` | SS | slow lead (2.5–4.5 m/s) in the ego lane; fast closer (13–18 m/s) coming up the left lane | none |

The ego always spawns on the middle lane `(">", ">>", 1)` at 5 m; the 40 m
approach is `(">>", ">>>", k)`. On X maps the ego's destination is the
straight-through exit `1X1_1_`.

## Signals (`SignalManager`)

MetaDrive's PG maps ship no lights and no light manager (lights exist only for
replayed real-world scenarios). `SignalManager` spawns a `BaseTrafficLight` on
every lane leaving every approach of the first X/T block (X: 4 approaches × 3
exits × 3 lanes = 36 lights), groups approaches into `ego` (parallel to the ego
approach) and `cross`, and drives phases from a schedule.

`signal_config` (env config): `enabled`, `mode` (`cycle` or `scripted`),
`green`/`yellow`/`all_red` seconds and `offset` for cycle mode, or `schedule`
as `[(t_start, ego_status, cross_status), ...]` for scripted mode.

`env.signals.get_state()`:

```python
{"t": 6.3, "ego_status": "TRAFFIC_LIGHT_GREEN", "cross_status": "TRAFFIC_LIGHT_RED",
 "approaches": {">>>": "ego", "-1X0_0_": "cross", "-1X1_0_": "ego", "-1X2_0_": "cross"},
 "lights": {"('>>>', '1X1_0_', 0)": "TRAFFIC_LIGHT_GREEN", ...},
 "stop_points": {"('>>>', '1X1_0_', 0)": (55.0, 7.0), ...}}
```

`env.signals.status_of_lane(lane_index)` gives one lane's status. The ego's
own collision flags `env.agent.red_light` / `yellow_light` are set by MetaDrive
when it crosses a stop line on red/yellow. IDM traffic vehicles obey the lights.

## Hazards (`HazardManager`)

Hazard types in `hazards.py`:

- `ParkedVehicle` – frozen vehicle (`set_break_down` + `set_static`), optionally XL.
- `Barrier` – cones or barriers across a lane.
- `CrossingPedestrian` – stands still until the ego is within `trigger_dist`, then walks `walk_dist` m.
- `KinematicVehicle` – driven by setting its velocity along a lane each step; an
  ordered list of events (`t`, `ego_within`, `ego_near`, `eta_match` triggers)
  changes its target speed, acceleration or lane. Used for runners, braking
  leads, cut-ins and fast closers.
- `IDMVehicle` – ordinary MetaDrive traffic vehicle with the IDM policy.

`env.hazards.get_state()` returns `{"family", "t", "hazards": {name: {...}}}`
with per-actor position, speed, and what has triggered (`fired` for kinematic
vehicles, `triggered_t` for pedestrians).

## Determinism

Every random draw comes from the manager's `np_random`, which MetaDrive seeds
from the episode seed, and from a seed-derived generator for the per-seed
signal schedule. `tests/test_scenarios.py::test_replay_is_deterministic`
checks that two runs of the same seed produce bit-identical ego and runner
traces, which is what the oracle rollout relies on.

## Gotchas found while building this

- MetaDrive's managers get a legacy `numpy.random.RandomState` (`randint`, not `integers`).
- A vehicle spawned on a negative-direction road (e.g. `-1X0_1_`) without an
  explicit `destination` crashes MetaDrive's auto route assignment with
  `list.remove(x): x not in list`. All intersection hazards set one.
- A velocity command on a Bullet vehicle takes about 0.5 s to take full
  effect; `KinematicVehicle.launch_lag` compensates in the ETA trigger.
- The ETA trigger must include the ego's measured acceleration, otherwise a
  throttle-happy ego arrives ~1 s early and the conflict never happens.

## Known limitations

- Hazards are blind to the ego except through their triggers; they do not
  react to it. That is intended: the oracle needs non-reactive futures.
- `KinematicVehicle` overrides physics each step, so it will push through
  obstacles rather than stop for them. Use `IDMVehicle` where realism matters.
- Only the first X/T block gets signals; multi-intersection maps are not handled.
- Frames from `--frames` are top-down only; the 3D camera is not used in Phase 1.
