"""Phase-1 state probe: can MetaDrive give us what the oracle labeller needs?

Answers four questions, in increasing order of how much trouble they cause if
the answer is no:

  Q1  enumerate every actor with pose + velocity at an arbitrary step
  Q2  get footprints / bounding boxes for collision geometry
  Q3  read traffic-light phase (and does a scenario with lights exist)
  Q4  replay a seed deterministically  <-- the sleeper requirement

Q4 matters most. Oracle ranking means scoring K candidates from the SAME state,
so we need either deterministic replay or state save/restore. If Q4 fails, the
labelling pipeline design in docs/refined_proposal.md has to change.

    python scripts/probe_state.py
"""
import numpy as np
from metadrive.envs import MetaDriveEnv

CFG = dict(use_render=False, num_scenarios=5, start_seed=0,
           traffic_density=0.3, map=3)


def get_ego(env):
    return getattr(env, "agent", None) or getattr(env, "vehicle", None)


def attrs(o, names):
    out = {}
    for n in names:
        v = getattr(o, n, None)
        if v is not None and not callable(v):
            out[n] = v
    return out


print("#" * 60)
print("Q1/Q2/Q3: what does the engine expose?")
print("#" * 60)

env = MetaDriveEnv(CFG)
obs, info = env.reset(seed=0)
ego = get_ego(env)
print("ego class:", type(ego).__name__)

for _ in range(40):
    env.step([0.0, 0.5])

# --- Q1: actors with pose + velocity -------------------------------------
print("\n--- Q1 actors ---")
objs = env.engine.get_objects()
print(f"{len(objs)} objects in engine")
kinds = {}
for oid, o in objs.items():
    kinds.setdefault(type(o).__name__, []).append(o)
for k, v in kinds.items():
    print(f"  {k}: {len(v)}")

sample = next(iter(objs.values()))
print("\nsample object fields:")
for k, v in attrs(sample, ["position", "velocity", "speed", "heading_theta",
                           "heading", "height", "WIDTH", "LENGTH", "HEIGHT"]).items():
    print(f"  {k:15s} {np.round(v, 3) if isinstance(v, (np.ndarray, list)) else v}")

# --- Q2: bounding boxes ---------------------------------------------------
print("\n--- Q2 geometry ---")
for name in ("bounding_box", "get_state", "corners", "top_down_width", "top_down_length"):
    v = getattr(sample, name, None)
    if v is None:
        print(f"  {name:18s} MISSING")
    elif callable(v):
        try:
            print(f"  {name:18s} (call) -> {v()}")
        except Exception as e:
            print(f"  {name:18s} (call) raised {e}")
    else:
        print(f"  {name:18s} {v}")

# --- Q3: traffic lights ---------------------------------------------------
print("\n--- Q3 traffic lights ---")
print("engine managers:", list(getattr(env.engine, "managers", {}).keys()))
lights = [o for o in objs.values() if "light" in type(o).__name__.lower()]
print(f"{len(lights)} light objects in this scenario")
for lt in lights[:3]:
    print("  ", type(lt).__name__, attrs(lt, ["status", "position"]))
if not lights:
    print("  none here -> need an intersection scenario; check "
          "env.engine.managers for a light manager")

env.close()

# --- Q4: determinism ------------------------------------------------------
print("\n" + "#" * 60)
print("Q4: deterministic replay (the one that matters)")
print("#" * 60)

ACTIONS = [[0.0, 0.5]] * 30 + [[0.2, 0.3]] * 30


def rollout(seed):
    e = MetaDriveEnv(CFG)
    e.reset(seed=seed)
    eg = get_ego(e)
    trace = []
    for a in ACTIONS:
        e.step(a)
        trace.append(np.array(eg.position, dtype=float).copy())
    e.close()
    return np.array(trace)


a = rollout(0)
b = rollout(0)
drift = np.abs(a - b).max()
print(f"max |pos_a - pos_b| over {len(ACTIONS)} steps: {drift:.3e}")
if drift < 1e-9:
    print("PASS  bit-identical replay -> oracle rollout via re-simulation is fine")
elif drift < 1e-3:
    print("WARN  near-identical; small drift. Usable, but prefer save/restore "
          "state if MetaDrive exposes it")
else:
    print("FAIL  replay diverges. Oracle rollout cannot rely on re-simulation.\n"
          "      Fall back to: snapshot state -> propagate actors kinematically\n"
          "      in numpy rather than re-stepping the simulator.")

print("\ndone. Record the answers in docs/ before building the generator.")
