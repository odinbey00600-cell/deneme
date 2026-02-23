'use client';
import { useSimStore } from '../state_store/store';

export default function SystemStatusPanel() {
  const last = useSimStore((s) => s.last);
  return (
    <div>
      <h3>System Status</h3>
      <p>WS Health: {last?.ws_health ? 'Healthy' : 'Degraded'}</p>
      <p>Feed Latency: {last?.latency_ms?.toFixed?.(2) ?? '0'} ms</p>
    </div>
  );
}
