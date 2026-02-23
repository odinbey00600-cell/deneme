import numpy as np


def sharpe(equities: list[float]) -> float:
    if len(equities) < 3:
        return 0.0
    returns = np.diff(np.array(equities))
    std = np.std(returns)
    if std == 0:
        return 0.0
    return float(np.mean(returns) / std * np.sqrt(252))
