from dataclasses import dataclass


@dataclass
class RiskSnapshot:
    exposure_ratio: float
    margin_usage: float
    trade_frequency: float
    liquidation_proximity: float
    risk_adjusted_return: float
