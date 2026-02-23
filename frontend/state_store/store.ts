'use client';

import { create } from 'zustand';

type Tick = {
  ts: string;
  mark_price: number;
  funding_rate: number;
  generation: number;
  balance: number;
  equity: number;
  liq_price: number;
  latency_ms: number;
  ws_health: boolean;
  order_book_imbalance: number;
  position: { side: string; qty: number; entry_price: number; margin: number; opened_ts: number };
};

type State = {
  ticks: Tick[];
  last?: Tick;
  replayMode: boolean;
  setReplayMode: (v: boolean) => void;
  pushTick: (t: Tick) => void;
};

export const useSimStore = create<State>((set) => ({
  ticks: [],
  replayMode: false,
  setReplayMode: (replayMode) => set({ replayMode }),
  pushTick: (tick) =>
    set((s) => ({
      last: tick,
      ticks: [...s.ticks.slice(-500), tick],
    })),
}));
