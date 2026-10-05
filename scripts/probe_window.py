"""Isolate why the Panda3D 3D window fails on macOS.

Finding (2026-10-05, M4 Air, macOS 15): Apple's GL-on-Metal compat context
refuses MetaDrive's hardcoded `multisamples 8` pixel format. See mac_gl.py.

Each stage runs in a fresh subprocess (ShowBase is a per-process singleton,
so a failed window can't be retried in-process):

  A-C. bare Panda3D window at multisamples 0 / 4 / 8
  D-E. MetaDrive with the mac_gl workaround at multisamples 0 / 4

    python scripts/probe_window.py
"""
import os
import subprocess
import sys

def bare(ms):
    return f"""
from panda3d.core import loadPrcFileData
loadPrcFileData("", "notify-level-display debug")
loadPrcFileData("", "win-size 800 600")
loadPrcFileData("", "audio-library-name null")
loadPrcFileData("", "textures-power-2 none")
loadPrcFileData("", "compressed-textures 1")
loadPrcFileData("", "framebuffer-multisample {1 if ms else 0}")
loadPrcFileData("", "multisamples {ms}")
from direct.showbase.ShowBase import ShowBase
b = ShowBase(windowType="onscreen")
print("   gsg :", b.win.getGsg().getDriverRenderer(), b.win.getGsg().getDriverVersion())
print("   fb  :", b.win.getFbProperties())
for _ in range(30):
    b.taskMgr.step()
b.destroy()
"""


def metadrive(ms):
    return f"""
import os, sys
sys.path.insert(0, {os.path.dirname(os.path.abspath(__file__))!r})
from mac_gl import apply_mac_gl_workaround
from metadrive.envs import MetaDriveEnv
apply_mac_gl_workaround({ms})
env = MetaDriveEnv(dict(
    use_render=True, multi_thread_render=False, window_size=(800, 600), num_scenarios=3,
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
    ("C. bare panda3d, multisamples 8 (metadrive default)", bare(8)),
    ("D. metadrive + workaround, multisamples 0", metadrive(0)),
    ("E. metadrive + workaround, multisamples 4", metadrive(4)),
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
print("D pass -> 3D window works with multisamples 0 (current default in mac_gl.py)")
print("E pass -> 4x antialiasing also works; bump the default in mac_gl.py to 4")
sys.exit(1 if any(t != "PASS" for _, t in results) else 0)
