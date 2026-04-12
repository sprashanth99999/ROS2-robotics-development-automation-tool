import { useState } from "react";
import { useChatStore } from "../../state/chatStore";
import { useChatStream } from "../../features/chat/useChatStream";
import { MessageList } from "./MessageList";
import { Composer } from "./Composer";
import { ProviderSwitcher } from "./ProviderSwitcher";

export function ChatPanel() {
  const { send } = useChatStream();
  const streaming = useChatStore((s) => s.streaming);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#0d1117" }}>
      <div style={{ padding: "8px 16px", borderBottom: "1px solid #21262d", display: "flex", alignItems: "center", gap: 12 }}>
        <b style={{ color: "#58a6ff" }}>AI Chat</b>
        <ProviderSwitcher />
      </div>
      <MessageList />
      <Composer onSend={send} disabled={streaming} />
    </div>
  );
}
