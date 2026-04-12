import { useEffect, useState } from "react";
import { ChatPanel } from "./components/chat/ChatPanel";

type Health = { status: string; version: string } | null;

export function App() {
  const [health, setHealth] = useState<Health>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8765/health").then(r => r.json()).then(setHealth).catch(() => {});
  }, []);

  return (
    <div style={{ fontFamily: "monospace", background: "#0d1117", color: "#c9d1d9", height: "100vh", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "6px 16px", borderBottom: "1px solid #21262d", display: "flex", alignItems: "center", gap: 12, fontSize: 12 }}>
        <b style={{ color: "#58a6ff" }}>RoboForge AI</b>
        {health ? <span style={{ color: "#3fb950" }}>backend: ok</span> : <span style={{ color: "#8b949e" }}>connecting...</span>}
      </div>
      <ChatPanel />
    </div>
  );
}
