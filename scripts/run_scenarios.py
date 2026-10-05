"""Run every scenario family headless and report what the engine exposes.

    python scripts/run_scenarios.py                 # all families, seeds 0-2
    python scripts/run_scenarios.py --family ambiguous_light --seeds 5
    python scripts/run_scenarios.py --frames        # also save top-down PNGs to out/scenarios/

Exit code 1 if any family fails to build or run.
"""
import argparse
import os
import sys
import traceback

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cassvla.scenarios import FAMILIES, make_env  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--family", default=None)
p.add_argument("--seeds", type=int, default=3)
p.add_argument("--steps", type=int, default=120)
p.add_argument("--throttle", type=float, default=0.5)
p.add_argument("--frames", action="store_true", help="save top-down frames to out/scenarios/")
args = p.parse_args()

fams = [args.family] if args.family else list(FAMILIES)
rows, failed = [], False
os.makedirs("out/scenarios", exist_ok=True)

for fam in fams:
    print(f"\n{'=' * 70}\n{fam}: {FAMILIES[fam].description}\n{'=' * 70}")
    env = None
    try:
        env = make_env(fam, seed=0, num_scenarios=args.seeds)
        for seed in range(args.seeds):
            env.reset(seed=seed)
            objs = env.engine.get_objects()
            kinds = {}
            for o in objs.values():
                kinds[type(o).__name__] = kinds.get(type(o).__name__, 0) + 1
            sig0 = env.signals.get_state()
            events, red_seen, crash, term_reason = [], False, False, None
            for s in range(args.steps):
                _, _, term, trunc, info = env.step([0.0, args.throttle])
                red_seen |= bool(env.agent.red_light)
                crash |= bool(env.agent.crash_vehicle or env.agent.crash_object or env.agent.crash_human)
                if args.frames and s in (0, 30, 60, 90):
                    try:
                        frame = env.render(mode="top_down", window=False, screen_size=(600, 600), film_size=(1200, 1200))
                        if frame is not None:
                            import matplotlib
                            matplotlib.use("Agg")
                            import matplotlib.pyplot as plt
                            plt.imsave(f"out/scenarios/{fam}_s{seed}_t{s:03d}.png", np.asarray(frame))
                    except Exception as e:  # rendering is best-effort
                        print("   frame failed:", e)
                if term or trunc:
                    term_reason = [k for k in ("arrive_dest", "crash_vehicle", "crash_object", "crash_human", "out_of_road", "max_step") if info.get(k)]
                    break
            hz = env.hazards.get_state()
            sig = env.signals.get_state()
            fired = {n: h.get("fired") or h.get("triggered_t") for n, h in hz["hazards"].items() if h.get("fired") or h.get("triggered_t") is not None}
            print(f"  seed {seed}: {s + 1:3d} steps  ego@{np.round(env.agent.position, 1)}  objects={kinds}")
            print(f"           lights={len(sig['lights'])} ego_light t0={sig0['ego_status']} tEnd={sig['ego_status']} approaches={sig['approaches']}")
            print(f"           triggers={fired}  red_light_seen={red_seen} crash={crash} end={term_reason}")
            rows.append((fam, seed, s + 1, len(sig["lights"]), sig0["ego_status"], sig["ego_status"], len(hz["hazards"]), len(fired), red_seen, crash, term_reason))
    except Exception:
        failed = True
        traceback.print_exc()
        rows.append((fam, "-", "ERROR", 0, None, None, 0, 0, False, False, None))
    finally:
        if env is not None:
            env.close()

print(f"\n{'family':24s} {'seed':>4s} {'steps':>5s} {'lights':>6s} {'ego0':>20s} {'egoEnd':>20s} {'hz':>3s} {'fired':>5s} {'red':>5s} {'crash':>5s}  end")
for r in rows:
    print(f"{r[0]:24s} {str(r[1]):>4s} {str(r[2]):>5s} {r[3]:>6d} {str(r[4]):>20s} {str(r[5]):>20s} {r[6]:>3d} {r[7]:>5d} {str(r[8]):>5s} {str(r[9]):>5s}  {r[10]}")
sys.exit(1 if failed else 0)
