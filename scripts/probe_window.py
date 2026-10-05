"""Isolate why the Panda3D 3D window fails on macOS.

Runs three stages, each in a fresh subprocess (ShowBase is a per-process
singleton, so a failed window can't be retried in-process):

  A. bare Panda3D ShowBase, default settings, display notify at debug
  B. bare Panda3D with MetaDrive's prc settings (multisamples 8 etc.)
  C. MetaDrive with debug=True, debug_panda3d=True (un-silences Panda3D)

    python scripts/probe_window.py
"""
import subprocess
import sys

STAGE_A = r"""
from panda3d.core import loadPrcFileData
loadPrcFileData("", "notify-level-display debug")
loadPrcFileData("", "notify-level-glgsg debug")
loadPrcFileData("", "win-size 800 600")
from direct.showbase.ShowBase import ShowBase
b = ShowBase(windowType="onscreen")
print("   pipe:", b.pipe.getType().getName())
print("   gsg :", b.win.getGsg().getDriverRenderer(), b.win.getGsg().getDriverVersion())
print("   fb  :", b.win.getFbProperties())
for _ in range(30):
    b.taskMgr.step()
b.destroy()
"""

STAGE_B = r"""
from panda3d.core import loadPrcFileData
loadPrcFileData("", "notify-level-display debug")
loadPrcFileData("", "notify-level-glgsg debug")
loadPrcFileData("", "win-size 800 600")
# what metadrive/engine/core/engine_core.py sets at import + init
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 8")
loadPrcFileData("", "audio-library-name null")
loadPrcFileData("", "model-cache-compressed-textures 1")
loadPrcFileData("", "textures-power-2 none")
loadPrcFileData("", "garbage-collect-states 0")
loadPrcFileData("", "compressed-textures 1")
from direct.showbase.ShowBase import ShowBase
b = ShowBase(windowType="onscreen")
print("   pipe:", b.pipe.getType().getName())
print("   fb  :", b.win.getFbProperties())
for _ in range(30):
    b.taskMgr.step()
b.destroy()
"""

STAGE_C = r"""
from metadrive.envs import MetaDriveEnv
env = MetaDriveEnv(dict(
    use_render=True,
    multi_thread_render=False,
    window_size=(800, 600),
    num_scenarios=3,
    debug=True,
    debug_panda3d=True,
))
env.reset(seed=0)
for _ in range(60):
    env.step([0.0, 0.3])
print("   3D window ran 60 steps")
env.close()
"""

STAGES = [
    ("A. bare panda3d, default prc", STAGE_A),
    ("B. bare panda3d + metadrive prc", STAGE_B),
    ("C. metadrive, debug_panda3d=True", STAGE_C),
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
print("A fail -> Panda3D/Cocoa itself can't open a GL window from this python")
print("A pass, B fail -> one of MetaDrive's prc settings (likely multisamples 8)")
print("A+B pass, C fail -> something in MetaDrive's engine init; read the debug log above")
sys.exit(1 if any(t != "PASS" for _, t in results) else 0)
