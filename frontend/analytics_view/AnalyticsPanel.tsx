'use client';
import { useSimStore } from '../state_store/store';

export default function AnalyticsPanel() {
  const ticks = useSimStore((s) => s.ticks);
  if (!ticks.length) return <div>No analytics yet.</div>;
  const equities = ticks.map((t) => t.equity);
  const peak = Math.max(...equities);
  const drawdown = peak - equities[equities.length - 1];
  return <div><h3>Analytics</h3><p>Peak Equity: {peak.toFixed(2)}</p><p>Drawdown: {drawdown.toFixed(2)}</p></div>;
}
