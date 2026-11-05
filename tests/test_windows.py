"""Per-family decision windows: plumbing and the lead_brake_cutin regression."""
import numpy as np

from cassvla.planning import Oracle
from cassvla.scenarios import FAMILIES


def test_family_windows():
    for spec in FAMILIES.values():
        lo, hi = spec.t_window
        times = spec.decision_times()
        assert 0.0 < lo <= hi
        assert times[0] == lo and times[-1] == hi
        assert np.allclose(np.diff(times), 0.5)
    assert FAMILIES["lead_brake_cutin"].t_window[1] > 6.0


def test_lead_brake_window_reaches_hazard():
    o = Oracle("lead_brake_cutin", start_seed=3, num_scenarios=1)
    try:
        assert not o.label(seed=3, t_dec=6.0)["retained"]        # braking lead, all candidates safe on the old 6 s grid
        assert 14.0 in FAMILIES["lead_brake_cutin"].decision_times()
        rec = o.label(seed=3, t_dec=14.0)
        assert "lead" in rec["hazards"]["hazards"]
        assert rec["retained"]
    finally:
        o.close()
