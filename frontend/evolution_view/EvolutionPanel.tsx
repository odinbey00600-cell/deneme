'use client';
import { useEffect, useState } from 'react';

export default function EvolutionPanel() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    fetch('/api/proxy/generations').then((r) => r.json()).then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <div>
      <h3>Evolution Panel</h3>
      <ul>
        {rows.slice(0, 10).map((r, i) => <li key={i}>Gen {r.generation_number} | survival {r.survival_seconds?.toFixed?.(1)}s | peak {r.equity_peak?.toFixed?.(2)}</li>)}
      </ul>
    </div>
  );
}
