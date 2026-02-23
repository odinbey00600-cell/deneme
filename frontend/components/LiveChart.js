'use client';

import { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import { useSimStore } from '../store/useSimStore';

export default function LiveChart() {
  const ref = useRef(null);
  const chartRef = useRef(null);
  const points = useSimStore((s) => s.points);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, { width: ref.current.clientWidth, height: 420, layout: { background: { color: '#111827' }, textColor: '#cbd5e1' }, grid: { vertLines: { color: '#1f2937' }, horzLines: { color: '#1f2937' } } });
    const priceSeries = chart.addLineSeries({ color: '#22d3ee', lineWidth: 2 });
    const ema9 = chart.addLineSeries({ color: '#f59e0b', lineWidth: 1 });
    const ema21 = chart.addLineSeries({ color: '#a78bfa', lineWidth: 1 });
    chartRef.current = { chart, priceSeries, ema9, ema21 };
    return () => chart.remove();
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.priceSeries.setData(points.map((p) => ({ time: p.time, value: p.value })));
    chartRef.current.ema9.setData(points.map((p) => ({ time: p.time, value: p.ema9 })));
    chartRef.current.ema21.setData(points.map((p) => ({ time: p.time, value: p.ema21 })));
  }, [points]);

  return <div ref={ref} style={{ width: '100%', border: '1px solid #1f2937', borderRadius: 12 }} />;
}
