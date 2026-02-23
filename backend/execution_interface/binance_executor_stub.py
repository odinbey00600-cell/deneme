from backend.execution_interface.abstract_executor import AbstractExecutor


class BinanceExecutorStub(AbstractExecutor):
    async def place_order(self, side: str, qty: float):
        raise RuntimeError('Binance live execution disabled in simulation mode')

    async def close_position(self):
        raise RuntimeError('Binance live execution disabled in simulation mode')

    def update_mark_price(self, mark_price: float):
        return None

    def get_position(self) -> dict:
        return {}

    def get_balance(self) -> float:
        return 0.0
