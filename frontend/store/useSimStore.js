import { create } from 'zustand';

export const useSimStore = create((set) => ({
  sim: null,
  wsConnected: false,
  points: [],
  setSnapshot: (payload) => set((state) => ({
    sim: payload.sim,
    wsConnected: payload.ws_connected,
    points: [...state.points.slice(-600), { time: Math.floor(Date.now() / 1000), value: payload.sim.mark_price || 0, ema9: payload.sim.ema9 || 0, ema21: payload.sim.ema21 || 0 }]
  }))
}));
