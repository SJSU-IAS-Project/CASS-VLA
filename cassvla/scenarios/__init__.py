"""Scripted MetaDrive scenario families for PlanDiscrim (Phase 1).

    from cassvla.scenarios import make_env, FAMILIES
    env = make_env("occluded_cross_traffic", seed=3)
    obs, info = env.reset(seed=3)
    env.signals.get_state()   # traffic-light phases, per lane
    env.hazards.get_state()   # scripted actors, triggers
"""
from cassvla.scenarios.env import HazardEnv, make_env
from cassvla.scenarios.families import FAMILIES, FamilySpec
from cassvla.scenarios.signals import SignalManager
from cassvla.scenarios.hazards import HazardManager

__all__ = ["HazardEnv", "make_env", "FAMILIES", "FamilySpec", "SignalManager", "HazardManager"]
