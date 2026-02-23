'use client';
import { useEffect } from 'react';
import { useLabStore } from '../lib/store';
import { LiveChart } from '../components/LiveChart';

export default function Home() {
  const { snapshot, setSnapshot } = useLabStore();

  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_BASE || 'ws://localhost:8000/ws/live');
    ws.onmessage = (e) => setSnapshot(JSON.parse(e.data));
    return () => ws.close();
  }, [setSnapshot]);

  if (!snapshot) return <main className="p-6">Connecting...</main>;

  return (
    <main className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-4 font-mono">
      <section className="col-span-1 lg:col-span-2">
        <h1 className="text-2xl mb-2">BTCUSDT Futures AI Simulation Lab</h1>
        <LiveChart candles={snapshot.candles || []} emaShort={snapshot.ema_short} emaLong={snapshot.ema_long} />
      </section>
      <section className="border rounded p-3">
        <h2>Bot Dashboard</h2>
        <div>Generation: {snapshot.generation_id}</div>
        <div>Balance: {snapshot.balance?.toFixed(4)}</div>
        <div>Equity: {snapshot.equity?.toFixed(4)}</div>
        <div>Position: {snapshot.position?.side || 'FLAT'}</div>
        <div>Unrealized PnL: {snapshot.unrealized_pnl?.toFixed(4)}</div>
        <div>Distance to Liq: {snapshot.distance_to_liquidation?.toFixed(6)}</div>
        <div>Time Alive: {snapshot.time_alive?.toFixed(1)}s</div>
      </section>
      <section className="border rounded p-3">
        <h2>Evolution + Analytics</h2>
        <div>Liquidations: {snapshot.liquidations}</div>
        <div>RSI: {snapshot.rsi?.toFixed(2)}</div>
        <div>Volatility: {snapshot.volatility?.toFixed(6)}</div>
        <div>Latency: {snapshot.latency_ms} ms</div>
        <div>WS Healthy: {String(snapshot.ws_healthy)}</div>
        <div>CPU/RAM: {snapshot.system?.cpu_percent}% / {snapshot.system?.ram_percent}%</div>
      </section>
    </main>
  );
}
