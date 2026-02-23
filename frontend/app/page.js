'use client';

import { useEffect } from 'react';
import LiveChart from '../components/LiveChart';
import { useSimStore } from '../store/useSimStore';

const card = { background: '#111827', border: '1px solid #1f2937', borderRadius: 12, padding: 16 };

export default function Home() {
  const { sim, wsConnected, setSnapshot } = useSimStore();

  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/live');
    ws.onmessage = (ev) => setSnapshot(JSON.parse(ev.data));
    return () => ws.close();
  }, [setSnapshot]);

  return (
    <main style={{ padding: 20, display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
      <section style={card}>
        <h2 style={{ marginTop: 0 }}>BTCUSDT Live Chart</h2>
        <LiveChart />
      </section>
      <section style={{ display: 'grid', gap: 12 }}>
        <div style={card}>
          <h3 style={{ marginTop: 0 }}>Bot Panel</h3>
          <p>Generation: {sim?.generation ?? '-'}</p>
          <p>Balance: {sim?.balance?.toFixed(2) ?? '-'}</p>
          <p>Unrealized PnL: {sim?.unrealized_pnl?.toFixed(2) ?? '-'}</p>
          <p>Position: {sim?.position ?? '-'}</p>
          <p>Distance to Liquidation: {sim?.distance_to_liquidation?.toFixed(4) ?? '-'}</p>
          <p>Time Alive: {sim ? `${Math.floor(sim.time_alive_sec)}s` : '-'}</p>
        </div>
        <div style={card}>
          <h3 style={{ marginTop: 0 }}>Analytics</h3>
          <p>Liquidations: {sim?.liquidations ?? 0}</p>
          <p>Mark Price: {sim?.mark_price?.toFixed(2) ?? '-'}</p>
          <p>EMA9: {sim?.ema9?.toFixed(2) ?? '-'}</p>
          <p>EMA21: {sim?.ema21?.toFixed(2) ?? '-'}</p>
        </div>
        <div style={card}>
          <h3 style={{ marginTop: 0 }}>System Status</h3>
          <p>WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}</p>
          <p>Latency: {sim?.latency_ms?.toFixed(1) ?? '-'} ms</p>
          <p>Training: episode-end policy gradient</p>
        </div>
      </section>
    </main>
  );
}
