"""Isolate why the Panda3D 3D window fails on macOS.

Findings (2026-10-05, M4 Air, macOS 15, Apple GL 2.1-on-Metal compat context):
  - 8x multisampled pixel formats are refused ("Could not find a usable pixel
    format"); 0x and 4x work. MetaDrive 0.4.3 hardcodes 8x for the window and
    16x for simplepbr's offscreen buffer, and its PBR shaders are GLSL 330
    which the 2.1 context can't compile.
  - Upstream fixed all of this for macOS in PR #794 (gl-version 4 1,
    multisamples 4, GLSL 330 everywhere), so requirements.txt pins a git commit.

Each stage runs in a fresh subprocess (ShowBase is a per-process singleton,
so a failed window can't be retried in-process):

  A-C. bare Panda3D window at multisamples 0 / 4 / 8 (default GL profile)
  D.   bare Panda3D, gl-version 4 1 core profile, multisamples 4 (upstream's mac settings)
  E.   MetaDrive as shipped
  F.   MetaDrive with debug_panda3d=True so shader compile errors are visible

    python scripts/probe_window.py
"""
import subprocess
import sys

def bare(ms, gl=None):
    glline = f'loadPrcFileData("", "gl-version {gl}")' if gl else ""
    return f"""
from panda3d.core import loadPrcFileData
loadPrcFileData("", "notify-level-display debug")
loadPrcFileData("", "win-size 800 600")
loadPrcFileData("", "audio-library-name null")
loadPrcFileData("", "framebuffer-multisample {1 if ms else 0}")
loadPrcFileData("", "multisamples {ms}")
{glline}
from direct.showbase.ShowBase import ShowBase
b = ShowBase(windowType="onscreen")
g = b.win.getGsg()
print("   gsg :", g.getDriverRenderer(), g.getDriverVersion(), "glsl", g.getDriverShaderVersionMajor(), g.getDriverShaderVersionMinor())
print("   fb  :", b.win.getFbProperties())
for _ in range(30):
    b.taskMgr.step()
b.destroy()
"""


def metadrive(debug):
    return f"""
import metadrive
from metadrive.envs import MetaDriveEnv
from metadrive.version import VERSION; print("   metadrive", VERSION, metadrive.__file__)
env = MetaDriveEnv(dict(
    use_render=True, multi_thread_render=False, window_size=(800, 600), num_scenarios=3,
    debug={debug}, debug_panda3d={debug},
))
env.reset(seed=0)
for _ in range(120):
    env.step([0.0, 0.3])
print("   3D window ran 120 steps")
env.close()
"""


STAGES = [
    ("A. bare panda3d, multisamples 0", bare(0)),
    ("B. bare panda3d, multisamples 4", bare(4)),
    ("C. bare panda3d, multisamples 8 (0.4.3 default)", bare(8)),
    ("D. bare panda3d, gl-version 4 1, multisamples 4 (upstream mac)", bare(4, "4 1")),
    ("E. metadrive as shipped", metadrive(False)),
    ("F. metadrive, debug_panda3d=True", metadrive(True)),
]

results = []
for name, code in STAGES:
    print(f"\n=== {name} ===", flush=True)
    try:
        r = subprocess.run([sys.executable, "-c", code], timeout=120)
        tag = "PASS" if r.returncode == 0 else "FAIL"
    except subprocess.TimeoutExpired:
        tag = "HANG"
    print(f"{tag}  {name}", flush=True)
    results.append((name, tag))

print("\n" + "=" * 46)
for name, tag in results:
    print(f"{tag}  {name}")
print()
print("E pass -> 3D rendering works on this Mac")
print("E fail -> read F's Panda3D debug log above for the reason")
sys.exit(1 if any(t != "PASS" for _, t in results) else 0)
