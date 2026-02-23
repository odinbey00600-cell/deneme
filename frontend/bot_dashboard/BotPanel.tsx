'use client';
import { useSimStore } from '../state_store/store';

export default function BotPanel() {
  const last = useSimStore((s) => s.last);
  if (!last) return <div>Waiting for market stream…</div>;
  return (
    <div>
      <h3>Bot Panel</h3>
      <p>Generation: {last.generation}</p>
      <p>Balance: {last.balance.toFixed(2)} USDT</p>
      <p>Equity: {last.equity.toFixed(2)} USDT</p>
      <p>Position: {last.position.side}</p>
      <p>Unrealized PnL: {(last.equity - last.balance).toFixed(2)}</p>
      <p>Distance to Liq: {last.liq_price > 0 ? (((last.mark_price - last.liq_price) / last.mark_price) * 100).toFixed(2) : '0'}%</p>
    </div>
  );
}
