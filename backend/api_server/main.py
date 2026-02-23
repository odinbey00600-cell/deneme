import asyncio
import time
import structlog
from fastapi import FastAPI
from sqlalchemy import text

from backend.config_manager.config_loader import get_settings
from backend.config_manager.seed_control import apply_seed
from backend.data_feed.stream_manager import StreamManager
from backend.data_feed.heartbeat_monitor import HeartbeatMonitor
from backend.data_feed.sequence_validator import SequenceValidator
from backend.market_state_engine.orderbook_state import OrderBookState
from backend.market_state_engine.candle_builder import CandleBuilder
from backend.market_state_engine.mark_price_tracker import MarkPriceTracker
from backend.market_state_engine.funding_tracker import FundingTracker
from backend.indicator_engine.ema import EMA
from backend.indicator_engine.rsi import RSI
from backend.indicator_engine.volatility import Volatility
from backend.indicator_engine.orderbook_imbalance import calculate_imbalance
from backend.execution_interface.simulated_executor import SimulatedExecutor
from backend.strategy_engine.strategy_context import StrategyContext
from backend.strategy_engine.ema_rsi_strategy import decide
from backend.risk_engine.exposure_tracker import notional
from backend.liquidation_engine.maintenance_margin_model import maintenance_margin
from backend.liquidation_engine.isolated_margin_liquidation import is_liquidated
from backend.risk_engine.drawdown_calculator import DrawdownCalculator
from backend.rl_engine.ppo_agent import PPOAgent
from backend.rl_engine.state_encoder import encode
from backend.rl_engine.reward_engine import compute_reward
from backend.rl_engine.replay_buffer import ReplayBuffer
from backend.evolution_engine.genome_model import Genome
from backend.evolution_engine.mutation_engine import mutate
from backend.evolution_engine.lineage_tracker import LineageTracker
from backend.persistence_layer.db import AsyncSessionLocal
from backend.api_server.rest_routes import build_rest_router
from backend.api_server.websocket_routes import build_ws_router
from backend.health_monitor.metrics_endpoint import build_metrics_router
from backend.health_monitor.system_watchdog import system_stats

logger = structlog.get_logger(__name__)


class AppState:
    def __init__(self):
        self.settings = get_settings()
        apply_seed(self.settings.seed)
        self.ws_heartbeat = HeartbeatMonitor(self.settings.ws_timeout_seconds)
        self.seq = SequenceValidator()
        self.orderbook = OrderBookState()
        self.candles = CandleBuilder()
        self.mark = MarkPriceTracker()
        self.funding = FundingTracker()
        self.genome = Genome()
        self.executor = SimulatedExecutor(self.settings)
        self.ema_s = EMA(self.genome.ema_short)
        self.ema_l = EMA(self.genome.ema_long)
        self.rsi = RSI(self.genome.rsi_period)
        self.vol = Volatility(30)
        self.drawdown = DrawdownCalculator()
        self.ppo = PPOAgent(self.settings.seed)
        self.buffer = ReplayBuffer(50000)
        self.stream = StreamManager(self.settings, self.on_event)
        self.lineage = LineageTracker()
        self.current_generation = 1
        self.parent_generation = None
        self.trades = []
        self.equity_history = []
        self.liquidations = 0
        self.latest = {
            'generation_id': 1, 'balance': self.settings.initial_balance, 'equity': self.settings.initial_balance,
            'position': {}, 'unrealized_pnl': 0.0, 'distance_to_liquidation': 1.0, 'time_alive': 0.0,
            'latency_ms': 0, 'ws_healthy': True, 'mark_price': 0.0, 'candles': [], 'ema_short': 0, 'ema_long': 0,
            'rsi': 50.0, 'volatility': 0.0, 'liquidations': 0, 'system': {'cpu_percent': 0, 'ram_percent': 0}
        }
        self.started_at = time.time()

    async def initialize_db(self):
        async with AsyncSessionLocal() as s:
            await s.execute(text('SELECT 1'))

    def reset_generation(self):
        self.parent_generation = self.current_generation
        self.current_generation += 1
        self.genome = mutate(self.genome)
        self.ema_s = EMA(self.genome.ema_short)
        self.ema_l = EMA(self.genome.ema_long)
        self.rsi = RSI(self.genome.rsi_period)
        self.vol = Volatility(30)
        self.executor = SimulatedExecutor(self.settings)
        self.trades.clear()
        self.equity_history.clear()
        self.started_at = time.time()
        self.lineage.add_generation(self.parent_generation, self.current_generation, 0.0)

    async def on_event(self, message: dict, recv_ts: float):
        self.ws_heartbeat.beat()
        stream = message.get('stream', '')
        data = message.get('data', {})
        if '@depth' in stream:
            uid = int(data.get('u', 0))
            self.seq.validate(uid)
            self.orderbook.apply(data)
        elif '@kline' in stream:
            c = self.candles.update(data)
            close = c['close']
            ema_short = self.ema_s.update(close)
            ema_long = self.ema_l.update(close)
            rsi = self.rsi.update(close)
            vol = self.vol.update(close)
            self.latest['candles'] = (self.latest['candles'] + [c])[-120:]
            self.latest['ema_short'] = ema_short
            self.latest['ema_long'] = ema_long
            self.latest['rsi'] = rsi
            self.latest['volatility'] = vol
            await self._maybe_trade(close, ema_short, ema_long, rsi, vol)
        elif '@markPrice' in stream:
            mark = self.mark.update(data)
            self.executor.update_mark_price(mark)
            self.latest['mark_price'] = mark
        elif '@fundingRate' in stream:
            self.funding.update(data)
        self.latest['latency_ms'] = int((time.time() - recv_ts) * 1000)
        self.latest['ws_healthy'] = self.ws_heartbeat.healthy()
        self.latest['system'] = system_stats()

    async def _maybe_trade(self, close, ema_short, ema_long, rsi, vol):
        pos = self.executor.get_position()
        direction = 1 if pos.get('side') == 'LONG' else -1 if pos.get('side') == 'SHORT' else 0
        qty = pos.get('qty', 0.0)
        entry = pos.get('entry_price', 0.0)
        unrealized = ((self.latest['mark_price'] - entry) * qty * direction) if direction != 0 else 0.0
        ntn = qty * self.latest['mark_price']
        maint = maintenance_margin(ntn, self.settings.maintenance_margin_rate)
        liq, ratio = is_liquidated(maint, self.executor.get_balance(), unrealized)
        ctx = StrategyContext(close, ema_short, ema_long, rsi, vol, calculate_imbalance(self.orderbook.bids, self.orderbook.asks), unrealized, max(0.0, 1-ratio), time.time()-pos['opened_at'] if pos.get('opened_at') else 0.0, direction)
        state = encode(ctx)
        action = decide(ctx)
        if action == 'OPEN_LONG' and direction == 0:
            margin = self.executor.get_balance() * 0.2 * self.genome.risk_aggressiveness
            order = await self.executor.place_order('BUY', notional(margin, self.settings.leverage) / max(1.0, close), vol)
            self.trades.append({'realized_pnl': 0.0, **order})
        elif action == 'OPEN_SHORT' and direction == 0:
            margin = self.executor.get_balance() * 0.2 * self.genome.risk_aggressiveness
            order = await self.executor.place_order('SELL', notional(margin, self.settings.leverage) / max(1.0, close), vol)
            self.trades.append({'realized_pnl': 0.0, **order})
        elif action == 'CLOSE_POSITION' and direction != 0:
            closed = await self.executor.close_position()
            if closed:
                self.trades.append(closed)
        balance = self.executor.get_balance()
        equity = balance + unrealized
        dd = self.drawdown.update(equity)
        reward = compute_reward(equity - self.latest['equity'], dd, len(self.trades), liq, vol, self.genome.reward_weights)
        self.buffer.add((state, action, reward))
        self.equity_history.append(equity)
        self.latest.update({
            'generation_id': self.current_generation,
            'balance': balance,
            'equity': equity,
            'position': self.executor.get_position(),
            'unrealized_pnl': unrealized,
            'distance_to_liquidation': max(0.0, 1-ratio),
            'time_alive': time.time() - self.started_at,
            'liquidations': self.liquidations
        })
        if liq:
            self.liquidations += 1
            self.reset_generation()

    async def start(self):
        self.lineage.add_generation(None, self.current_generation, self.settings.initial_balance)
        await self.initialize_db()
        await self.stream.start()

    async def stop(self):
        await self.stream.stop()

    def public_state(self):
        return self.latest

    def health_snapshot(self):
        return {'status': 'ok' if self.ws_heartbeat.healthy() else 'degraded', 'ws_healthy': self.ws_heartbeat.healthy(), 'sequence_gaps': self.seq.gaps}


app_state = AppState()
app = FastAPI(title='BTCUSDT Futures AI Simulation Lab')
app.include_router(build_rest_router(app_state))
app.include_router(build_ws_router(app_state))
app.include_router(build_metrics_router(app_state))


@app.on_event('startup')
async def startup():
    logger.info('starting_app')
    asyncio.create_task(app_state.start())


@app.on_event('shutdown')
async def shutdown():
    logger.info('stopping_app')
    await app_state.stop()
