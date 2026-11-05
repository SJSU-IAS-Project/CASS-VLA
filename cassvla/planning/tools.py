"""Simulated perception (refined proposal section 3): what the ego sees, and three tool responses.

Everything here works on a logged oracle record, so no tool call touches the simulator. Noise levels
are assumptions; ``perfect`` returns ground truth and the same record always gives the same output.
"""
import math
import zlib

import numpy as np

CAMERA_RANGE, CAMERA_HALF_FOV = 60.0, math.radians(45.0)
LIGHT_READABLE_RANGE = 20.0
TRACK_RANGE = 50.0
ROI_MARGIN = 10.0
MIN_OCCLUDER_LENGTH = 3.0
BASE_NOISE = dict(depth_rel=0.15, vel=2.0)
LEVELS = {
    "perfect": dict(depth_rel=0.0, vel=0.0, miss=0.0, false_pos=0.0, track_pos=0.0, roi_rel=0.0, roi_vel=0.0),
    "low": dict(depth_rel=0.02, vel=0.2, miss=0.02, false_pos=0.02, track_pos=0.2, roi_rel=0.05, roi_vel=0.5),
    "mid": dict(depth_rel=0.05, vel=0.5, miss=0.10, false_pos=0.05, track_pos=0.5, roi_rel=0.08, roi_vel=1.0),
    "high": dict(depth_rel=0.10, vel=1.0, miss=0.25, false_pos=0.15, track_pos=1.0, roi_rel=0.12, roi_vel=1.5),
}
TOOLS = ("roi", "depth", "collision")
TOOL_COST = 1.0


def rng_for(rec, *key):
    return np.random.default_rng(zlib.crc32("|".join(map(str, (rec["family"], rec["seed"], rec["t_dec"], *key))).encode()))


def _ego(rec):
    return np.array(rec["ego"]["position"][:2], float), float(rec["ego"]["heading"])


def _segments_cross(a, b, c, d):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0


def blocked(origin, target, polys):
    """True if the sight line crosses any polygon edge."""
    for poly in polys:
        for i in range(4):
            if _segments_cross(origin, target, poly[i], poly[(i + 1) % 4]):
                return True
    return False


def _occluders(rec, skip=None):
    return [a["poly"] for a in rec["actors"] if a["length"] >= MIN_OCCLUDER_LENGTH and a["name"] != skip]


def line_of_sight(rec, actor):
    """An actor is in sight if its centre or any corner has a clear line from the ego."""
    origin, _ = _ego(rec)
    polys = _occluders(rec, skip=actor["name"])
    return any(not blocked(origin, np.array(p, float), polys) for p in [actor["position"], *actor["poly"]])


def in_camera(rec, actor):
    origin, heading = _ego(rec)
    r = np.array(actor["position"], float) - origin
    dist = float(np.linalg.norm(r))
    bearing = abs((math.atan2(r[1], r[0]) - heading + math.pi) % (2 * math.pi) - math.pi)
    return dist <= CAMERA_RANGE and bearing <= CAMERA_HALF_FOV and line_of_sight(rec, actor)


def _belief(actor, pos, vel, source):
    return dict(name=actor["name"], type=actor["type"], position=np.asarray(pos, float), velocity=np.asarray(vel, float),
                heading=actor["heading"], length=actor["length"], width=actor["width"], source=source)


def _noisy(rec, actor, rng, depth_rel, vel_sigma, source):
    origin, _ = _ego(rec)
    pos, vel = np.array(actor["position"], float), np.array(actor["measured_velocity"], float)
    r = pos - origin
    dist = float(np.linalg.norm(r))
    if dist > 1e-6 and depth_rel > 0:
        pos = pos + r / dist * rng.normal(0.0, depth_rel * dist)
    if vel_sigma > 0:
        vel = vel + rng.normal(0.0, vel_sigma, 2)
    return _belief(actor, pos, vel, source)


def light_stop_distance(rec):
    points = rec["signals"].get("ego_stop_points") or {}
    if not points:
        return None
    origin, heading = _ego(rec)
    fwd = np.array([math.cos(heading), math.sin(heading)])
    ahead = [float(np.dot(np.array(p[:2], float) - origin, fwd)) for p in points.values()]
    ahead = [d for d in ahead if d > -1.0]
    return min(ahead) if ahead else None


def base_observation(rec):
    """Front camera only: noisy range and velocity, no occluded or rear actors, light readable when near."""
    rng = rng_for(rec, "base")
    actors = [_noisy(rec, a, rng, BASE_NOISE["depth_rel"], BASE_NOISE["vel"], "base") for a in rec["actors"] if in_camera(rec, a)]
    d = light_stop_distance(rec)
    light = rec["signals"].get("ego_status") if d is not None and d <= LIGHT_READABLE_RANGE else None
    return dict(actors=actors, light=light, collision=None)


def _in_roi(rec, actor):
    origin, heading = _ego(rec)
    pos = np.array(actor["position"], float)
    r = pos - origin
    if r[0] * math.cos(heading) + r[1] * math.sin(heading) < 0:
        return False
    return any(np.min(np.linalg.norm(np.array(c["xy"], float) - pos, axis=1)) <= ROI_MARGIN for c in rec["candidates"])


def tool_roi(rec, level):
    """Objects in the forward corridor of the candidates, occluded or not, and the light state."""
    p, rng = LEVELS[level], rng_for(rec, "roi", level)
    found = []
    for a in rec["actors"]:
        if _in_roi(rec, a) and rng.random() >= p["miss"]:
            found.append(_noisy(rec, a, rng, p["roi_rel"], p["roi_vel"], "roi"))
    if rng.random() < p["false_pos"] and rec["candidates"]:
        xy = np.array(rec["candidates"][int(rng.integers(len(rec["candidates"])))]["xy"], float)
        q = xy[int(rng.integers(len(xy) // 2, len(xy)))] + rng.normal(0.0, 1.0, 2)
        found.append(dict(name="phantom", type="DefaultVehicle", position=q, velocity=np.zeros(2), heading=float(rec["ego"]["heading"]),
                          length=4.5, width=1.9, source="roi"))
    light = rec["signals"].get("ego_status") if light_stop_distance(rec) is not None and rng.random() >= p["miss"] else None
    return dict(actors=found, light=light)


def tool_depth(rec, level):
    """Accurate range and velocity for the actors already in the camera view."""
    p, rng = LEVELS[level], rng_for(rec, "depth", level)
    return dict(actors=[_noisy(rec, a, rng, p["depth_rel"], p["vel"], "depth") for a in rec["actors"] if in_camera(rec, a)])


def tool_collision(rec, level):
    """Tracked state of every unoccluded actor around the ego, front or rear, for a per-candidate geometric check."""
    p, rng = LEVELS[level], rng_for(rec, "collision", level)
    origin, _ = _ego(rec)
    tracked = []
    for a in rec["actors"]:
        near = np.linalg.norm(np.array(a["position"], float) - origin) <= TRACK_RANGE
        if near and line_of_sight(rec, a) and rng.random() >= p["miss"]:
            pos = np.array(a["position"], float) + rng.normal(0.0, p["track_pos"], 2) if p["track_pos"] > 0 else np.array(a["position"], float)
            vel = np.array(a["measured_velocity"], float) + rng.normal(0.0, p["vel"], 2) if p["vel"] > 0 else np.array(a["measured_velocity"], float)
            tracked.append(_belief(a, pos, vel, "collision"))
    return dict(actors=tracked)


TOOL_FNS = dict(roi=tool_roi, depth=tool_depth, collision=tool_collision)


def merge(base, responses):
    """Newer sources replace base estimates of the same actor. Precision order: depth, collision, roi."""
    order = {"base": 0, "roi": 1, "collision": 2, "depth": 3}
    actors, light = {a["name"]: a for a in base["actors"]}, base["light"]
    for resp in responses:
        for a in resp["actors"]:
            if a["name"] not in actors or order[a["source"]] >= order[actors[a["name"]]["source"]]:
                actors[a["name"]] = a
        if resp.get("light") is not None:
            light = resp["light"]
    return dict(actors=list(actors.values()), light=light)
