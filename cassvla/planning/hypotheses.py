"""World hypotheses built only from the base observation, the ego state and the map.

Shared by the counterfactual flip features (``scripts/flip_features.py``, Max) and the value-of-information
selector (``cassvla/planning/voi.py``). Nothing privileged enters: visible actors come from the base
observation, occluders are the polygons of visible actors, and hypothetical actors sit at points the ego
cannot see.

    hypotheses(rec, base) -> {"depth": [...], "occl_static": [...], "occl_ped": [...], "light": [...], "rear": [...]}

Each value is a list of full beliefs (``dict(actors=..., light=..., collision=None)``); a class that does not
apply is an empty list. The random stream is ``rng_for(rec, "flip")``, so the worlds equal the ones the flip
features were fixed with on 2026-11-07.
"""
import math

import numpy as np

from cassvla.planning import tools as T
from cassvla.scenarios.signals import GREEN, RED

DRAWS = 8
MAX_POINTS = 6
LANE_WIDTH = 3.5
REAR_GAP = 12.0
REAR_EXTRA_SPEED = 4.0
CLASSES = ("depth", "occl_static", "occl_ped", "light", "rear")


def hypothetical_actor(name, kind, pos, vel, heading):
    length, width = (4.5, 1.9) if kind == "DefaultVehicle" else (0.5, 0.5)
    return dict(name=name, type=kind, position=np.asarray(pos, float), velocity=np.asarray(vel, float), heading=float(heading),
                length=length, width=width, source="hypothesis")


def occluded_points(rec, base, max_points=MAX_POINTS):
    """Points on the candidate paths, within camera range, hidden behind a visible long actor."""
    origin, _ = T._ego(rec)
    visible = {a["name"] for a in base["actors"]}
    occluders = [a["poly"] for a in rec["actors"] if a["name"] in visible and a["length"] >= T.MIN_OCCLUDER_LENGTH]
    points = []
    for c in rec["candidates"]:
        xy = np.asarray(c["xy"], float)
        for i in range(5, len(xy), 5):
            if np.linalg.norm(xy[i] - origin) <= T.CAMERA_RANGE and occluders and T.blocked(origin, xy[i], occluders):
                step = xy[i] - xy[i - 1]
                points.append((xy[i], math.atan2(step[1], step[0])))
    if len(points) > max_points:
        points = [points[j] for j in np.linspace(0, len(points) - 1, max_points).round().astype(int)]
    return points


def hypotheses(rec, base, draws=DRAWS, max_points=MAX_POINTS):
    rng = T.rng_for(rec, "flip")
    origin, heading = T._ego(rec)
    fwd = np.array([math.cos(heading), math.sin(heading)])
    left = np.array([-fwd[1], fwd[0]])

    def with_actors(extra, **kw):
        return dict(base, actors=list(base["actors"]) + extra, **kw)

    depth = []
    for _ in range(draws):
        acts = []
        for a in base["actors"]:
            r = a["position"] - origin
            d = float(np.linalg.norm(r))
            pos = a["position"] + (r / d * rng.normal(0.0, T.BASE_NOISE["depth_rel"] * d) if d > 1e-6 else 0.0)
            acts.append(dict(a, position=pos, velocity=a["velocity"] + rng.normal(0.0, T.BASE_NOISE["vel"], 2)))
        depth.append(dict(base, actors=acts))

    points = occluded_points(rec, base, max_points)
    static = [with_actors([hypothetical_actor("hyp", "DefaultVehicle", p, (0.0, 0.0), h)]) for p, h in points]
    ped = [with_actors([hypothetical_actor("hyp", "Pedestrian", p, (0.0, 0.0), h + math.pi / 2)]) for p, h in points]

    light = []
    if T.light_stop_distance(rec) is not None and base["light"] is None:
        light = [dict(base, light=RED), dict(base, light=GREEN)]

    speed = float(rec["ego"]["speed"]) + REAR_EXTRA_SPEED
    rear = [with_actors([hypothetical_actor("hyp", "DefaultVehicle", origin - REAR_GAP * fwd + s * LANE_WIDTH * left, speed * fwd, heading)])
            for s in (1, -1)]
    return dict(depth=depth, occl_static=static, occl_ped=ped, light=light, rear=rear)
