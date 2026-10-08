"""Tracking controller: turns a time-indexed candidate into MetaDrive actions.

Pure pursuit for steering on the candidate's path, a P controller with
feed-forward on the candidate's speed profile, plus a small correction for
along-track lag so the ego stays on the candidate's *timing*, not just its
path. Action convention (probed): [steering, throttle_brake] in [-1, 1],
positive steering turns counter-clockwise in world frame, wheel angle =
steering * max_steering.
"""
import math

import numpy as np

from cassvla.planning.candidates import DT, Candidate
from cassvla.planning.geometry import Polyline


class Tracker:
    def __init__(self, cand: Candidate, vehicle, k_v=0.6, k_s=0.4, k_ff=0.25, lookahead_t=0.8, lookahead_min=3.0):
        self.cand = cand
        self.path = Polyline(np.vstack([cand.xy, cand.xy[-1] + 30.0 * np.array([math.cos(cand.heading[-1]), math.sin(cand.heading[-1])])]))
        self.s_ref = np.array([self.path.project(p) for p in cand.xy])
        self.accel = np.gradient(cand.speed, DT)
        self.wheelbase = float(vehicle.FRONT_WHEELBASE + vehicle.REAR_WHEELBASE)
        self.max_steer = math.radians(float(vehicle.config["max_steering"]))
        self.k_v, self.k_s, self.k_ff = k_v, k_s, k_ff
        self.lookahead_t, self.lookahead_min = lookahead_t, lookahead_min
        self.i = 0
        self.errors = []      # (lateral, along-track) per step

    def act(self, vehicle):
        i = min(self.i, len(self.cand.t) - 1)
        self.i += 1
        pos = np.asarray(vehicle.position, dtype=float)[:2]
        v = float(vehicle.speed)
        s_ego = self.path.project(pos)
        on_path, _ = self.path.at(s_ego)
        self.errors.append((float(np.linalg.norm(on_path[0] - pos)), float(self.s_ref[i] - s_ego)))

        # steering: pure pursuit
        ld = max(self.lookahead_min, self.lookahead_t * v)
        target, _ = self.path.at(s_ego + ld)
        d = target[0] - pos
        alpha = math.atan2(d[1], d[0]) - float(vehicle.heading_theta)
        alpha = math.atan2(math.sin(alpha), math.cos(alpha))
        delta = math.atan2(2.0 * self.wheelbase * math.sin(alpha), ld)
        steer = float(np.clip(delta / self.max_steer, -1.0, 1.0))

        # speed: reference + along-track correction
        v_ref = float(self.cand.speed[i])
        v_cmd = max(0.0, v_ref + self.k_s * float(self.s_ref[i] - s_ego))
        if v_ref <= 0.05 and v < 0.5:
            u = -1.0          # hold the stop
        else:
            u = self.k_v * (v_cmd - v) + self.k_ff * float(self.accel[i])
        return [steer, float(np.clip(u, -1.0, 1.0))]

    def tracking_error(self):
        e = np.asarray(self.errors) if self.errors else np.zeros((1, 2))
        return dict(max_lateral=round(float(e[:, 0].max()), 2), max_along=round(float(np.abs(e[:, 1]).max()), 2))
