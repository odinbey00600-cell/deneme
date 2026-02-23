# BTCUSDT Futures AI Simulation Laboratory (Native Runtime)

## Stack
- Backend: Python 3.11 + FastAPI
- DB: PostgreSQL (native install)
- Cache/stream control: Redis (native install)
- Frontend: Next.js + Zustand + Lightweight Charts
- No Docker, all processes run directly.

## Folder Layout
- `backend/` full modular trading simulation and RL/evolution engine.
- `frontend/` live dashboard and charting UI.
- `scripts/` native startup/health scripts.

## Setup
1. Install PostgreSQL and create DB `btc_lab`.
2. Install Redis and start service on default `6379`.
3. Backend:
   - `cp backend/.env.example backend/.env`
   - adjust credentials.
   - `bash scripts/start_backend.sh`
4. Frontend:
   - `cp frontend/.env.local.example frontend/.env.local`
   - `bash scripts/start_frontend.sh`

## Startup order
1. PostgreSQL
2. Redis
3. FastAPI backend
4. Next.js frontend

## Health checks
- REST: `GET /api/health`
- Runtime metrics: `GET /metrics`
- Status payload: `GET /api/status`
- Live stream: `ws://localhost:8000/ws/live`

## Replay and seed control
- Seed is controlled by `SEED` env var and applied across numpy/python/torch in `backend/config_manager/seed_control.py`.
- Deterministic replays can be built by replaying archived event streams while using same seed.

## Production notes
- Executor abstraction isolates simulated/live execution switch.
- Binance live executor exists as explicit stub and can be swapped when enabling real trading.
- Evolution engine mutates genome on liquidation and tracks lineage graph.
