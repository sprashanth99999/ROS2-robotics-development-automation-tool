import { create } from "zustand";

export interface TermSession {
  id: string;
  name: string;
  active: boolean;
}

interface TerminalState {
  sessions: TermSession[];
  activeId: string | null;
  addSession: (s: TermSession) => void;
  removeSession: (id: string) => void;
  setActive: (id: string) => void;
}

export const useTerminalStore = create<TerminalState>((set) => ({
  sessions: [],
  activeId: null,
  addSession: (s) =>
    set((st) => ({
      sessions: [...st.sessions, s],
      activeId: s.id,
    })),
  removeSession: (id) =>
    set((st) => {
      const sessions = st.sessions.filter((s) => s.id !== id);
      return { sessions, activeId: sessions[0]?.id || null };
    }),
  setActive: (id) => set({ activeId: id }),
}));
