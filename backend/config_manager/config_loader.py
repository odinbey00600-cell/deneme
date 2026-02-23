from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_env: str = 'development'
    log_level: str = 'INFO'
    database_url: str
    redis_url: str
    binance_ws_url: str
    binance_streams: str
    ws_ping_seconds: int = 10
    ws_timeout_seconds: int = 30
    maintenance_margin_rate: float = 0.004
    taker_fee_rate: float = 0.0004
    leverage: int = 125
    initial_balance: float = 100.0
    execution_latency_min_ms: int = 100
    execution_latency_max_ms: int = 400
    seed: int = 1337
    api_host: str = '0.0.0.0'
    api_port: int = 8000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
