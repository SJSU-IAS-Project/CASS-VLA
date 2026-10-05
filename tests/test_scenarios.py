"""Fast headless checks: every family builds, runs, and exposes signal + hazard state."""
import numpy as np
import pytest

from cassvla.scenarios import FAMILIES, make_env
from cassvla.scenarios.signals import GREEN, RED, YELLOW


@pytest.mark.parametrize("family", list(FAMILIES))
def test_family_builds_and_runs(family):
    env = make_env(family, seed=0, num_scenarios=2)
    try:
        for seed in (0, 1):
            env.reset(seed=seed)
            hz = env.hazards.get_state()
            assert hz["family"] == family
            for _ in range(40):
                env.step([0.0, 0.5])
            sig = env.signals.get_state()
            if FAMILIES[family].signals.get("enabled"):
                assert len(sig["lights"]) > 0, "intersection family must spawn lights"
                assert sig["ego_status"] in (GREEN, YELLOW, RED)
                assert set(sig["approaches"].values()) == {"ego", "cross"}
                assert all(v in (GREEN, YELLOW, RED) for v in sig["lights"].values())
            else:
                assert sig["lights"] == {}
            for h in env.hazards.get_state()["hazards"].values():
                assert "position" in h or "positions" in h
    finally:
        env.close()


def test_replay_is_deterministic():
    def run(seed):
        env = make_env("occluded_cross_traffic", seed=0, num_scenarios=3)
        env.reset(seed=seed)
        trace = []
        for _ in range(60):
            env.step([0.0, 0.5])
            hz = env.hazards.get_state()["hazards"]
            trace.append([*env.agent.position, *hz["runner"]["position"], hz["runner"]["speed"]])
        env.close()
        return np.array(trace)

    a, b = run(2), run(2)
    assert np.abs(a - b).max() == 0.0
