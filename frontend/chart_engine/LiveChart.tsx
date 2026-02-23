'use client';

import { useEffect, useRef } from 'react';
import { ColorType, createChart } from 'lightweight-charts';
import { useSimStore } from '../state_store/store';

export default function LiveChart() {
  const ref = useRef<HTMLDivElement>(null);
  const ticks = useSimStore((s) => s.ticks);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, {
      width: 900,
      height: 300,
      layout: { background: { type: ColorType.Solid, color: '#111' }, textColor: '#DDD' },
      grid: { vertLines: { color: '#222' }, horzLines: { color: '#222' } },
    });
    const series = chart.addLineSeries({ color: '#f7931a' });
    const liqSeries = chart.addLineSeries({ color: '#ff4d4f' });
    ticks.forEach((t) => {
      const ts = Math.floor(new Date(t.ts).getTime() / 1000);
      series.update({ time: ts as never, value: t.mark_price });
      if (t.liq_price > 0) liqSeries.update({ time: ts as never, value: t.liq_price });
    });
    return () => chart.remove();
  }, [ticks]);

  return <div ref={ref} />;
}
