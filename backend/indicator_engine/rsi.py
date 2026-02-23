class RSI:
    def __init__(self, period: int = 14):
        self.period = period
        self.avg_gain = None
        self.avg_loss = None
        self.prev = None

    def update(self, price: float) -> float:
        if self.prev is None:
            self.prev = price
            return 50.0
        delta = price - self.prev
        gain = max(delta, 0)
        loss = max(-delta, 0)
        if self.avg_gain is None:
            self.avg_gain = gain
            self.avg_loss = loss
        else:
            self.avg_gain = (self.avg_gain * (self.period - 1) + gain) / self.period
            self.avg_loss = (self.avg_loss * (self.period - 1) + loss) / self.period
        self.prev = price
        if self.avg_loss == 0:
            return 100.0
        rs = self.avg_gain / self.avg_loss
        return 100 - (100 / (1 + rs))
