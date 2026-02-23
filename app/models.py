from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum


class BotStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    DEAD = "DEAD"
    PAUSED = "PAUSED"


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Position:
    symbol: str
    side: Side
    qty: float
    entry_price: float
    mark_price: float
    leverage: int
    maintenance_margin_rate: float = 0.005

    @property
    def notional(self) -> float:
        return self.qty * self.mark_price


@dataclass
class TradeRecord:
    ts: datetime = field(default_factory=datetime.utcnow)
    symbol: str = ""
    action: str = ""
    side: Side | None = None
    qty: float = 0.0
    price: float = 0.0
    pnl: float = 0.0
    reason: str = ""
    ml_confidence: float = 0.0
    rl_action: str = ""
    risk_approved: bool = False

    def model_dump(self, mode: str = "python") -> dict:
        data = asdict(self)
        data["ts"] = self.ts.isoformat()
        data["side"] = self.side.value if self.side else None
        return data


@dataclass
class BotSnapshot:
    bot_id: int
    generation: int
    status: BotStatus
    balance: float
    equity: float
    unrealized_pnl: float
    drawdown: float
    leverage: int
    positions: dict[str, Position] = field(default_factory=dict)
    liquidation_price: dict[str, float] = field(default_factory=dict)
    recent_trades: list[TradeRecord] = field(default_factory=list)

    def model_dump(self, mode: str = "python") -> dict:
        return {
            "bot_id": self.bot_id,
            "generation": self.generation,
            "status": self.status.value,
            "balance": self.balance,
            "equity": self.equity,
            "unrealized_pnl": self.unrealized_pnl,
            "drawdown": self.drawdown,
            "leverage": self.leverage,
            "positions": {
                k: {
                    "symbol": v.symbol,
                    "side": v.side.value,
                    "qty": v.qty,
                    "entry_price": v.entry_price,
                    "mark_price": v.mark_price,
                    "leverage": v.leverage,
                    "maintenance_margin_rate": v.maintenance_margin_rate,
                    "notional": v.notional,
                }
                for k, v in self.positions.items()
            },
            "liquidation_price": self.liquidation_price,
            "recent_trades": [t.model_dump(mode=mode) for t in self.recent_trades],
        }
