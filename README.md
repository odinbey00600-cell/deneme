# BTCUSDT Futures AI Simulation Platform

Production-structured research environment for evolutionary RL trading simulations using **live Binance Futures market data** and fully local simulated execution.

## Features
- Binance Futures websocket ingestion (`kline_1m`, `markPrice`, `depth5`, `fundingRate`)
- 125x isolated margin simulation with maintenance margin liquidation logic
- Taker fee, slippage, and random latency simulation (seed-controlled)
- Funding impact accounting per interval
- Continuous generation lifecycle and mutation-based evolution
- RL loop (experience buffer, epsilon decay, LR decay, gradient-style clipping via TD clipping)
- Replay controller with deterministic seed handling
- FastAPI REST + websocket gateway
- Next.js dashboard with live chart and bot/evolution/analytics/system panels
- Dockerized backend, frontend, PostgreSQL, Redis, and Nginx

## Run
1. Copy env:
```bash
cp .env.example .env
```
2. Start stack:
```bash
docker compose up --build
```
3. Open UI: `http://localhost`

## API
- `GET /health`
- `GET /metrics`
- `GET /api/generations`
- `WS /ws/live`

## Database tables
- `trades`
- `generations`
- `genome_parameters`
- `equity_history`
- `metrics`
- `liquidation_events`

