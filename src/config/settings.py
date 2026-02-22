from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["dev", "prod"] = "prod"

    binance_api_key: str = Field(..., alias="BINANCE_API_KEY")
    binance_api_secret: str = Field(..., alias="BINANCE_API_SECRET")
    use_testnet: bool = Field(default=False, alias="BINANCE_TESTNET")

    symbols: list[str] = Field(default_factory=lambda: ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"])
    max_open_positions: int = 3

    risk_per_trade: float = 0.005
    max_daily_loss_pct: float = 0.03
    safe_mode_equity_pct: float = 0.8
    max_consecutive_losses: int = 3
    cooldown_minutes: int = 20
    rr_min: float = 2.0

    leverage_min: int = 1
    leverage_max: int = 10

    ml_confidence_threshold: float = 0.55

    history_limit: int = 3000

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    @field_validator("risk_per_trade")
    @classmethod
    def validate_risk_per_trade(cls, value: float) -> float:
        if not 0 < value <= 0.01:
            raise ValueError("risk_per_trade must be between 0 and 0.01")
        return value

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("at least one symbol must be configured")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
