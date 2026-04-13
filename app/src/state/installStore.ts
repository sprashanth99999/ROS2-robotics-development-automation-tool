import { create } from "zustand";

export interface InstallStep {
  id: string;
  name: string;
  command: string;
  description: string;
  sudo: boolean;
  status: "pending" | "running" | "done" | "failed" | "skipped";
  output?: string;
  error?: string;
}

interface InstallState {
  steps: InstallStep[];
  phase: "idle" | "planning" | "ready" | "running" | "done" | "error";
  distro: string;
  currentStep: number;
  error: string | null;
  setSteps: (steps: InstallStep[]) => void;
  setPhase: (p: InstallState["phase"]) => void;
  updateStep: (id: string, patch: Partial<InstallStep>) => void;
  setCurrentStep: (n: number) => void;
  setError: (e: string | null) => void;
  reset: () => void;
}

export const useInstallStore = create<InstallState>((set) => ({
  steps: [],
  phase: "idle",
  distro: "humble",
  currentStep: 0,
  error: null,
  setSteps: (steps) => set({ steps }),
  setPhase: (phase) => set({ phase }),
  updateStep: (id, patch) =>
    set((s) => ({
      steps: s.steps.map((st) => (st.id === id ? { ...st, ...patch } : st)),
    })),
  setCurrentStep: (n) => set({ currentStep: n }),
  setError: (error) => set({ error }),
  reset: () => set({ steps: [], phase: "idle", currentStep: 0, error: null }),
}));
