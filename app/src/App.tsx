import { useEffect, useState } from "react";
import { ChatPanel } from "./components/chat/ChatPanel";
import { InstallWizard } from "./components/install/InstallWizard";
import { TerminalTabs } from "./components/terminal/TerminalTabs";
import { NodeGraph } from "./components/nodegraph/NodeGraph";
import { TopicMonitor } from "./components/topics/TopicMonitor";
import { UrdfViewer } from "./components/viewer/UrdfViewer";
import { ViewerToolbar } from "./components/viewer/ViewerToolbar";

type Health = { status: string; version: string } | null;
type Tab = "chat" | "install" | "terminal" | "graph" | "topics" | "viewer";

const tabStyle = (active: boolean) => ({
  background: "none", border: "none", color: active ? "#58a6ff" : "#8b949e",
  cursor: "pointer", padding: "4px 8px", fontSize: 12, fontWeight: active ? 700 : 400,
  borderBottom: active ? "2px solid #58a6ff" : "2px solid transparent",
});

export function App() {
  const [health, setHealth] = useState<Health>(null);
  const [tab, setTab] = useState<Tab>("chat");

  useEffect(() => {
    fetch("http://127.0.0.1:8765/health").then(r => r.json()).then(setHealth).catch(() => {});
  }, []);

  return (
    <div style={{ fontFamily: "monospace", background: "#0d1117", color: "#c9d1d9", height: "100vh", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "6px 16px", borderBottom: "1px solid #21262d", display: "flex", alignItems: "center", gap: 12, fontSize: 12 }}>
        <b style={{ color: "#58a6ff" }}>RoboForge AI</b>
        {health ? <span style={{ color: "#3fb950" }}>backend: ok</span> : <span style={{ color: "#8b949e" }}>connecting...</span>}
        <div style={{ marginLeft: "auto", display: "flex", gap: 4 }}>
          <button style={tabStyle(tab === "chat")} onClick={() => setTab("chat")}>Chat</button>
          <button style={tabStyle(tab === "install")} onClick={() => setTab("install")}>Install</button>
          <button style={tabStyle(tab === "terminal")} onClick={() => setTab("terminal")}>Terminal</button>
          <button style={tabStyle(tab === "graph")} onClick={() => setTab("graph")}>Graph</button>
          <button style={tabStyle(tab === "topics")} onClick={() => setTab("topics")}>Topics</button>
          <button style={tabStyle(tab === "viewer")} onClick={() => setTab("viewer")}>3D</button>
        </div>
      </div>
      {tab === "chat" && <ChatPanel />}
      {tab === "install" && <div style={{ flex: 1, overflow: "auto" }}><InstallWizard /></div>}
      {tab === "terminal" && <TerminalTabs />}
      {tab === "graph" && <div style={{ flex: 1 }}><NodeGraph /></div>}
      {tab === "topics" && <div style={{ flex: 1, overflow: "auto" }}><TopicMonitor /></div>}
      {tab === "viewer" && <div style={{ flex: 1, display: "flex", flexDirection: "column" }}><ViewerToolbar /><UrdfViewer /></div>}
    </div>
  );
}
