"""macOS OpenGL workaround for MetaDrive's 3D window.

MetaDrive sets `framebuffer-multisample 1` / `multisamples 8` at import time
(metadrive/engine/core/engine_core.py). Apple's GL-on-Metal compat context
refuses an 8x multisampled pixel format:

    :display:cocoadisplay(error): Could not find a usable pixel format.

Panda3D's prc system lets later entries override earlier ones, so calling
this AFTER `import metadrive...` and BEFORE the env is created is enough.

    from mac_gl import apply_mac_gl_workaround
    from metadrive.envs import MetaDriveEnv
    apply_mac_gl_workaround()
    env = MetaDriveEnv(dict(use_render=True, multi_thread_render=False, ...))
"""
import sys


def apply_mac_gl_workaround(multisamples: int = 0) -> None:
    if sys.platform != "darwin":
        return
    from panda3d.core import loadPrcFileData
    if multisamples > 0:
        loadPrcFileData("", "framebuffer-multisample 1")
        loadPrcFileData("", f"multisamples {multisamples}")
    else:
        loadPrcFileData("", "framebuffer-multisample 0")
        loadPrcFileData("", "multisamples 0")
