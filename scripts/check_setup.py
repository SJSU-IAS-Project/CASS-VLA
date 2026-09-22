"""Setup diagnostic. Runs four checks in order and reports PASS/FAIL.

    python scripts/check_setup.py          # checks 1-2 (headless only)
    python scripts/check_setup.py --gui    # also checks 3-4 (opens windows)
"""
import sys
import traceback

GUI = "--gui" in sys.argv
results = []


def check(name, fatal=True):
    def wrap(fn):
        print(f"\n=== {name} ===")
        try:
            fn()
            print(f"PASS  {name}")
            results.append((name, "PASS", ""))
        except Exception as e:
            tag = "FAIL" if fatal else "WARN"
            print(f"{tag}  {name}: {e}")
            if fatal:
                traceback.print_exc()
            results.append((name, tag, str(e).splitlines()[0]))
        return fn
    return wrap


@check("1. headless env")
def _():
    from metadrive.envs import MetaDriveEnv
    env = MetaDriveEnv(dict(use_render=False, num_scenarios=3))
    obs, info = env.reset(seed=0)
    print("   obs shape:", obs.shape)
    env.close()


@check("2. cv2 / sdl2 status", fatal=False)
def _():
    import cv2, glob, os
    print("   cv2:", cv2.__version__, cv2.__file__)
    dylibs = glob.glob(os.path.join(os.path.dirname(cv2.__file__), ".dylibs", "*SDL*"))
    if dylibs:
        # Informational only. pygame and cv2 each bundle libSDL2, which makes
        # macOS print objc duplicate-class warnings. opencv-python-headless 5.x
        # bundles it too, so swapping builds does NOT help -- and installing
        # both breaks cv2 outright, since they share the cv2/ directory.
        # Verified harmless: check 4 passes with the collision present.
        raise RuntimeError(
            "cv2 bundles libSDL2 -> expect objc duplicate-class warnings on "
            "macOS. Harmless; do NOT install opencv-python-headless alongside "
            "opencv-python to 'fix' it. See docs/phase1_findings.md"
        )
    print("   no bundled SDL2 -> no objc warnings expected")


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
for name, tag, err in results:
    print(f"{tag}  {name}" + (f"  -> {err}" if err else ""))
if not GUI:
    print("\n(rerun with --gui to check the renderers)")
sys.exit(1 if any(t == "FAIL" for _, t, _ in results) else 0)
