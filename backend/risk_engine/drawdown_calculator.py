class DrawdownCalculator:
    def __init__(self):
        self.peak = 0.0

    def update(self, equity: float) -> float:
        self.peak = max(self.peak, equity)
        if self.peak == 0:
            return 0.0
        return max(0.0, (self.peak - equity) / self.peak)
