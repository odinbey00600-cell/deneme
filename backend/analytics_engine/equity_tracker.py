class EquityTracker:
    def __init__(self):
        self.series = []

    def update(self, ts: int, equity: float):
        self.series.append({'ts': ts, 'equity': equity})
