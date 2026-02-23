'use client';
import { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

export function LiveChart({ candles, emaShort, emaLong }: { candles: any[]; emaShort: number; emaLong: number }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, { width: ref.current.clientWidth, height: 360 });
    const candleSeries = chart.addCandlestickSeries();
    const emaS = chart.addLineSeries({ color: '#4CAF50' });
    const emaL = chart.addLineSeries({ color: '#FF9800' });
    candleSeries.setData(candles.map((c) => ({ time: Math.floor(c.close_time / 1000), open: c.open, high: c.high, low: c.low, close: c.close })));
    const lastTime = candles.length ? Math.floor(candles[candles.length - 1].close_time / 1000) : Math.floor(Date.now() / 1000);
    emaS.setData([{ time: lastTime, value: emaShort || 0 }]);
    emaL.setData([{ time: lastTime, value: emaLong || 0 }]);
    return () => chart.remove();
  }, [candles, emaShort, emaLong]);

  return <div ref={ref} className="w-full border rounded" />;
}
