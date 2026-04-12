import { useCallback } from "react";
import { useChatStore, ChatMsg } from "../../state/chatStore";
import { useProviderStore } from "../../state/providerStore";

const BACKEND = "http://127.0.0.1:8765";

function uid() { return crypto.randomUUID(); }

export function useChatStream() {
  const { addMessage, appendToLast, setStreaming } = useChatStore();
  const active = useProviderStore((s) => s.active);
  const messages = useChatStore((s) => s.messages);

  const send = useCallback(async (text: string) => {
    const userMsg: ChatMsg = { id: uid(), role: "user", content: text, provider: active, timestamp: Date.now() };
    addMessage(userMsg);

    const assistantMsg: ChatMsg = { id: uid(), role: "assistant", content: "", provider: active, timestamp: Date.now() };
    addMessage(assistantMsg);
    setStreaming(true);

    try {
      const body = {
        provider: active,
        messages: [...messages, userMsg].map((m) => ({ role: m.role, content: m.content })),
      };
      const resp = await fetch(`${BACKEND}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const reader = resp.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
          try {
            const { text: t } = JSON.parse(line.slice(6));
            if (t) appendToLast(t);
          } catch {}
        }
      }
    } catch (e) {
      appendToLast(`\n[Error: ${e}]`);
    } finally {
      setStreaming(false);
    }
  }, [active, messages, addMessage, appendToLast, setStreaming]);

  return { send };
}
