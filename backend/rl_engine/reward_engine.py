def compute_reward(delta_equity: float, drawdown: float, trade_freq: float, liquidation: bool, vol_risk: float, w: dict) -> float:
    return (
        delta_equity
        - w['lambda1'] * drawdown
        - w['lambda2'] * trade_freq
        - w['lambda3'] * (1.0 if liquidation else 0.0)
        - w['lambda4'] * vol_risk
    )
