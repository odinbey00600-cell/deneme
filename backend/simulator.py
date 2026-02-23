from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import settings
from .db import Database
from .execution_engine import ExecutionEngine
from .liquidation_engine import LiquidationEngine
from .market_state import MarketState
from .strategy_agent import StrategyAgent


@dataclass
class Position:
    side: int = 0
    qty: float = 0.0
    entry: float = 0.0
    open_ts: float = 0.0


@dataclass
class SimState:
    generation: int = 1
    balance: float = settings.initial_balance
    max_equity: float = settings.initial_balance
    position: Position = field(default_factory=Position)
    realized_pnl: float = 0.0
    liquidations: int = 0
    gen_start_ts: float = field(default_factory=time.time)


class Simulator:
    def __init__(self, db: Database, market: MarketState):
        self.db = db
        self.market = market
        self.exec_engine = ExecutionEngine(settings.seed)
        self.agent = StrategyAgent(settings.seed)
        self.state = SimState()
        self.running = False
        settings.replay_dir.mkdir(exist_ok=True, parents=True)
        self.replay_file = settings.replay_dir / "live_stream.jsonl"

    def _equity(self) -> float:
        return self.state.balance + self._unrealized_pnl()

    def _unrealized_pnl(self) -> float:
        p = self.state.position
        if p.side == 0:
            return 0.0
        return (self.market.mark_price - p.entry) * p.qty * p.side

    def _distance_to_liq(self) -> float:
        p = self.state.position
        if p.side == 0:
            return 1.0
        liq = LiquidationEngine.liquidation_price(
            p.entry, p.qty, max(self.state.balance, 1e-6), p.side
        )
        if p.side > 0:
            dist = (self.market.mark_price - liq) / self.market.mark_price
        else:
            dist = (liq - self.market.mark_price) / self.market.mark_price
        return max(0.0, dist)

    def _build_state(self) -> list[float]:
        close = self.market.close_price or self.market.mark_price or 1
        return [
            close / 100_000,
            self.market.indicators.ema(9) / close,
            self.market.indicators.ema(21) / close,
            self.market.indicators.rsi() / 100,
            self.market.indicators.volatility(),
            self.market.order_book_imbalance(),
            self._unrealized_pnl() / max(1.0, self.state.balance),
            self._distance_to_liq(),
            float(self.state.position.side),
            (time.time() - self.state.position.open_ts) / 3600 if self.state.position.side else 0.0,
        ]

    async def _open(self, side: int):
        if self.state.position.side != 0 or self.market.mark_price <= 0:
            return
        margin = self.state.balance
        qty = (margin * settings.leverage) / self.market.mark_price
        px, fee, _ = await self.exec_engine.execute_price(self.market.mark_price, "BUY" if side > 0 else "SELL")
        self.state.balance -= fee
        self.state.position = Position(side=side, qty=qty, entry=px, open_ts=time.time())
        await self.db.execute(
            "INSERT INTO trades(ts,generation_id,side,qty,price,fee,pnl) VALUES(?,?,?,?,?,?,?)",
            (int(time.time() * 1000), self.state.generation, "LONG" if side > 0 else "SHORT", qty, px, fee, 0.0),
        )

    async def _close(self, reason: str = "manual"):
        p = self.state.position
        if p.side == 0:
            return
        px, fee, _ = await self.exec_engine.execute_price(self.market.mark_price, "SELL" if p.side > 0 else "BUY")
        pnl = (px - p.entry) * p.qty * p.side
        self.state.balance += pnl - fee
        self.state.balance = max(0.0, self.state.balance)
        self.state.realized_pnl += pnl
        await self.db.execute(
            "INSERT INTO trades(ts,generation_id,side,qty,price,fee,pnl) VALUES(?,?,?,?,?,?,?)",
            (int(time.time() * 1000), self.state.generation, f"CLOSE_{reason.upper()}", p.qty, px, fee, pnl),
        )
        self.state.position = Position()

    async def _apply_funding(self):
        p = self.state.position
        if p.side == 0:
            return
        payment = p.qty * self.market.mark_price * self.market.funding_rate * p.side
        self.state.balance -= payment
        self.state.balance = max(0.0, self.state.balance)

    async def _liquidate(self):
        self.state.liquidations += 1
        await self.db.execute(
            "INSERT INTO liquidation_events(ts,generation_id,mark_price,equity,distance) VALUES(?,?,?,?,?)",
            (int(time.time() * 1000), self.state.generation, self.market.mark_price, self._equity(), self._distance_to_liq()),
        )
        score = self.agent.train_and_mutate()
        survival = time.time() - self.state.gen_start_ts
        await self.db.execute(
            "INSERT OR REPLACE INTO generations(id,start_ts,end_ts,survival_sec,max_equity,liquidation_count,score) VALUES(?,?,?,?,?,?,?)",
            (self.state.generation, int(self.state.gen_start_ts), int(time.time()), survival, self.state.max_equity, 1, score),
        )
        self.state = SimState(generation=self.state.generation + 1)

    async def step(self):
        if self.market.mark_price <= 0:
            return
        st = self._build_state()
        action = self.agent.choose_action(st)
        if action == "OPEN_LONG":
            await self._open(1)
        elif action == "OPEN_SHORT":
            await self._open(-1)
        elif action == "CLOSE_POSITION":
            await self._close()

        if int(time.time()) % (settings.funding_interval_hours * 3600) == 0:
            await self._apply_funding()

        p = self.state.position
        if p.side != 0:
            liq = LiquidationEngine.liquidation_price(p.entry, p.qty, max(self.state.balance, 1e-6), p.side)
            if LiquidationEngine.should_liquidate(self.market.mark_price, liq, p.side):
                self.agent.remember(st, action, -100.0)
                self.state.balance = 0
                self.state.position = Position()
                await self._liquidate()
                await self.db.commit()
                return

        eq = self._equity()
        # ---- HARD EQUITY FLOOR ----
        if eq <= 0:
            self.agent.remember(st, action, -100.0)
            self.state.balance = 0.0
            self.state.position = Position()
            await self._liquidate()
            await self.db.commit()
            return
        # ----------------------------
        self.state.max_equity = max(self.state.max_equity, eq)
        dd = 0.0 if self.state.max_equity == 0 else (self.state.max_equity - eq) / self.state.max_equity
        reward = (eq - settings.initial_balance) - (dd * 5) - (0.001 if action != "HOLD" else 0)
        self.agent.remember(st, action, reward)
        await self.db.execute(
            "INSERT INTO equity_history(ts,generation_id,equity,drawdown) VALUES(?,?,?,?)",
            (int(time.time() * 1000), self.state.generation, eq, dd),
        )
        with self.replay_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": int(time.time() * 1000), "action": action, "equity": eq, "mark": self.market.mark_price, "gen": self.state.generation}) + "\n")

    async def run(self):
        self.running = True
        while self.running:
            await self.step()
            await self.db.commit()
            await asyncio.sleep(1)

    def snapshot(self) -> dict:
        p = self.state.position
        return {
            "generation": self.state.generation,
            "balance": self.state.balance,
            "unrealized_pnl": self._unrealized_pnl(),
            "position": "LONG" if p.side > 0 else "SHORT" if p.side < 0 else "FLAT",
            "distance_to_liquidation": self._distance_to_liq(),
            "time_alive_sec": time.time() - self.state.gen_start_ts,
            "liquidations": self.state.liquidations,
            "latency_ms": self.market.ws_latency_ms,
            "mark_price": self.market.mark_price,
            "ema9": self.market.indicators.ema(9),
            "ema21": self.market.indicators.ema(21),
        }

    def replay(self, path: Path):
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        return [json.loads(l) for l in lines if l.strip()]
