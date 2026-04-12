import { useEffect, useRef } from "react";
import { useChatStore } from "../../state/chatStore";

export function MessageList() {
  const messages = useChatStore((s) => s.messages);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  return (
    <div style={{ flex: 1, overflow: "auto", padding: 16 }}>
      {messages.map((m) => (
        <div key={m.id} style={{ marginBottom: 12 }}>
          <span style={{ color: m.role === "user" ? "#d2a8ff" : "#3fb950", fontWeight: 600, fontSize: 12 }}>
            {m.role === "user" ? "You" : m.provider || "AI"}
          </span>
          <div style={{ color: "#c9d1d9", whiteSpace: "pre-wrap", marginTop: 4, lineHeight: 1.5 }}>
            {m.content || "..."}
          </div>
        </div>
      ))}
      <div ref={bottom} />
    </div>
  );
}
