"""Scripted hazard actors and the manager that owns them.

Each Hazard is a small object with ``spawn(mgr)``, ``step(mgr, ego)`` and
``state()``. The HazardManager builds the list for the configured family at
reset, steps them before every physics step and exposes their state through
``get_state()`` so the oracle labeller can log what the script did.

Determinism: every hazard draws its randomness from the manager's
``np_random``, which MetaDrive seeds from the episode seed.
"""
import math

import numpy as np
from metadrive.component.static_object.traffic_object import TrafficBarrier, TrafficCone
from metadrive.component.traffic_participants.pedestrian import Pedestrian
from metadrive.component.vehicle.vehicle_type import DefaultVehicle, StaticDefaultVehicle, XLVehicle
from metadrive.manager.base_manager import BaseManager
from metadrive.policy.idm_policy import IDMPolicy

TRAFFIC_V_CONFIG = dict(show_navi_mark=False, show_dest_mark=False, enable_reverse=False,
                        show_lidar=False, show_lane_line_detector=False, show_side_detector=False)


def _lane(mgr, lane_index):
    return mgr.engine.current_map.road_network.get_lane(tuple(lane_index))


def _dist(a, b):
    return float(np.linalg.norm(np.asarray(a, dtype=float)[:2] - np.asarray(b, dtype=float)[:2]))


class Hazard:
    name = "hazard"

    def spawn(self, mgr):
        raise NotImplementedError

    def step(self, mgr, ego):
        pass

    def state(self):
        return {}


class ParkedVehicle(Hazard):
    """A vehicle frozen on a lane: the occluder."""

    def __init__(self, name, lane_index, longitude, lateral=0.0, large=False, destination=None):
        self.name, self.lane_index, self.longitude, self.lateral, self.large = name, tuple(lane_index), float(longitude), float(lateral), large
        self.destination, self.obj = destination, None

    def spawn(self, mgr):
        cls = XLVehicle if self.large else StaticDefaultVehicle
        vc = dict(TRAFFIC_V_CONFIG, spawn_lane_index=self.lane_index, spawn_longitude=self.longitude, spawn_lateral=self.lateral,
                  destination=self.destination)
        self.obj = mgr.spawn_object(cls, vehicle_config=vc)
        self.obj.set_break_down()
        self.obj.set_static(True)

    def state(self):
        return dict(kind="parked", position=tuple(np.round(self.obj.position, 2)), heading=round(float(self.obj.heading_theta), 3),
                    size=(self.obj.LENGTH, self.obj.WIDTH))


class Barrier(Hazard):
    """Cones or barriers across a lane."""

    def __init__(self, name, lane_index, longitude, count=3, spacing=1.2, cones=False):
        self.name, self.lane_index, self.longitude, self.count, self.spacing, self.cones = name, tuple(lane_index), float(longitude), count, spacing, cones
        self.objs = []

    def spawn(self, mgr):
        lane = _lane(mgr, self.lane_index)
        cls = TrafficCone if self.cones else TrafficBarrier
        half = lane.width_at(self.longitude) / 2 - 0.4
        lats = np.linspace(-half, half, self.count) if self.count > 1 else [0.0]
        for lat in lats:
            self.objs.append(mgr.spawn_object(cls, lane=lane, position=lane.position(self.longitude, float(lat)),
                                              static=True, heading_theta=lane.heading_theta_at(self.longitude)))

    def state(self):
        return dict(kind="barrier", positions=[tuple(np.round(o.position, 2)) for o in self.objs])


class CrossingPedestrian(Hazard):
    """Stands still (hidden) until the ego is within ``trigger_dist`` of it, then walks ``walk_dist`` metres."""

    def __init__(self, name, position, heading_theta, speed=1.4, trigger_dist=15.0, walk_dist=9.0):
        self.name = name
        self.position0, self.heading, self.speed = np.asarray(position, float), float(heading_theta), float(speed)
        self.trigger_dist, self.walk_dist = float(trigger_dist), float(walk_dist)
        self.obj, self.triggered_t, self.walked, self.done = None, None, 0.0, False

    def spawn(self, mgr):
        self.obj = mgr.spawn_object(Pedestrian, position=self.position0.tolist(), heading_theta=self.heading, random_seed=int(mgr.np_random.randint(1 << 30)))
        self.obj.set_velocity([1, 0], 0.0, in_local_frame=True)

    def step(self, mgr, ego):
        if self.done:
            return
        if self.triggered_t is None:
            if _dist(ego.position, self.obj.position) <= self.trigger_dist:
                self.triggered_t = mgr.t
            else:
                return
        self.walked = _dist(self.obj.position, self.position0)
        if self.walked >= self.walk_dist:
            self.obj.set_velocity([1, 0], 0.0, in_local_frame=True)
            self.done = True
        else:
            self.obj.set_velocity([math.cos(self.heading), math.sin(self.heading)], self.speed, in_local_frame=False)

    def state(self):
        return dict(kind="pedestrian", position=tuple(np.round(self.obj.position, 2)), triggered_t=self.triggered_t,
                    walked=round(self.walked, 2), done=self.done, speed=round(float(self.obj.speed), 2))


class KinematicVehicle(Hazard):
    """A vehicle driven by setting its velocity along a lane each step.

    Vehicles spawned on a negative-direction road (e.g. "-1X0_1_") need an
    explicit ``destination`` node: MetaDrive's auto route assignment raises
    ``list.remove(x)`` for them.

    ``events`` is a list of dicts applied in order, each with a trigger and a
    target: {"when": ("t", 3.0) | ("ego_within", dist) | ("ego_near", (x, y), dist)
                     | ("eta_match", (x, y), lead_s),
             "speed": float, "accel": float (m/s^2, magnitude), "lane_index": optional new lane}.

    ``eta_match`` fires when the ego's time to reach the conflict point (x, y)
    at its current speed drops to this vehicle's own time to get there under
    the event's speed/accel, plus ``lead_s`` (negative = this vehicle arrives
    first). It makes the conflict timing independent of the ego's policy.
    Also used for red-light runners, braking leads, cut-ins and fast closers.
    """

    def __init__(self, name, lane_index, longitude, speed, events=(), lateral=0.0, large=False, destination=None):
        self.name, self.lane_index, self.longitude, self.lateral = name, tuple(lane_index), float(longitude), float(lateral)
        self.destination = destination
        self.speed, self.target_speed, self.accel = float(speed), float(speed), 100.0
        self.events, self.fired, self.large = list(events), [], large
        self.obj, self.lane, self.target_lat = None, None, float(lateral)
        self._ego_v_prev = None
        self.launch_lag = 0.5   # s; measured delay between the first velocity command and the body moving

    def spawn(self, mgr):
        self.lane = _lane(mgr, self.lane_index)
        cls = XLVehicle if self.large else DefaultVehicle
        vc = dict(TRAFFIC_V_CONFIG, spawn_lane_index=self.lane_index, spawn_longitude=self.longitude, spawn_lateral=self.lateral,
                  destination=self.destination)
        self.obj = mgr.spawn_object(cls, vehicle_config=vc)
        self._drive(mgr.dt)

    def _triggered(self, ev, mgr, ego):
        kind = ev["when"][0]
        if kind == "t":
            return mgr.t >= ev["when"][1]
        if kind == "ego_within":
            return _dist(ego.position, self.obj.position) <= ev["when"][1]
        if kind == "ego_near":
            return _dist(ego.position, ev["when"][1]) <= ev["when"][2]
        if kind == "eta_match":
            point, lead = ev["when"][1], ev["when"][2]
            eta_ego = self._eta_ego(ego, point, mgr.dt)
            v, a = float(ev.get("speed", self.target_speed)), float(ev.get("accel", 100.0))
            d = _dist(self.obj.position, point)
            d_acc = (v * v - self.speed * self.speed) / (2 * a) if v > self.speed else 0.0
            eta_self = ((v - self.speed) / a + (d - d_acc) / v) if d > d_acc else math.sqrt(2 * d / a)
            return eta_ego <= eta_self + self.launch_lag + lead
        raise ValueError(ev)

    def _eta_ego(self, ego, point, dt):
        """Time for the ego to reach ``point`` assuming it keeps its current (measured) acceleration."""
        v = max(float(ego.speed), 0.5)
        a = 0.0 if self._ego_v_prev is None else float(np.clip((v - self._ego_v_prev) / dt, 0.0, 4.0))
        d = _dist(ego.position, point)
        if a < 1e-3:
            return d / v
        return (-v + math.sqrt(v * v + 2 * a * d)) / a

    def step(self, mgr, ego):
        try:
            self._ego_v_now = float(ego.speed)
        except Exception:
            self._ego_v_now = None
        while self.events and self._triggered(self.events[0], mgr, ego):
            ev = self.events.pop(0)
            self.target_speed = float(ev.get("speed", self.target_speed))
            self.accel = float(ev.get("accel", 100.0))
            if "lane_index" in ev:
                self.lane_index = tuple(ev["lane_index"])
                self.lane = _lane(mgr, self.lane_index)
            self.fired.append((round(mgr.t, 2), ev.get("speed"), ev.get("lane_index")))
        self._ego_v_prev = self._ego_v_now
        self._drive(mgr.dt)

    def _drive(self, dt):
        if self.speed < self.target_speed:
            self.speed = min(self.target_speed, self.speed + self.accel * dt)
        elif self.speed > self.target_speed:
            self.speed = max(self.target_speed, self.speed - self.accel * dt)
        lon, lat = self.lane.local_coordinates(self.obj.position)
        lon = float(np.clip(lon, 0.0, self.lane.length))
        h = self.lane.heading_theta_at(lon)
        fwd = np.array([math.cos(h), math.sin(h)])
        left = np.array([-math.sin(h), math.cos(h)])
        d = fwd + 0.25 * (self.target_lat - lat) * left
        d /= np.linalg.norm(d)
        self.obj.set_velocity(d, self.speed, in_local_frame=False)
        self.obj.set_heading_theta(math.atan2(d[1], d[0]))

    def state(self):
        return dict(kind="kinematic", position=tuple(np.round(self.obj.position, 2)), speed=round(float(self.obj.speed), 2),
                    target_speed=self.target_speed, lane=self.lane_index, fired=list(self.fired), pending=len(self.events))


class IDMVehicle(Hazard):
    """Ordinary MetaDrive traffic vehicle with the IDM policy (obeys lights, follows leads)."""

    def __init__(self, name, lane_index, longitude, destination=None):
        self.name, self.lane_index, self.longitude, self.destination = name, tuple(lane_index), float(longitude), destination
        self.obj = None

    def spawn(self, mgr):
        vc = dict(TRAFFIC_V_CONFIG, spawn_lane_index=self.lane_index, spawn_longitude=self.longitude, destination=self.destination)
        self.obj = mgr.spawn_object(DefaultVehicle, vehicle_config=vc)
        mgr.add_policy(self.obj.id, IDMPolicy, self.obj, mgr.generate_seed())

    def step(self, mgr, ego):
        p = mgr.get_policy(self.obj.id)
        self.obj.before_step(p.act())

    def state(self):
        return dict(kind="idm", position=tuple(np.round(self.obj.position, 2)), speed=round(float(self.obj.speed), 2))


class HazardManager(BaseManager):
    PRIORITY = 60  # after SignalManager

    def __init__(self):
        super().__init__()
        self.hazards = []
        self.family = None
        self.t = 0.0
        self.dt = 0.1

    def reset(self):
        from cassvla.scenarios.families import FAMILIES
        gc = self.engine.global_config
        self.dt = gc["physics_world_step_size"] * gc["decision_repeat"]
        self.t = 0.0
        self.family = gc.get("family")
        self.hazards = []
        if not self.family:
            return
        spec = FAMILIES[self.family]
        self.hazards = spec.build(self.np_random, self)
        for h in self.hazards:
            h.spawn(self)

    def _ego(self):
        agents = self.engine.agent_manager.active_agents
        return next(iter(agents.values())) if agents else None

    def before_step(self, *args, **kwargs):
        ego = self._ego()
        if ego is not None:
            for h in self.hazards:
                h.step(self, ego)
        self.t += self.dt
        return dict()

    def get_state(self):
        return dict(family=self.family, t=round(self.t, 2), hazards={h.name: h.state() for h in self.hazards})
