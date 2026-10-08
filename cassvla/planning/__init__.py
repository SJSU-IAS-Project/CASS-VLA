"""Candidate trajectories and oracle scoring for PlanDiscrim (Phase 2).

    from cassvla.planning import Oracle
    oracle = Oracle("lane_blockage", start_seed=0, num_scenarios=4)
    rec = oracle.label(seed=2, t_dec=1.5)
    rec["c_star"], rec["oracle_order"], rec["metrics"]["keep"]
"""
from cassvla.planning.candidates import Candidate, generate_candidates
from cassvla.planning.control import Tracker
from cassvla.planning.oracle import Oracle

__all__ = ["Candidate", "generate_candidates", "Tracker", "Oracle"]
