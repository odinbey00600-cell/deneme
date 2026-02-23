from __future__ import annotations

from dataclasses import dataclass, field

from app.config import settings
from app.ml.filter import MLTradeFilter
from app.models import BotSnapshot, BotStatus, Position, Side, TradeRecord
from app.rl.agent import TimingRLAgent
from app.risk.manager import RiskManager
from app.sim.futures_engine import FuturesSimulator
from app.strategy.hybrid import RuleStrategy
from app.strategy.indicators import compute_features


@dataclass
class TradingBot:
    bot_id: int
    generation: int
    balance: float = settings.initial_balance
    status: BotStatus = BotStatus.ACTIVE
    rule: RuleStrategy = field(default_factory=RuleStrategy)
    ml: MLTradeFilter = field(default_factory=MLTradeFilter)
    rl: TimingRLAgent = field(default_factory=TimingRLAgent)
    risk: RiskManager = field(default_factory=lambda: RiskManager(settings.risk_per_trade, settings.min_leverage, settings.max_leverage))
    positions: dict[str, Position] = field(default_factory=dict)
    recent_trades: list[TradeRecord] = field(default_factory=list)
    peak_equity: float = settings.initial_balance
    daily_pnl: float = 0.0
    consecutive_losses: int = 0

    def snapshot(self, prices: dict[str, float]) -> BotSnapshot:
        upnl = 0.0
        liq = {}
        for sym, pos in self.positions.items():
            mark = prices[sym]
            pos.mark_price = mark
            upnl += FuturesSimulator.unrealized_pnl(pos, mark)
            liq[sym] = FuturesSimulator.liquidation_price(pos, self.balance)
        equity = self.balance + upnl
        self.peak_equity = max(self.peak_equity, equity)
        dd = (self.peak_equity - equity) / max(self.peak_equity, 1e-9)
        return BotSnapshot(
            bot_id=self.bot_id,
            generation=self.generation,
            status=self.status,
            balance=self.balance,
            equity=equity,
            unrealized_pnl=upnl,
            drawdown=dd,
            leverage=max((p.leverage for p in self.positions.values()), default=1),
            positions=self.positions,
            liquidation_price=liq,
            recent_trades=self.recent_trades[-20:],
        )

    def step(self, symbol: str, df, price: float) -> TradeRecord | None:
        if self.status != BotStatus.ACTIVE:
            return None
        features = compute_features(df)
        signal = self.rule.decide(features)
        feat_vec = [features[k] for k in ["ema_fast", "ema_slow", "vwap", "rsi", "atr", "volatility", "regime"]]
        ml_dir, conf = self.ml.predict(feat_vec, signal.direction)
        rl_action = self.rl.act(features)

        if symbol in self.positions and rl_action == 2:
            return self._close(symbol, price, f"rl exit | {signal.reason}", conf, rl_action)

        if signal.direction == 0 or ml_dir == 0 or conf < 0.52 or rl_action != 1 or symbol in self.positions:
            return None

        risk = self.risk.assess(
            equity=self.balance,
            price=price,
            atr=features["atr"],
            daily_loss=self.daily_pnl,
            daily_limit=settings.daily_loss_limit,
            consecutive_losses=self.consecutive_losses,
            max_consecutive_losses=settings.max_consecutive_losses,
        )
        if not risk.approved:
            tr = TradeRecord(symbol=symbol, action="REJECTED", reason=risk.reason, ml_confidence=conf, rl_action=str(rl_action), risk_approved=False)
            self.recent_trades.append(tr)
            return tr

        side = Side.LONG if ml_dir > 0 else Side.SHORT
        self.positions[symbol] = Position(symbol=symbol, side=side, qty=risk.qty, entry_price=price, mark_price=price, leverage=risk.leverage)
        tr = TradeRecord(symbol=symbol, action="OPEN", side=side, qty=risk.qty, price=price, reason=signal.reason, ml_confidence=conf, rl_action=str(rl_action), risk_approved=True)
        self.recent_trades.append(tr)
        return tr

    def _close(self, symbol: str, price: float, reason: str, conf: float, rl_action: int) -> TradeRecord:
        pos = self.positions.pop(symbol)
        pnl = FuturesSimulator.unrealized_pnl(pos, price)
        self.balance += pnl
        self.daily_pnl += pnl
        self.consecutive_losses = self.consecutive_losses + 1 if pnl < 0 else 0
        tr = TradeRecord(symbol=symbol, action="CLOSE", side=pos.side, qty=pos.qty, price=price, pnl=pnl, reason=reason, ml_confidence=conf, rl_action=str(rl_action), risk_approved=True)
        self.recent_trades.append(tr)
        return tr

    def liquidate(self, symbol: str, price: float) -> TradeRecord:
        pos = self.positions.pop(symbol)
        pnl = FuturesSimulator.unrealized_pnl(pos, price)
        self.balance += pnl
        self.status = BotStatus.DEAD
        tr = TradeRecord(symbol=symbol, action="LIQUIDATION", side=pos.side, qty=pos.qty, price=price, pnl=pnl, reason="equity <= maintenance margin", risk_approved=True)
        self.recent_trades.append(tr)
        return tr
