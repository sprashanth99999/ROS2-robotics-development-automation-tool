import { create } from "zustand";

export interface ChatMsg {
  id: string;
  role: "user" | "assistant";
  content: string;
  provider?: string;
  timestamp: number;
}

interface ChatState {
  messages: ChatMsg[];
  streaming: boolean;
  addMessage: (msg: ChatMsg) => void;
  appendToLast: (text: string) => void;
  setStreaming: (v: boolean) => void;
  clear: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  streaming: false,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  appendToLast: (text) =>
    set((s) => {
      const msgs = [...s.messages];
      const last = msgs[msgs.length - 1];
      if (last) msgs[msgs.length - 1] = { ...last, content: last.content + text };
      return { messages: msgs };
    }),
  setStreaming: (v) => set({ streaming: v }),
  clear: () => set({ messages: [] }),
}));
