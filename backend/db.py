from __future__ import annotations

import aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    generation_id INTEGER NOT NULL,
    side TEXT NOT NULL,
    qty REAL NOT NULL,
    price REAL NOT NULL,
    fee REAL NOT NULL,
    pnl REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_trades_gen_ts ON trades(generation_id, ts);

CREATE TABLE IF NOT EXISTS generations (
    id INTEGER PRIMARY KEY,
    start_ts INTEGER NOT NULL,
    end_ts INTEGER,
    survival_sec REAL DEFAULT 0,
    max_equity REAL DEFAULT 0,
    liquidation_count INTEGER DEFAULT 0,
    score REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS equity_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    generation_id INTEGER NOT NULL,
    equity REAL NOT NULL,
    drawdown REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_equity_gen_ts ON equity_history(generation_id, ts);

CREATE TABLE IF NOT EXISTS liquidation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    generation_id INTEGER NOT NULL,
    mark_price REAL NOT NULL,
    equity REAL NOT NULL,
    distance REAL NOT NULL
);
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def execute(self, sql: str, params: tuple = ()):
        assert self.conn
        await self.conn.execute(sql, params)

    async def executemany(self, sql: str, params: list[tuple]):
        assert self.conn
        await self.conn.executemany(sql, params)

    async def commit(self):
        assert self.conn
        await self.conn.commit()

    async def fetchone(self, sql: str, params: tuple = ()):
        assert self.conn
        async with self.conn.execute(sql, params) as cur:
            return await cur.fetchone()
