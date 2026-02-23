#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os

os.environ["SANDBOX_MODE"] = "1"

from app.bot.manager import BotManager


async def main() -> None:
    manager = BotManager()
    ticks = 120
    print("[sandbox] starting deterministic offline simulation")
    await manager.run_sandbox_ticks(ticks)

    state = manager.current_state()
    bot = state["active_bot"]

    print(f"[sandbox] finished ticks={ticks}")
    print(f"[sandbox] bot_id={bot['bot_id']} generation={bot['generation']} status={bot['status']}")
    print(f"[sandbox] equity={bot['equity']:.4f} balance={bot['balance']:.4f} upnl={bot['unrealized_pnl']:.4f}")
    print(f"[sandbox] drawdown={bot['drawdown']:.4f} dead_bots={state['dead_bots']} global_stop={state['global_stop']}")

    print("[sandbox] recent decisions:")
    for event in state["events"][-15:]:
        print(
            f"  - {event['action']} {event.get('symbol','')} side={event.get('side')} "
            f"qty={event.get('qty',0):.6f} price={event.get('price',0):.4f} "
            f"pnl={event.get('pnl',0):.4f} reason={event.get('reason','')}"
        )

    print("[sandbox] liquidation memory:", state["memory"]) 


if __name__ == "__main__":
    asyncio.run(main())
