import time
from backend.execution_interface.abstract_executor import AbstractExecutor
from backend.simulated_execution_engine.execution_latency_simulator import apply_latency
from backend.simulated_execution_engine.slippage_model import apply_slippage
from backend.simulated_execution_engine.fee_model import taker_fee
from backend.simulated_execution_engine.order_matching import fill_order


class SimulatedExecutor(AbstractExecutor):
    def __init__(self, settings):
        self.settings = settings
        self.balance = settings.initial_balance
        self.position = {'side': None, 'qty': 0.0, 'entry_price': 0.0, 'opened_at': None}
        self.mark_price = 0.0

    def update_mark_price(self, mark_price: float):
        self.mark_price = mark_price

    async def place_order(self, side: str, qty: float, volatility: float = 0.001):
        latency = await apply_latency(self.settings.execution_latency_min_ms, self.settings.execution_latency_max_ms)
        slipped = apply_slippage(self.mark_price, side, volatility)
        order = fill_order(self.mark_price, qty, side, slipped)
        notional = qty * slipped
        fee = taker_fee(notional, self.settings.taker_fee_rate)
        self.balance -= fee
        self.position = {
            'side': 'LONG' if side == 'BUY' else 'SHORT',
            'qty': qty,
            'entry_price': slipped,
            'opened_at': time.time(),
            'latency_ms': latency
        }
        return {**order, 'fee': fee, 'latency_ms': latency}

    async def close_position(self):
        if not self.position['side']:
            return None
        side = 'SELL' if self.position['side'] == 'LONG' else 'BUY'
        qty = self.position['qty']
        slipped = apply_slippage(self.mark_price, side, 0.001)
        entry = self.position['entry_price']
        direction = 1 if self.position['side'] == 'LONG' else -1
        realized = (slipped - entry) * qty * direction
        fee = taker_fee(qty * slipped, self.settings.taker_fee_rate)
        self.balance += realized - fee
        closed = {'realized_pnl': realized, 'fee': fee, 'exit_price': slipped}
        self.position = {'side': None, 'qty': 0.0, 'entry_price': 0.0, 'opened_at': None}
        return closed

    def get_position(self) -> dict:
        return self.position

    def get_balance(self) -> float:
        return self.balance
