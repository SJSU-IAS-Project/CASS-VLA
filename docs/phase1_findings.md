# Phase 1 findings: MetaDrive setup and capability probe

Recorded 2026-10-05 from `./scripts/setup.sh --force --gui --probe --window`
on a MacBook Air M4 (macOS 15, Apple GL-on-Metal), Python 3.11.17, uv 0.12.

## Setup status

| check | result |
|---|---|
| headless env (`use_render=False`) | PASS, obs shape (259,) |
| cv2 / SDL2 | WARN (expected, see below) |
| Panda3D 3D window, single-threaded | PASS |
| top-down pygame renderer | PASS |
| deterministic replay (probe Q4) | PASS, max position diff 0.0 over 38 steps |

## Why MetaDrive is pinned to a git commit, not PyPI 0.4.3

PyPI 0.4.3 (2024-12-06) cannot open its 3D window on Apple Silicon:

1. It hardcodes `multisamples 8` for the window. Apple's GL compat context
   refuses that pixel format: `cocoadisplay(error): Could not find a usable
   pixel format`. 0x and 4x work.
2. One layer deeper it initialises simplepbr with `msaa_samples=16` for the
   offscreen tonemapping buffer, which fails the same way, so FilterManager
   returns None and init crashes with `'NoneType' object has no attribute
   'set_shader'`.
3. Its PBR shaders are GLSL 330 but the default Apple context is GL 2.1 /
   GLSL 1.20.

Upstream fixed all three for macOS in PR #794 (merged 2025-01-09): GL 4.1 core
context, 4x multisampling, GLSL 330 shaders across 12 files. No PyPI release
contains it, so `requirements.txt` pins main at commit `85e5dadc` (2025-05-12).
That commit still reports VERSION 0.4.3 and downloads the same `assets.zip`.
Side effect on all platforms: panda3d 1.10.16 instead of 1.10.13.

`scripts/probe_window.py` reproduces the diagnosis (bare Panda3D at 0/4/8x and
at `gl-version 4 1`, then MetaDrive with and without Panda3D debug logging).

## cv2 / SDL2 objc warnings on macOS

pygame and opencv-python each bundle libSDL2, so macOS prints
`objc: Class SDL... is implemented in both` at import. Harmless: the top-down
renderer passes with the collision present. Do NOT install
opencv-python-headless next to opencv-python; both own the `cv2/` directory
and uninstalling either deletes it. `setup.sh` filters these lines unless run
with `--verbose`.

## Scenario suite

Six scripted families (`cassvla/scenarios/`, documented in
[`scenarios.md`](scenarios.md)) run headless and deterministically;
`scripts/run_scenarios.py` and `tests/test_scenarios.py` exercise all of them.

## Capability probe answers (`scripts/probe_state.py`)

- **Actors (Q1).** 39 objects in a default scenario: 1 `DefaultVehicle` ego
  plus traffic of `SVehicle`/`MVehicle`/`LVehicle`/`XLVehicle`. Each exposes
  `position`, `velocity`, `speed`, `heading_theta`, `heading`, `WIDTH`,
  `LENGTH`, `HEIGHT`.
- **Geometry (Q2).** `bounding_box` gives the 4 corner points in world frame;
  `get_state()` returns position (3D), heading, roll/pitch, velocity, size,
  steering, throttle_brake, crash flags, spawn road and destination. There is
  no `corners` attribute; use `bounding_box`.
- **Traffic lights (Q3).** None in PG maps by default: MetaDrive only ships a
  light manager for replayed real-world scenarios. Resolved by
  `cassvla/scenarios/signals.py`, which spawns `BaseTrafficLight`s on every
  approach lane of the first X/T block and exposes per-lane status, ego/cross
  phase and stop points through `env.signals.get_state()`. The ego's
  `red_light`/`yellow_light` flags and IDM traffic respond to them. See
  [`scenarios.md`](scenarios.md).
- **Deterministic replay (Q4).** Re-simulating the same seed and actions is
  bit-identical over 38 steps. Oracle rollouts via re-simulation are safe.
