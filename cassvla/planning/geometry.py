"""Small 2D helpers: polylines with arc length, and convex-polygon distance."""
import math

import numpy as np


class Polyline:
    """A 2D path sampled densely enough to treat as piecewise linear."""

    def __init__(self, xy):
        xy = np.asarray(xy, dtype=float)
        keep = np.r_[True, np.linalg.norm(np.diff(xy, axis=0), axis=1) > 1e-6]
        self.xy = xy[keep]
        seg = np.linalg.norm(np.diff(self.xy, axis=0), axis=1)
        self.s = np.r_[0.0, np.cumsum(seg)]
        self.length = float(self.s[-1])

    def at(self, s):
        """Position and heading at arc length ``s`` (extrapolates straight past either end)."""
        s = np.atleast_1d(np.asarray(s, dtype=float))
        i = np.clip(np.searchsorted(self.s, s, side="right") - 1, 0, len(self.s) - 2)
        d = self.xy[i + 1] - self.xy[i]
        seg = np.maximum(self.s[i + 1] - self.s[i], 1e-9)
        u = ((s - self.s[i]) / seg)[:, None]
        return self.xy[i] + u * d, np.arctan2(d[:, 1], d[:, 0])

    def project(self, p):
        """Arc length of the closest point to ``p``."""
        p = np.asarray(p, dtype=float)[:2]
        a, b = self.xy[:-1], self.xy[1:]
        d = b - a
        u = np.clip(np.einsum("ij,ij->i", p - a, d) / np.maximum(np.einsum("ij,ij->i", d, d), 1e-12), 0.0, 1.0)
        dist = np.linalg.norm(a + u[:, None] * d - p, axis=1)
        i = int(np.argmin(dist))
        return float(self.s[i] + u[i] * (self.s[i + 1] - self.s[i]))


def box(center, heading, length, width):
    """Corners of an oriented rectangle, counter-clockwise."""
    c, s = math.cos(heading), math.sin(heading)
    fx, fy = c * length / 2, s * length / 2
    lx, ly = -s * width / 2, c * width / 2
    x, y = float(center[0]), float(center[1])
    return np.array([[x + fx + lx, y + fy + ly], [x - fx + lx, y - fy + ly], [x - fx - lx, y - fy - ly], [x + fx - lx, y + fy - ly]])


def _overlap(p, q):
    """Separating-axis test for two convex polygons."""
    for poly in (p, q):
        for i in range(len(poly)):
            e = poly[(i + 1) % len(poly)] - poly[i]
            n = np.array([-e[1], e[0]])
            a, b = p @ n, q @ n
            if a.max() < b.min() or b.max() < a.min():
                return False
    return True


def _point_seg(p, a, b):
    d = b - a
    u = np.clip(np.dot(p - a, d) / max(np.dot(d, d), 1e-12), 0.0, 1.0)
    return float(np.linalg.norm(a + u * d - p))


def poly_distance(p, q):
    """Distance between convex polygons; 0 if they overlap."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    if _overlap(p, q):
        return 0.0
    best = math.inf
    for P, Q in ((p, q), (q, p)):
        for pt in P:
            for i in range(len(Q)):
                best = min(best, _point_seg(pt, Q[i], Q[(i + 1) % len(Q)]))
    return best
