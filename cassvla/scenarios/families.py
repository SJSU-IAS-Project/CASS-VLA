"""The six scenario families from docs/refined_proposal.md section 4.

Lane naming (PG maps): the first block is always ``I`` with nodes
``>``, ``>>``, ``>>>``; the ego spawns on (">", ">>", k) and the 40 m
approach is (">>", ">>>", k). Lane 0 is the leftmost. ``lateral`` is
positive to the left. See docs/phase1_findings.md for the X/T lane graphs.

Each family is a FamilySpec whose ``build(rng, mgr)`` returns the hazards to
spawn for one episode. Randomness comes only from ``rng`` (seeded by episode).
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List

import numpy as np

from cassvla.scenarios.hazards import Barrier, CrossingPedestrian, Hazard, IDMVehicle, KinematicVehicle, ParkedVehicle
from cassvla.scenarios.signals import GREEN, RED, YELLOW

APPROACH = (">>", ">>>")          # 40 m straight before block 1
EGO_LANE = (">", ">>", 1)         # middle of 3 lanes


def _lane(k):
    return APPROACH + (k,)


@dataclass
class FamilySpec:
    name: str
    map: str
    description: str
    build: Callable[[np.random.RandomState, object], List[Hazard]]
    signals: dict = field(default_factory=lambda: dict(enabled=False))
    ego_destination: str = None
    traffic_density: float = 0.0
    horizon: int = 300
    env_overrides: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. occluded pedestrian emerging from behind a parked vehicle
# ---------------------------------------------------------------------------
def _occluded_pedestrian(rng, mgr):
    lane = mgr.engine.current_map.road_network.get_lane(_lane(2))
    lon = float(rng.uniform(20.0, 30.0))
    parked = ParkedVehicle("parked_car", _lane(2), lon, lateral=0.0, large=bool(rng.random() < 0.3))
    # pedestrian stands just right of the parked car (off the lane), then walks left across the road
    ped_pos = lane.position(lon + float(rng.uniform(2.0, 4.0)), -4.3)
    ped = CrossingPedestrian("pedestrian", ped_pos, lane.heading_theta_at(lon) + np.pi / 2,
                             speed=float(rng.uniform(1.1, 1.8)), trigger_dist=float(rng.uniform(12.0, 20.0)),
                             walk_dist=float(rng.uniform(6.0, 10.0)))
    return [parked, ped]


# ---------------------------------------------------------------------------
# 2. occluded cross traffic at a signalised intersection (red-light runner)
# ---------------------------------------------------------------------------
def _occluded_cross_traffic(rng, mgr):
    rn = mgr.engine.current_map.road_network
    # big vehicle parked at the near-right corner, on the southbound exit road, hiding the south arm
    occluder = ParkedVehicle("corner_truck", ("1X0_0_", "1X0_1_", 2), float(rng.uniform(1.0, 6.0)), large=True, destination="1X0_1_")
    # runner comes north from the south arm across the ego's path. It launches when the ego's ETA to the
    # conflict point matches its own (+ lead): lead < 0 -> runner crosses first, lead > 0 -> ego first.
    runner_lane = ("-1X0_1_", "-1X0_0_", int(rng.randint(0, 2)))
    ego_y = rn.get_lane(EGO_LANE).position(0, 0)[1]
    conflict = (float(rn.get_lane(runner_lane).position(0, 0)[0]), float(ego_y))
    runner = KinematicVehicle("runner", runner_lane, float(rng.uniform(8.0, 18.0)), speed=0.0,
                              events=[dict(when=("eta_match", conflict, float(rng.uniform(-1.2, 1.2))),
                                           speed=float(rng.uniform(9.0, 14.0)), accel=4.0),
                                      dict(when=("t", 1e9))],
                              destination="1X2_1_")
    out = [occluder, runner]
    if rng.random() < 0.5:   # sometimes a law-abiding car queued on the cross road too
        out.append(IDMVehicle("cross_idm", ("-1X2_1_", "-1X2_0_", 1), float(rng.uniform(5.0, 15.0)), destination="1X0_1_"))
    return out


# ---------------------------------------------------------------------------
# 3. distant / ambiguous traffic-light state
# ---------------------------------------------------------------------------
def _ambiguous_light(rng, mgr):
    # optional lead car so "follow the lead" is a tempting but wrong heuristic
    if rng.random() < 0.5:
        return [IDMVehicle("lead_idm", _lane(1), float(rng.uniform(18.0, 28.0)), destination="1X1_1_")]
    return []


def _ambiguous_light_signals(rng):
    """Scripted schedule: the ego light changes around the ego's arrival (~5-7 s at a moderate throttle)."""
    t_change = float(rng.uniform(2.5, 8.0))
    if rng.random() < 0.35:   # starts red, turns green late
        return dict(enabled=True, mode="scripted", schedule=[(0.0, RED, GREEN), (t_change, RED, YELLOW), (t_change + 3.0, RED, RED), (t_change + 4.0, GREEN, RED)])
    return dict(enabled=True, mode="scripted", schedule=[(0.0, GREEN, RED), (t_change, YELLOW, RED), (t_change + 3.0, RED, RED), (t_change + 4.0, RED, GREEN)])


# ---------------------------------------------------------------------------
# 4. sudden lead-vehicle braking or cut-in
# ---------------------------------------------------------------------------
def _lead_brake_cutin(rng, mgr):
    cruise = float(rng.uniform(6.0, 9.0))
    if rng.random() < 0.5:
        lead = KinematicVehicle("lead", _lane(1), float(rng.uniform(22.0, 30.0)), speed=cruise,
                                events=[dict(when=("ego_within", float(rng.uniform(10.0, 16.0))), speed=0.0, accel=float(rng.uniform(5.0, 8.0)))])
        return [lead]
    side = int(rng.choice([0, 2]))
    cutter = KinematicVehicle("cutter", _lane(side), float(rng.uniform(14.0, 22.0)), speed=cruise,
                              events=[dict(when=("ego_within", float(rng.uniform(8.0, 14.0))), lane_index=_lane(1), speed=cruise * 0.6, accel=3.0)])
    return [cutter]


# ---------------------------------------------------------------------------
# 5. lane blockage: commit to a lane change or stop
# ---------------------------------------------------------------------------
def _lane_blockage(rng, mgr):
    lon = float(rng.uniform(26.0, 36.0))
    block = [ParkedVehicle("stalled_car", _lane(1), lon), Barrier("cones", _lane(1), lon - 6.0, count=3, cones=True)]
    # an overtaking car in the left lane approaching from behind makes "change left now" risky
    block.append(KinematicVehicle("overtaker", _lane(0), 0.5, speed=float(rng.uniform(11.0, 15.0)), lateral=0.0))
    if rng.random() < 0.4:   # right lane sometimes blocked too (stalled truck)
        block.append(ParkedVehicle("right_truck", _lane(2), lon + float(rng.uniform(-4.0, 4.0)), large=True))
    return block


# ---------------------------------------------------------------------------
# 6. depth / closing-speed ambiguity when merging left to pass a slow lead
# ---------------------------------------------------------------------------
def _merge_closing_speed(rng, mgr):
    slow = KinematicVehicle("slow_lead", _lane(1), float(rng.uniform(16.0, 24.0)), speed=float(rng.uniform(2.5, 4.5)))
    closer = KinematicVehicle("fast_closer", _lane(0), 0.5, speed=float(rng.uniform(13.0, 18.0)))
    return [slow, closer]


FAMILIES: Dict[str, FamilySpec] = {
    "occluded_pedestrian": FamilySpec(
        "occluded_pedestrian", "SS", "pedestrian steps out from behind a car parked in the right lane", _occluded_pedestrian),
    "occluded_cross_traffic": FamilySpec(
        "occluded_cross_traffic", "X", "red-light runner from the south arm, hidden by a truck at the corner", _occluded_cross_traffic,
        signals=dict(enabled=True, mode="scripted", schedule=[(0.0, GREEN, RED)]), ego_destination="1X1_1_"),
    "ambiguous_light": FamilySpec(
        "ambiguous_light", "X", "ego light changes around the ego's arrival at the stop line", _ambiguous_light,
        signals=dict(enabled=True, mode="scripted", schedule=[(0.0, GREEN, RED)]), ego_destination="1X1_1_"),
    "lead_brake_cutin": FamilySpec(
        "lead_brake_cutin", "SS", "lead brakes hard, or a neighbour cuts in and slows", _lead_brake_cutin),
    "lane_blockage": FamilySpec(
        "lane_blockage", "SS", "ego lane blocked ahead; overtaker approaching in the left lane", _lane_blockage),
    "merge_closing_speed": FamilySpec(
        "merge_closing_speed", "SS", "slow lead ahead, fast closer behind in the passing lane", _merge_closing_speed),
}

# per-seed signal schedules for families whose signal timing is randomised
SIGNAL_BUILDERS = {"ambiguous_light": _ambiguous_light_signals}
