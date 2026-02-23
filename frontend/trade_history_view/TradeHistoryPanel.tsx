'use client';
import { useSimStore } from '../state_store/store';

export default function TradeHistoryPanel() {
  const ticks = useSimStore((s) => s.ticks);
  return <div><h3>Trade Stream</h3><p>Received ticks: {ticks.length}</p></div>;
}
