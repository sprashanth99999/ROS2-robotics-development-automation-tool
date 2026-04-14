import { useEffect, useState } from "react";
import { SignIn } from "./components/auth/SignIn";
import { ChatPanel } from "./components/chat/ChatPanel";
import { InstallWizard } from "./components/install/InstallWizard";
import { TerminalTabs } from "./components/terminal/TerminalTabs";
import { NodeGraph } from "./components/nodegraph/NodeGraph";
import { TopicMonitor } from "./components/topics/TopicMonitor";
import { UrdfViewer } from "./components/viewer/UrdfViewer";
import { ViewerToolbar } from "./components/viewer/ViewerToolbar";
import { GazeboPanel } from "./components/gazebo/GazeboPanel";
import { SettingsPanel } from "./components/settings/SettingsPanel";

type Health = { status: string; version: string } | null;
type Tab = "chat" | "install" | "terminal" | "graph" | "topics" | "viewer" | "sim" | "settings";

const tabStyle = (active: boolean) => ({
  background: "none", border: "none", color: active ? "#58a6ff" : "#8b949e",
  cursor: "pointer", padding: "4px 8px", fontSize: 12, fontWeight: active ? 700 : 400,
  borderBottom: active ? "2px solid #58a6ff" : "2px solid transparent",
});

type User = { email: string; name: string; picture: string } | null;

export function App() {
  const [health, setHealth] = useState<Health>(null);
  const [tab, setTab] = useState<Tab>("chat");
  const [user, setUser] = useState<User>(null);
  const [checking, setChecking] = useState(true);

  const checkAuth = () => {
    fetch("http://127.0.0.1:8765/auth/me").then(r => r.ok ? r.json() : null).then((u) => {
      setUser(u); setChecking(false);
    }).catch(() => setChecking(false));
  };

  useEffect(() => {
    fetch("http://127.0.0.1:8765/health").then(r => r.json()).then(setHealth).catch(() => {});
    checkAuth();
  }, []);

  const logout = async () => {
    await fetch("http://127.0.0.1:8765/auth/logout", { method: "POST" });
    setUser(null);
  };

  if (checking) return <div style={{ height: "100vh", background: "#0d1117", color: "#8b949e", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", fontSize: 12 }}>Loading...</div>;
  if (!user) return <SignIn onSignedIn={checkAuth} />;

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
          <button style={tabStyle(tab === "sim")} onClick={() => setTab("sim")}>Sim</button>
          <button style={tabStyle(tab === "settings")} onClick={() => setTab("settings")}>Settings</button>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginLeft: 12, paddingLeft: 12, borderLeft: "1px solid #30363d" }}>
            {user.picture && <img src={user.picture} alt="" style={{ width: 18, height: 18, borderRadius: 9 }} />}
            <span style={{ color: "#c9d1d9", fontSize: 11 }}>{user.email}</span>
            <button onClick={logout} style={{ background: "none", border: "1px solid #30363d", color: "#8b949e", cursor: "pointer", padding: "2px 8px", fontSize: 10, borderRadius: 3 }}>Sign out</button>
          </div>
        </div>
      </div>
      {tab === "chat" && <ChatPanel />}
      {tab === "install" && <div style={{ flex: 1, overflow: "auto" }}><InstallWizard /></div>}
      {tab === "terminal" && <TerminalTabs />}
      {tab === "graph" && <div style={{ flex: 1 }}><NodeGraph /></div>}
      {tab === "topics" && <div style={{ flex: 1, overflow: "auto" }}><TopicMonitor /></div>}
      {tab === "viewer" && <div style={{ flex: 1, display: "flex", flexDirection: "column" }}><ViewerToolbar /><UrdfViewer /></div>}
      {tab === "sim" && <div style={{ flex: 1, overflow: "auto" }}><GazeboPanel /></div>}
      {tab === "settings" && <div style={{ flex: 1, overflow: "auto" }}><SettingsPanel /></div>}
    </div>
  );
}
