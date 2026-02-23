class CandleBuilder:
    def __init__(self):
        self.last_candle = None

    def update(self, kline_payload: dict) -> dict:
        k = kline_payload['k']
        candle = {
            'open_time': k['t'], 'close_time': k['T'], 'open': float(k['o']), 'high': float(k['h']),
            'low': float(k['l']), 'close': float(k['c']), 'volume': float(k['v']), 'closed': bool(k['x'])
        }
        self.last_candle = candle
        return candle
