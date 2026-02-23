from backend.analytics_engine.sharpe_ratio import sharpe
from backend.analytics_engine.expectancy_calculator import expectancy


def compute_metrics(equities: list[float], trades: list[dict], liquidations: int) -> dict:
    wins = [t['realized_pnl'] for t in trades if t['realized_pnl'] > 0]
    losses = [t['realized_pnl'] for t in trades if t['realized_pnl'] <= 0]
    dd = 0.0
    peak = -1e9
    for e in equities:
        peak = max(peak, e)
        if peak > 0:
            dd = max(dd, (peak - e) / peak)
    return {
        'sharpe': sharpe(equities),
        'expectancy': expectancy(wins, losses),
        'max_drawdown': dd,
        'liquidation_frequency': liquidations / max(1, len(trades))
    }
