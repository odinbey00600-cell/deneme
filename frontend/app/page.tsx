'use client';

import { useEffect } from 'react';
import LiveChart from '../chart_engine/LiveChart';
import BotPanel from '../bot_dashboard/BotPanel';
import EvolutionPanel from '../evolution_view/EvolutionPanel';
import AnalyticsPanel from '../analytics_view/AnalyticsPanel';
import TradeHistoryPanel from '../trade_history_view/TradeHistoryPanel';
import SystemStatusPanel from '../system_status_view/SystemStatusPanel';
import ControlPanel from '../control_panel/ControlPanel';
import { useSimStore } from '../state_store/store';

export default function HomePage() {
  const pushTick = useSimStore((s) => s.pushTick);
  useEffect(() => {
    const ws = new WebSocket((process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/live'));
    ws.onopen = () => ws.send('subscribe');
    ws.onmessage = (m) => {
      const d = JSON.parse(m.data);
      if (d.type === 'tick') pushTick(d);
    };
    return () => ws.close();
  }, [pushTick]);

  return (
    <main>
      <h1>BTCUSDT Futures AI Simulation Lab</h1>
      <LiveChart />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
        <BotPanel />
        <SystemStatusPanel />
        <ControlPanel />
        <EvolutionPanel />
        <AnalyticsPanel />
        <TradeHistoryPanel />
      </div>
    </main>
  );
}
