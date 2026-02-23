import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    sandbox_mode: bool = os.getenv("SANDBOX_MODE", "0") == "1"
    symbols: list[str] = field(default_factory=lambda: ["btcusdt", "ethusdt", "solusdt", "bnbusdt"])
    initial_balance: float = 100.0
    max_leverage: int = 10
    min_leverage: int = 1
    risk_per_trade: float = 0.01
    daily_loss_limit: float = 0.05
    safe_mode_equity_ratio: float = 0.5
    max_consecutive_losses: int = 3
    circuit_breaker_atr_ratio: float = 0.03
    liquidation_streak_stop: int = 3
    ui_refresh_ms: int = 1000
    memory_path: str = "data/learning_memory.json"


settings = Settings()
