import { useEffect, useState } from "react";

type Health = { status: string; version: string; ros2_distro: string; ai_default_provider: string } | null;

export function App() {
  const [health, setHealth] = useState<Health>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    const port = new URLSearchParams(window.location.search).get("port") || "8765";
    fetch(`http://127.0.0.1:${port}/health`)
      .then(r => r.json())
      .then(setHealth)
      .catch(e => setErr(e.message));
  }, []);

  return (
    <div style={{ fontFamily: "monospace", padding: 32, background: "#0d1117", color: "#c9d1d9", minHeight: "100vh" }}>
      <h1 style={{ color: "#58a6ff" }}>RoboForge AI</h1>
      {err && <p style={{ color: "#f85149" }}>Backend: {err}</p>}
      {health && (
        <div style={{ background: "#161b22", padding: 16, borderRadius: 8, marginTop: 16 }}>
          <p>Status: <b style={{ color: "#3fb950" }}>{health.status}</b></p>
          <p>Version: {health.version}</p>
          <p>ROS2: {health.ros2_distro}</p>
          <p>AI Provider: {health.ai_default_provider}</p>
        </div>
      )}
      {!health && !err && <p>Connecting to backend...</p>}
    </div>
  );
}
