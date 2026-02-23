# BTCUSDT Futures AI Simulation Platform

Lightweight local-first simulator with live Binance Futures streaming, 125x isolated-margin simulation, liquidation/reset generations, and a professional real-time UI.

## Stack
- Backend: FastAPI + asyncio + SQLite
- Frontend: Next.js + Zustand + TradingView Lightweight Charts
- No Docker / Redis / PostgreSQL

## Features
- Live streams: `kline_1m`, `markPrice`, `depth5`, `fundingRate`
- Auto reconnect + heartbeat + latency tracking
- 125x isolated simulation with:
  - taker fees
  - slippage
  - latency delay
  - funding impact
  - liquidation engine and reset
- Lightweight mini policy-gradient agent (CPU, NumPy)
- Generation tracking + liquidation snapshots in SQLite
- Replay mode (`replays/live_stream.jsonl`)

## Quick start (under 15 min)

### 1) Backend
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000

## API
- `GET /api/state` -> current simulation snapshot
- `GET /api/replay?path=live_stream.jsonl` -> replay events
- `WS /ws/live` -> live frontend feed

## Notes
- Binance stream requires internet access.
- For reproducibility, set `SIM_SEED` in `.env`.
- SQLite DB file: `sim.db`.
