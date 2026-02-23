import { create } from 'zustand';

type LabState = {
  snapshot: any;
  setSnapshot: (s: any) => void;
};

export const useLabStore = create<LabState>((set) => ({
  snapshot: null,
  setSnapshot: (snapshot) => set({ snapshot }),
}));
