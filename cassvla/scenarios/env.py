"""HazardEnv: MetaDriveEnv plus the signal and hazard managers."""
import numpy as np
from metadrive.constants import DEFAULT_AGENT
from metadrive.envs.metadrive_env import MetaDriveEnv

from cassvla.scenarios.families import EGO_LANE, FAMILIES, SIGNAL_BUILDERS
from cassvla.scenarios.hazards import HazardManager
from cassvla.scenarios.signals import DEFAULT_SIGNAL_CONFIG, SignalManager


class HazardEnv(MetaDriveEnv):
    @classmethod
    def default_config(cls):
        cfg = super().default_config()
        cfg.update(dict(family=None, signal_config=dict(DEFAULT_SIGNAL_CONFIG)), allow_add_new_key=True)
        return cfg

    def setup_engine(self):
        super().setup_engine()
        self.engine.register_manager("signal_manager", SignalManager())
        self.engine.register_manager("hazard_manager", HazardManager())

    def reset(self, seed=None):
        # per-seed signal schedule for families that randomise it; must be set before managers reset
        fam = self.config["family"]
        if fam in SIGNAL_BUILDERS:
            s = self.config["start_seed"] if seed is None else seed
            rng = np.random.default_rng(int(s) + 7919)
            self.config["signal_config"].update(SIGNAL_BUILDERS[fam](rng))
        return super().reset(seed=seed)

    @property
    def signals(self) -> SignalManager:
        return self.engine.signal_manager

    @property
    def hazards(self) -> HazardManager:
        return self.engine.hazard_manager


def make_env(family: str, seed: int = 0, num_scenarios: int = 1, use_render: bool = False, **overrides) -> HazardEnv:
    """Build a HazardEnv for one family. ``env.reset(seed=s)`` with start_seed <= s < start_seed + num_scenarios."""
    spec = FAMILIES[family]
    agent_cfg = dict(use_special_color=True, spawn_lane_index=EGO_LANE, spawn_longitude=5.0)
    if spec.ego_destination:
        agent_cfg["destination"] = spec.ego_destination
    cfg = dict(
        family=family,
        map=spec.map,
        start_seed=seed,
        num_scenarios=num_scenarios,
        traffic_density=spec.traffic_density,
        traffic_mode="hybrid",
        random_spawn_lane_index=False,
        random_traffic=False,
        accident_prob=0.0,
        horizon=spec.horizon,
        use_render=use_render,
        signal_config=dict(DEFAULT_SIGNAL_CONFIG, **spec.signals),
        agent_configs={DEFAULT_AGENT: agent_cfg},
        log_level=30,
    )
    cfg.update(spec.env_overrides)
    cfg.update(overrides)
    return HazardEnv(cfg)
