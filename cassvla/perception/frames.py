"""Front-camera frames at a decision point, for the offline VLM pass (Phase 5).

A decision point is ``(family, seed, t_dec)``. The renderer drives the same hazard-blind cruise prefix as the
oracle (it reuses ``Oracle._prefix``), with an offscreen RGB camera added to the env, and captures one frame
from the ego's front camera at ``t_dec``. Physics does not depend on the camera, so the ego reaches the same
pose as in the labelled oracle record; ``tests/test_frames.py`` checks this.

    from cassvla.perception import FrameRenderer
    r = FrameRenderer("occluded_pedestrian", start_seed=100, num_scenarios=5)
    out = r.render(seed=101, t_dec=2.0)       # dict, or None if the prefix ended the episode
    out["image"]                              # (H, W, 3) uint8 RGB
    r.close()

MetaDrive allows one engine per process, so keep one renderer alive at a time.
"""
import time

import numpy as np
from metadrive.component.sensors.rgb_camera import RGBCamera

from cassvla.planning.candidates import cruise_candidate
from cassvla.planning.control import Tracker
from cassvla.planning.oracle import Oracle

CAMERA_SIZE = (640, 360)              # width, height
CAMERA_POSITION = (0.0, 0.8, 1.5)     # MetaDrive's default sensor mount, relative to the ego origin
CAMERA_HPR = (0.0, -5.0, 0.0)


def frame_key(family, seed, t_dec):
    """Stable key used for file names and for joining frames and VLM outputs to dataset rows."""
    return f"{family}/{int(seed)}_{float(t_dec):.1f}"


def camera_overrides(size=CAMERA_SIZE):
    w, h = size
    return dict(image_observation=True, sensors=dict(rgb_camera=(RGBCamera, w, h)),
                vehicle_config=dict(image_source="rgb_camera"), stack_size=1,
                show_interface=False, show_logo=False, show_fps=False)


class FrameRenderer:
    def __init__(self, family, start_seed=0, num_scenarios=1, size=CAMERA_SIZE):
        self.family, self.size = family, tuple(size)
        self._oracle = Oracle(family, start_seed=start_seed, num_scenarios=num_scenarios, **camera_overrides(size))

    @property
    def env(self):
        return self._oracle.env

    def close(self):
        self._oracle.close()

    def capture(self):
        """The ego's current front view as (H, W, 3) uint8 RGB."""
        cam = self.env.engine.get_sensor("rgb_camera")
        bgr = cam.perceive(to_float=False, new_parent_node=self.env.agent.origin, position=CAMERA_POSITION, hpr=CAMERA_HPR)
        return np.ascontiguousarray(np.asarray(bgr, dtype=np.uint8)[..., ::-1])

    def _frame(self, seed, t_dec, t0):
        ego = self.env.agent
        return dict(key=frame_key(self.family, seed, t_dec), family=self.family, seed=int(seed), t_dec=float(t_dec),
                    image=self.capture(), ego=dict(position=[round(float(x), 2) for x in ego.position],
                                                   heading=round(float(ego.heading_theta), 3), speed=round(float(ego.speed), 2)),
                    seconds=round(time.time() - t0, 3))

    def render(self, seed, t_dec):
        """One decision point, with its own reset and prefix: exactly ``Oracle._prefix``."""
        t0 = time.time()
        _, ended = self._oracle._prefix(seed, t_dec)
        return None if ended is not None else self._frame(seed, t_dec, t0)

    def render_seed(self, seed, t_decs):
        """Every decision point of one seed from a single rollout, which skips one reset per frame.

        The cruise policy's action at a given step does not depend on how far ahead its reference path
        runs, so stopping at each ``t_dec`` on the way to the last one gives the same ego state as separate
        prefixes; ``tests/test_frames.py`` checks this against oracle records. Yields one frame dict per
        ``t_dec`` (in ascending order) until the prefix ends the episode."""
        env, oracle = self.env, self._oracle
        steps = sorted({int(round(t / 0.1)): float(t) for t in t_decs}.items())
        t0 = time.time()
        env.reset(seed=seed)
        tracker = Tracker(cruise_candidate(env, oracle.cruise, steps[-1][1] + 1.0), env.agent)
        done = 0
        for n, t_dec in steps:
            while done < n:
                _, _, term, trunc, _ = env.step(tracker.act(env.agent))
                done += 1
                if term or trunc:
                    return
            yield self._frame(seed, t_dec, t0)
            t0 = time.time()
