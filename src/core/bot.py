from __future__ import annotations

import time
from dataclasses import dataclass

from loguru import logger

from src.config.settings import Settings
from src.data.binance_client import BinanceFuturesGateway
from src.execution.executor import OrderExecutor, PlannedOrder
from src.features.indicators import add_indicators
from src.ml.model import SignalFilterModel
from src.monitoring.analytics import PerformanceAnalytics
from src.monitoring.notifier import Notifier
from src.risk.manager import RiskManager
from src.rl.dqn import DQNAgent
from src.strategy.hybrid import HybridStrategy


@dataclass
class RuntimeState:
    is_safe_mode: bool = False


class TradingBot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.gateway = BinanceFuturesGateway(settings.binance_api_key, settings.binance_api_secret, settings.use_testnet)
        self.executor = OrderExecutor(self.gateway)
        self.strategy = HybridStrategy()
        self.risk = RiskManager(settings.max_daily_loss_pct, settings.max_consecutive_losses, settings.cooldown_minutes)
        self.ml = SignalFilterModel("rf")
        self.rl = DQNAgent(state_dim=8, action_dim=4)
        self.analytics = PerformanceAnalytics()
        self.notifier = Notifier(settings.telegram_bot_token, settings.telegram_chat_id)
        self.state = RuntimeState()

    def load_or_train_ml(self) -> None:
        import os

        model_path = "models/ml_filter.joblib"
        if os.path.exists(model_path):
            self.ml.load(model_path)
            return

        symbol = self.settings.symbols[0]
        klines = self.gateway.fetch_klines(symbol=symbol, interval="1m", limit=self.settings.history_limit)
        feat = add_indicators(klines)
        target = (feat["close"].shift(-1) > feat["close"]).astype(int).dropna()
        feat = feat.iloc[:-1]
        report = self.ml.train(feat, target)
        self.ml.save(model_path)
        logger.info("ML trained: {}", report)

    def run(self) -> None:
        self.load_or_train_ml()
        while True:
            try:
                self.loop_once()
                time.sleep(20)
            except KeyboardInterrupt:
                logger.info("graceful shutdown")
                break
            except Exception as exc:  # noqa: BLE001
                logger.exception("critical error: {}", exc)
                self.notifier.send_sync(f"Bot stopped due to error: {exc}")
                break

    def loop_once(self) -> None:
        account = self.gateway.get_account_snapshot()
        self.risk.mark_day_start(account.equity)

        if account.equity < self.risk.day_start_equity * self.settings.safe_mode_equity_pct:
            self.state.is_safe_mode = True

        if self.state.is_safe_mode:
            logger.warning("SAFE MODE active, skipping new trades")
            return

        risk_decision = self.risk.can_trade(account.equity)
        if not risk_decision.approved:
            logger.warning("Risk gate blocked trading: {}", risk_decision.reason)
            return

        open_positions = self.gateway.get_open_positions()
        if len(open_positions) >= self.settings.max_open_positions:
            return

        close_map = {}
        for symbol in self.settings.symbols:
            frame_1m = add_indicators(self.gateway.fetch_klines(symbol, "1m", self.settings.history_limit))
            frame_15m = add_indicators(self.gateway.fetch_klines(symbol, "15m", self.settings.history_limit))
            close_map[symbol] = frame_1m["close"]

            base_signal = self.strategy.scalping_signal(frame_1m)
            if base_signal.direction == 0:
                base_signal = self.strategy.swing_signal(frame_15m)
            if base_signal.direction == 0:
                continue

            ml_signal = self.ml.predict_latest(frame_1m)
            if ml_signal.confidence < self.settings.ml_confidence_threshold:
                continue
            if (ml_signal.direction == 1 and base_signal.direction < 0) or (
                ml_signal.direction == 0 and base_signal.direction > 0
            ):
                continue

            obs = self.rl.policy.net[0].weight.new_tensor([
                frame_1m.iloc[-1]["ema_spread_fast"],
                frame_1m.iloc[-1]["ema_spread_swing"],
                frame_1m.iloc[-1]["rsi14"] / 100,
                frame_1m.iloc[-1]["atr14"] / frame_1m.iloc[-1]["close"],
                frame_1m.iloc[-1]["vwap_dev"],
                frame_1m.iloc[-1]["returns_3"],
                0.0,
                0.0,
            ]).detach().cpu().numpy()
            rl_action = self.rl.act(obs)
            if rl_action.action == 0:
                continue

            atr = frame_1m.iloc[-1]["atr14"]
            price = frame_1m.iloc[-1]["close"]
            stop = price - (1.5 * atr * base_signal.direction)
            tp = price + (self.settings.rr_min * abs(price - stop) * base_signal.direction)
            lev = self.risk.dynamic_leverage(atr / price, self.settings.leverage_min, self.settings.leverage_max)
            qty = self.risk.calculate_position_size(account.equity, self.settings.risk_per_trade, price, stop)
            if qty <= 0:
                continue

            order = PlannedOrder(symbol=symbol, direction=base_signal.direction, qty=qty, leverage=lev, stop_loss=stop, take_profit=tp)
            self.executor.execute(order)
            self.notifier.send_sync(
                f"OPEN {symbol} dir={base_signal.direction} qty={qty:.4f} ml={ml_signal.confidence:.2f} rl={rl_action.action}"
            )

        corr = self.risk.correlation_matrix(close_map)
        logger.info("correlation matrix\n{}", corr)
