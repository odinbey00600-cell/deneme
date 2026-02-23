from __future__ import annotations

import asyncio
import time
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, generate_latest
from starlette.responses import PlainTextResponse

from analytics_engine.reward import reward_function
from config_manager.settings import settings
from data_feed.binance_ws import BinanceDataFeed
from evolution_engine.evolution import EvolutionEngine
from indicator_engine.indicators import ema, rsi, volatility
from market_state_engine.state import MarketState
from persistence_layer.db import Base, engine
from persistence_layer.repository import Repository
from rl_engine.agent import ACTIONS, Experience, RLAgent
from simulated_execution_engine.sim_engine import SimulatedExecutionEngine
from strategy_engine.baseline import baseline_signal

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['*'], allow_methods=['*'])

connections: set[WebSocket] = set()
market_state = MarketState()
repo = Repository()
evolution = EvolutionEngine(settings.seed)
agent = RLAgent(settings.seed)
feed = BinanceDataFeed(market_state)

SIM_TICK = Counter('sim_ticks_total', 'Simulation ticks')
WS_CONNECTIONS = Gauge('ws_connections', 'Active ws clients')

runtime = {
    'generation_number': 1,
    'genome': evolution.initial_genome(),
    'generation_id': None,
    'spawn_time': time.time(),
    'equity_peak': settings.initial_balance,
    'liquidations': 0,
    'trade_ids': {},
}

engine_sim = SimulatedExecutionEngine(
    initial_balance=settings.initial_balance,
    leverage=settings.leverage,
    taker_fee=settings.taker_fee,
    maintenance_margin_rate=settings.maintenance_margin_rate,
    min_latency_ms=settings.min_latency_ms,
    max_latency_ms=settings.max_latency_ms,
    slippage_bps_mean=settings.slippage_bps_mean,
    slippage_bps_std=settings.slippage_bps_std,
    seed=settings.seed,
)


def current_state_vector(liq_price: float) -> list[float]:
    closes = [c.close for c in market_state.candles]
    pos = engine_sim.get_position()
    mark = market_state.mark_price or (closes[-1] if closes else 0.0)
    dist_to_liq = 0.0 if liq_price == 0 else abs(mark - liq_price) / max(mark, 1e-9)
    upnl = engine_sim.get_equity() - engine_sim.get_balance() - pos.margin
    return [
        mark,
        ema(closes, runtime['genome']['ema_short']),
        ema(closes, runtime['genome']['ema_long']),
        rsi(closes),
        volatility(closes),
        dist_to_liq,
        upnl,
        1.0 if pos.side == 'LONG' else -1.0 if pos.side == 'SHORT' else 0.0,
        time.time() - pos.opened_ts if pos.opened_ts else 0.0,
        market_state.order_book_imbalance,
    ]


async def broadcast(payload: dict) -> None:
    dead = []
    for ws in connections:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.discard(ws)
    WS_CONNECTIONS.set(len(connections))


async def spawn_generation(parent_id: int | None = None) -> None:
    generation = repo.create_generation(runtime['generation_number'], runtime['genome'], settings.initial_balance, parent_id)
    runtime['generation_id'] = generation.id
    runtime['spawn_time'] = time.time()
    runtime['equity_peak'] = settings.initial_balance


async def simulation_loop() -> None:
    await spawn_generation(None)
    last_funding = time.time()
    while True:
        await asyncio.sleep(settings.decision_interval_seconds)
        SIM_TICK.inc()
        if not market_state.candles or market_state.mark_price == 0:
            continue

        mark = market_state.mark_price
        engine_sim.update_mark_price(mark)
        liq, liq_price = engine_sim.liquidation_check()
        state = current_state_vector(liq_price)
        signal = baseline_signal(mark, state[1], state[2], state[3], state[4], engine_sim.get_position().side != 'FLAT')
        action = agent.act(state)
        chosen = action if action != 'HOLD' else signal

        trade_frequency = repo.trade_count(runtime['generation_id']) / max(1, (time.time() - runtime['spawn_time']) / 60)
        drawdown = max(0.0, runtime['equity_peak'] - engine_sim.get_equity())

        if chosen in {'OPEN_LONG', 'OPEN_SHORT'}:
            result = await engine_sim.place_order(chosen.split('_')[1], engine_sim.get_balance() * 0.95, mark)
            if result.get('status') == 'filled':
                t = repo.add_trade(
                    generation_id=runtime['generation_id'],
                    side=chosen.split('_')[1],
                    qty=result['qty'],
                    entry_price=result['price'],
                    fee_paid=result['fee'],
                    slippage=result['slippage'],
                )
                runtime['trade_ids']['open'] = t.id
        elif chosen == 'CLOSE_POSITION':
            result = await engine_sim.close_position(mark)
            if result.get('status') == 'filled' and 'open' in runtime['trade_ids']:
                repo.update_trade(runtime['trade_ids']['open'], exit_price=result['price'], pnl=result['pnl'], fee_paid=result['fee'], closed_at=datetime.utcnow())

        if time.time() - last_funding >= settings.funding_interval_hours * 3600:
            payment = engine_sim.funding_payment(market_state.funding_rate)
            repo.add_metric(runtime['generation_id'], 'funding_payment', payment)
            last_funding = time.time()

        liquidation_penalty = liq
        reward = reward_function(
            delta_equity=engine_sim.get_equity() - settings.initial_balance,
            drawdown=drawdown,
            trade_frequency=trade_frequency,
            liquidation=liquidation_penalty,
            volatility_risk=state[4],
            weights=runtime['genome']['reward_weights'],
        )
        next_state = current_state_vector(liq_price)
        agent.store(Experience(state=state, action=ACTIONS.index(action), reward=reward, next_state=next_state, done=liq))
        agent.train_step()

        runtime['equity_peak'] = max(runtime['equity_peak'], engine_sim.get_equity())
        repo.add_equity_point(runtime['generation_id'], engine_sim.get_balance(), engine_sim.get_equity(), next_state[6], drawdown)

        if liq:
            runtime['liquidations'] += 1
            repo.add_liquidation(runtime['generation_id'], mark, liq_price, 'mark_price_cross')
            survival = time.time() - runtime['spawn_time']
            repo.close_generation(runtime['generation_id'], 0.0, survival, runtime['equity_peak'], runtime['liquidations'])
            runtime['genome'] = evolution.mutate(runtime['genome'], reward)
            runtime['generation_number'] += 1
            await broadcast({'type': 'liquidation', 'generation': runtime['generation_number'] - 1, 'liq_price': liq_price})
            globals()['engine_sim'] = SimulatedExecutionEngine(
                initial_balance=settings.initial_balance,
                leverage=settings.leverage,
                taker_fee=settings.taker_fee,
                maintenance_margin_rate=settings.maintenance_margin_rate,
                min_latency_ms=settings.min_latency_ms,
                max_latency_ms=settings.max_latency_ms,
                slippage_bps_mean=settings.slippage_bps_mean,
                slippage_bps_std=settings.slippage_bps_std,
                seed=settings.seed + runtime['generation_number'],
            )
            await spawn_generation(runtime['generation_id'])

        await broadcast(
            {
                'type': 'tick',
                'ts': datetime.utcnow().isoformat(),
                'mark_price': mark,
                'funding_rate': market_state.funding_rate,
                'generation': runtime['generation_number'],
                'balance': engine_sim.get_balance(),
                'equity': engine_sim.get_equity(),
                'position': engine_sim.get_position().__dict__,
                'liq_price': liq_price,
                'ws_health': market_state.ws_healthy and feed.heartbeat_ok(),
                'latency_ms': market_state.last_update_latency_ms,
                'order_book_imbalance': market_state.order_book_imbalance,
            }
        )


@app.on_event('startup')
async def startup() -> None:
    asyncio.create_task(feed.run())
    asyncio.create_task(simulation_loop())


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'ws': market_state.ws_healthy and feed.heartbeat_ok()}


@app.get('/metrics')
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode('utf-8'))


@app.get('/api/generations')
def generations() -> list[dict]:
    return repo.generation_summary()


@app.websocket('/ws/live')
async def ws_live(websocket: WebSocket) -> None:
    await websocket.accept()
    connections.add(websocket)
    WS_CONNECTIONS.set(len(connections))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.discard(websocket)
        WS_CONNECTIONS.set(len(connections))
