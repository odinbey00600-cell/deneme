from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    symbol: str = os.getenv("SYMBOL", "btcusdt")
    initial_balance: float = float(os.getenv("INITIAL_BALANCE", "100"))
    leverage: int = int(os.getenv("LEVERAGE", "125"))
    maintenance_margin_rate: float = float(os.getenv("MAINT_MARGIN_RATE", "0.004"))
    taker_fee_rate: float = float(os.getenv("TAKER_FEE_RATE", "0.0004"))
    slippage_bps: float = float(os.getenv("SLIPPAGE_BPS", "4"))
    min_latency_ms: int = int(os.getenv("MIN_LATENCY_MS", "100"))
    max_latency_ms: int = int(os.getenv("MAX_LATENCY_MS", "300"))
    seed: int = int(os.getenv("SIM_SEED", "42"))
    db_path: Path = Path(os.getenv("SQLITE_PATH", "sim.db"))
    replay_dir: Path = Path(os.getenv("REPLAY_DIR", "replays"))
    funding_interval_hours: int = 8


settings = Settings()
