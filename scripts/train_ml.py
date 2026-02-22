from src.config.settings import get_settings
from src.data.binance_client import BinanceFuturesGateway
from src.features.indicators import add_indicators, create_target
from src.ml.model import SignalFilterModel


def main() -> None:
    settings = get_settings()
    gateway = BinanceFuturesGateway(settings.binance_api_key, settings.binance_api_secret, settings.use_testnet)
    symbol = settings.symbols[0]
    klines = gateway.fetch_klines(symbol, "1m", settings.history_limit)
    feat = add_indicators(klines)
    target = create_target(feat).iloc[:-1]
    feat = feat.iloc[:-1]

    model = SignalFilterModel("rf")
    report = model.train(feat, target)
    model.save("models/ml_filter.joblib")
    print(report)


if __name__ == "__main__":
    main()
