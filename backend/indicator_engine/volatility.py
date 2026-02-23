from collections import deque
import numpy as np


class Volatility:
    def __init__(self, window: int = 30):
        self.window = window
        self.prices = deque(maxlen=window)

    def update(self, price: float) -> float:
        self.prices.append(price)
        if len(self.prices) < 2:
            return 0.0
        arr = np.array(self.prices, dtype=float)
        returns = np.diff(np.log(arr))
        return float(np.std(returns) * (len(returns) ** 0.5))
