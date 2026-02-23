
def reward_function(
    delta_equity: float,
    drawdown: float,
    trade_frequency: float,
    liquidation: bool,
    volatility_risk: float,
    weights: dict,
) -> float:
    return (
        delta_equity
        - weights['drawdown'] * drawdown
        - weights['trade_frequency'] * trade_frequency
        - (weights['liquidation_penalty'] if liquidation else 0)
        - weights['volatility_risk'] * volatility_risk
    )
