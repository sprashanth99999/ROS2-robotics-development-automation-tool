import { create } from "zustand";

interface ProviderInfo { name: string; has_key: boolean }

interface ProviderState {
  providers: ProviderInfo[];
  active: string;
  setActive: (name: string) => void;
  setProviders: (list: ProviderInfo[]) => void;
}

export const useProviderStore = create<ProviderState>((set) => ({
  providers: [],
  active: "claude",
  setActive: (name) => set({ active: name }),
  setProviders: (list) => set({ providers: list }),
}));
