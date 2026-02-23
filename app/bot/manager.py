from __future__ import annotations

import asyncio
from datetime import datetime

from app.bot.bot import TradingBot
from app.config import settings
from app.market.binance_feed import BinanceMarketFeed
from app.models import BotStatus
from app.sim.futures_engine import FuturesSimulator
from app.storage.memory import LearningMemory


class BotManager:
    def __init__(self) -> None:
        self.feed = BinanceMarketFeed(settings.symbols, deterministic=settings.sandbox_mode)
        self.memory = LearningMemory(settings.memory_path)
        self.active_bot = TradingBot(bot_id=1, generation=1)
        self.dead_bots: list[TradingBot] = []
        self.global_stop = False
        self.paused = False
        self.event_log: list[dict] = []

    async def run(self) -> None:
        asyncio.create_task(self.feed.run())
        while True:
            if self.global_stop or self.paused:
                await asyncio.sleep(1)
                continue
            await self._step_once()
            await asyncio.sleep(1)

    async def run_sandbox_ticks(self, ticks: int) -> None:
        for symbol in settings.symbols:
            p = self.feed.bootstrap_price(symbol)
            self.feed.latest[symbol] = p
            self.feed.frames[symbol].append({"open": p, "high": p, "low": p, "close": p, "volume": 1.0})
        for _ in range(ticks):
            if self.global_stop or self.paused:
                break
            await self.feed.seed_ticks(1)
            await self._step_once()

    async def _step_once(self) -> None:
        bot = self.active_bot
        for symbol in settings.symbols:
            frame = self.feed.frame(symbol)
            if len(frame) < 30:
                continue
            price = self.feed.latest[symbol]
            tr = bot.step(symbol, frame, price)
            if tr:
                self.event_log.append(tr.model_dump(mode="json"))

            if symbol in bot.positions:
                pos = bot.positions[symbol]
                if FuturesSimulator.is_liquidated(pos, bot.balance, price):
                    liq = bot.liquidate(symbol, price)
                    self.event_log.append(liq.model_dump(mode="json"))
                    self.memory.record_liquidation(
                        {
                            "time": datetime.utcnow().isoformat(),
                            "symbol": symbol,
                            "leverage": pos.leverage,
                            "side": pos.side.value,
                        }
                    )
                    await self._handle_bot_death()
                    return
        if bot.snapshot(self.feed.latest).equity < settings.initial_balance * settings.safe_mode_equity_ratio:
            bot.status = BotStatus.WARNING

    async def _handle_bot_death(self) -> None:
        self.dead_bots.append(self.active_bot)
        if self.memory.data["liquidation_streak"] >= settings.liquidation_streak_stop:
            self.global_stop = True
            return
        gen = self.active_bot.generation + 1
        new_bot = TradingBot(bot_id=self.active_bot.bot_id + 1, generation=gen)
        bad_lev = self.memory.data.get("bad_leverages", {})
        if bad_lev:
            worst = max(bad_lev, key=bad_lev.get)
            if str(worst).isdigit():
                new_bot.risk.max_lev = max(2, min(settings.max_leverage, int(worst) - 1))
        self.active_bot = new_bot

    def current_state(self) -> dict:
        snap = self.active_bot.snapshot(self.feed.latest)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "global_stop": self.global_stop,
            "paused": self.paused,
            "memory": self.memory.data,
            "feed_connected": self.feed.connected,
            "active_bot": snap.model_dump(mode="json"),
            "dead_bots": len(self.dead_bots),
            "events": self.event_log[-200:],
        }

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def kill_bot(self) -> None:
        self.active_bot.status = BotStatus.DEAD

    def reset_learning(self) -> None:
        self.memory.clear()
        self.global_stop = False
