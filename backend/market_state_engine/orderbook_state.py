class OrderBookState:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.last_update_id = None

    def apply(self, payload: dict):
        self.bids = payload.get('b', [])
        self.asks = payload.get('a', [])
        self.last_update_id = payload.get('u')
