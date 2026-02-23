from collections import deque


class EMA:
    def __init__(self, period: int):
        self.period = period
        self.mult = 2 / (period + 1)
        self.value = None

    def update(self, price: float) -> float:
        if self.value is None:
            self.value = price
        else:
            self.value = (price - self.value) * self.mult + self.value
        return self.value
