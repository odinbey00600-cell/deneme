class FundingTracker:
    def __init__(self):
        self.last_rate = 0.0
        self.next_time = None

    def update(self, payload: dict):
        self.last_rate = float(payload.get('r', 0.0))
        self.next_time = payload.get('T')
        return self.last_rate, self.next_time
