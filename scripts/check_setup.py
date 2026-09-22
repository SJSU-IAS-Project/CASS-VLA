"""Setup diagnostic. Runs four checks in order and reports PASS/FAIL.

    python scripts/check_setup.py          # checks 1-2 (headless only)
    python scripts/check_setup.py --gui    # also checks 3-4 (opens windows)
"""
import sys
import traceback

GUI = "--gui" in sys.argv
results = []


def check(name):
    def wrap(fn):
        print(f"\n=== {name} ===")
        try:
            fn()
            print(f"PASS  {name}")
            results.append((name, True, ""))
        except Exception as e:
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            results.append((name, False, f"{type(e).__name__}: {e}"))
        return fn
    return wrap


@check("1. headless env")
def _():
    from metadrive.envs import MetaDriveEnv
    env = MetaDriveEnv(dict(use_render=False, num_scenarios=3))
    obs, info = env.reset(seed=0)
    print("   obs shape:", obs.shape)
    env.close()


@check("2. sdl2 / cv2 conflict")
def _():
    import cv2
    path = cv2.__file__
    print("   cv2:", cv2.__version__, path)
    # the headless build ships no SDL dylibs; the GUI build collides with pygame
    import glob, os
    dylibs = glob.glob(os.path.join(os.path.dirname(path), ".dylibs", "*SDL*"))
    if dylibs:
        raise RuntimeError(
            "opencv-python ships SDL2 and will collide with pygame. "
            "Fix: uv pip uninstall opencv-python && uv pip install opencv-python-headless"
        )
    print("   no SDL2 in cv2 -> no collision with pygame")


if GUI:
    @check("3. panda3d 3D window (single-threaded)")
    def _():
        from metadrive.envs import MetaDriveEnv
        env = MetaDriveEnv(dict(
            use_render=True,
            multi_thread_render=False,   # Cocoa needs GL on the main thread
            window_size=(800, 600),
            num_scenarios=3,
        ))
        env.reset(seed=0)
        for _ in range(120):
            env.step([0.0, 0.3])
        env.close()

    @check("4. top-down pygame renderer")
    def _():
        from metadrive.envs import MetaDriveEnv
        env = MetaDriveEnv(dict(use_render=False, num_scenarios=3, traffic_density=0.2))
        env.reset(seed=0)
        mode = None
        for candidate in ("top_down", "topdown"):
            try:
                env.render(mode=candidate)
                mode = candidate
                break
            except Exception as e:
                print(f"   mode={candidate!r} rejected: {e}")
        if mode is None:
            raise RuntimeError("no working top-down mode string")
        print(f"   using mode={mode!r}")
        for _ in range(200):
            env.step([0.0, 0.3])
            env.render(mode=mode)
        env.close()


print("\n" + "=" * 46)
for name, ok, err in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  -> {err}" if err else ""))
if not GUI:
    print("\n(rerun with --gui to check the renderers)")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
