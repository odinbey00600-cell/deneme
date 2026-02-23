from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'btc-sim-lab'
    env: str = 'development'
    api_host: str = '0.0.0.0'
    api_port: int = 8000

    ws_symbol: str = 'btcusdt'
    ws_base: str = 'wss://fstream.binance.com/stream?streams='
    decision_interval_seconds: int = 1

    db_url: str = 'postgresql+psycopg2://postgres:postgres@postgres:5432/simlab'
    redis_url: str = 'redis://redis:6379/0'

    seed: int = 42
    leverage: float = 125.0
    initial_balance: float = 100.0
    maintenance_margin_rate: float = 0.004
    taker_fee: float = 0.0004
    min_latency_ms: int = 100
    max_latency_ms: int = 400
    slippage_bps_mean: float = 2.0
    slippage_bps_std: float = 1.0

    funding_interval_hours: int = 8
    heartbeat_timeout_seconds: int = 15


settings = Settings()
