# Institutional-Grade Self-Learning Paper Trading System (Binance USDT-M Futures)

This project is a **paper trading laboratory** with live Binance Futures data and fully simulated execution.
It never sends real orders.

## Features

- Live USDT-M futures prices via Binance WebSocket (`btcusdt`, `ethusdt`, `solusdt`, `bnbusdt`)
- Isolated margin simulation with leverage, maintenance margin, liquidation price, and forced liquidation
- Hybrid strategy stack:
  - Rule layer (EMA/VWAP/RSI/ATR + regime detection)
  - Supervised ML confidence gate
  - RL timing agent interface (hold/enter/exit)
- Institutional risk controls:
  - Max risk per trade
  - Dynamic leverage from ATR
  - Daily loss circuit
  - Consecutive-loss cooldown
  - Safe-mode warning state on equity collapse
- Bot lifecycle evolution:
  - Bot dies on liquidation
  - BotManager archives dead bots and spawns next generation
  - Persistent learning memory tracks liquidation streak and bad leverage patterns
  - Global stop after repeated liquidations
- Live UI dashboard + control actions (pause/resume/kill/reset learning)

## Production mode

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

## Sandbox mode (offline / no external services)

Set `SANDBOX_MODE=1` to disable HTTP server and network calls, then run deterministic local simulation:

```bash
SANDBOX_MODE=1 python sandbox_run.py
```

Sandbox mode guarantees:
- no FastAPI/Uvicorn startup
- no Binance websocket or external API calls
- deterministic mock market feed
- full trading engine execution (signals, risk, margin, liquidation, lifecycle)

## Docker

```bash
docker compose up --build
```

## Safety

- Simulated execution only
- No Binance API keys required
- No order placement code exists
