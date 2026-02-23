class MarkPriceTracker:
    def __init__(self):
        self.mark_price = 0.0

    def update(self, payload: dict) -> float:
        self.mark_price = float(payload['p'])
        return self.mark_price
