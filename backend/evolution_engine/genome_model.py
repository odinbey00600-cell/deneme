from dataclasses import dataclass, asdict


@dataclass
class Genome:
    ema_short: int = 8
    ema_long: int = 21
    rsi_period: int = 14
    risk_aggressiveness: float = 1.0
    reward_weights: dict = None
    exploration_rate: float = 0.1
    exit_bias: float = 0.0
    stop_tightening_sensitivity: float = 0.1

    def __post_init__(self):
        if self.reward_weights is None:
            self.reward_weights = {'lambda1': 0.3, 'lambda2': 0.02, 'lambda3': 100.0, 'lambda4': 0.5}

    def to_dict(self):
        return asdict(self)
