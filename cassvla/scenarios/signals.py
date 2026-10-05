"""Traffic signals for procedurally generated MetaDrive intersections.

MetaDrive's PG maps ship no lights and no light manager; lights exist only
for replayed real-world scenarios (ScenarioLightManager). This manager spawns
a BaseTrafficLight on every lane leaving every approach of the first X or T
block, groups approaches into "ego" (parallel to the ego's approach) and
"cross", and drives their phases from a schedule.

Two schedule modes, selected through env config ``signal_config``:

  mode="cycle"     fixed-time cycle: green -> yellow -> all-red for the ego
                   group, then the same for the cross group. ``offset`` is
                   the cycle time at t=0 (None = random per seed).
  mode="scripted"  explicit list of (t_start, ego_status, cross_status).

State is exposed through ``get_state()`` and the ``ego_status``/
``cross_status`` properties so the oracle labeller never has to touch
Panda3D objects.
"""
import math

import numpy as np
from metadrive.component.traffic_light.base_traffic_light import BaseTrafficLight
from metadrive.constants import MetaDriveType
from metadrive.manager.base_manager import BaseManager

GREEN = MetaDriveType.LIGHT_GREEN
YELLOW = MetaDriveType.LIGHT_YELLOW
RED = MetaDriveType.LIGHT_RED

INTERSECTION_IDS = ("X", "T")

DEFAULT_SIGNAL_CONFIG = dict(
    enabled=False,
    mode="cycle",
    green=10.0,
    yellow=3.0,
    all_red=1.0,
    offset=None,      # seconds into the cycle at t=0; None -> random per seed
    schedule=None,    # scripted mode: [(t_start, ego_status, cross_status), ...]
)


def _setter(light, status):
    return {GREEN: light.set_green, YELLOW: light.set_yellow, RED: light.set_red}[status]


class SignalManager(BaseManager):
    PRIORITY = 50  # after PGMapManager so the road network exists at reset()

    def __init__(self):
        super().__init__()
        self.lights = {}          # lane_index -> BaseTrafficLight
        self.group_of = {}        # lane_index -> "ego" | "cross"
        self.approaches = {}      # approach node -> "ego" | "cross"
        self.schedule = []        # [(t_start, ego_status, cross_status)]
        self.ego_status = None
        self.cross_status = None
        self.t = 0.0
        self.dt = 0.1
        self.block = None

    # ---- configuration -------------------------------------------------
    @property
    def cfg(self):
        c = dict(DEFAULT_SIGNAL_CONFIG)
        c.update(self.engine.global_config.get("signal_config", {}) or {})
        return c

    # ---- lifecycle -------------------------------------------------------
    def reset(self):
        gc = self.engine.global_config
        self.dt = gc["physics_world_step_size"] * gc["decision_repeat"]
        self.t = 0.0
        self.lights, self.group_of, self.approaches = {}, {}, {}
        self.ego_status = self.cross_status = None
        cfg = self.cfg
        if not cfg["enabled"]:
            return
        self.block = self._find_intersection()
        if self.block is None:
            return
        rn = self.engine.current_map.road_network
        ego_node = self.block.pre_block_socket.positive_road.end_node
        ego_heading = rn.graph[ego_node][next(iter(rn.graph[ego_node]))][0].heading_theta_at(0)
        for node in self._approach_nodes(self.block, rn):
            first = rn.graph[node][next(iter(rn.graph[node]))][0]
            dh = first.heading_theta_at(0) - ego_heading
            group = "ego" if abs(math.cos(dh)) > 0.7 else "cross"
            self.approaches[node] = group
            for dest, lanes in rn.graph[node].items():
                for lane in lanes:
                    light = self.spawn_object(BaseTrafficLight, lane=lane)
                    self.lights[lane.index] = light
                    self.group_of[lane.index] = group
        self.schedule = self._build_schedule(cfg)
        self._apply(0.0)

    def before_step(self, *args, **kwargs):
        if self.lights:
            self._apply(self.t)
        self.t += self.dt
        return dict()

    def destroy(self):
        self.lights, self.group_of = {}, {}
        super().destroy()

    # ---- schedule --------------------------------------------------------
    def _build_schedule(self, cfg):
        if cfg["mode"] == "scripted":
            sched = [(float(t), e, c) for t, e, c in cfg["schedule"]]
            return sorted(sched, key=lambda x: x[0])
        g, y, r = cfg["green"], cfg["yellow"], cfg["all_red"]
        half = g + y + r
        cycle = 2 * half
        offset = cfg["offset"]
        if offset is None:
            offset = float(self.np_random.uniform(0, cycle))
        # one cycle starting at -offset, repeated enough to cover the horizon
        horizon = self.engine.global_config.get("horizon") or 1000
        n_cycles = int(horizon * self.dt / cycle) + 2
        sched = []
        for k in range(n_cycles):
            base = k * cycle - offset
            sched += [
                (base, GREEN, RED),
                (base + g, YELLOW, RED),
                (base + g + y, RED, RED),
                (base + half, RED, GREEN),
                (base + half + g, RED, YELLOW),
                (base + half + g + y, RED, RED),
            ]
        return sched

    def _apply(self, t):
        ego, cross = RED, RED
        for t0, e, c in self.schedule:
            if t0 <= t:
                ego, cross = e, c
            else:
                break
        if (ego, cross) == (self.ego_status, self.cross_status):
            return
        self.ego_status, self.cross_status = ego, cross
        for idx, light in self.lights.items():
            _setter(light, ego if self.group_of[idx] == "ego" else cross)()

    # ---- queries ---------------------------------------------------------
    def status_of_lane(self, lane_index):
        light = self.lights.get(tuple(lane_index))
        return light.status if light is not None else None

    def get_state(self):
        return dict(
            t=self.t,
            ego_status=self.ego_status,
            cross_status=self.cross_status,
            approaches=dict(self.approaches),
            lights={str(idx): light.status for idx, light in self.lights.items()},
            stop_points={str(idx): tuple(np.round(light.get_state()["stop_point"], 2)) for idx, light in self.lights.items()},
        )

    # ---- map helpers -----------------------------------------------------
    def _find_intersection(self):
        for block in self.engine.current_map.blocks:
            if block.ID in INTERSECTION_IDS:
                return block
        return None

    @staticmethod
    def _approach_nodes(block, rn):
        """Nodes from which lanes enter the intersection body.

        For block i of type X/T these are the previous block's end node (the
        ego approach) and the negative-road nodes ``-i{ID}{k}_0_`` of each arm.
        """
        nodes = [block.pre_block_socket.positive_road.end_node]
        tag = f"-{block.block_index}{block.ID}"
        for node in rn.graph:
            if node.startswith(tag) and node.endswith("_0_"):
                nodes.append(node)
        return nodes
