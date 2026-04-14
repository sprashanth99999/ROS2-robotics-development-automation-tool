import { useEffect, useState } from "react";

const BACKEND = "http://127.0.0.1:8765";

interface SimStatus {
  connected: boolean;
  simulator: string;
  world: string;
  paused: boolean;
  entities: string[];
}

export function GazeboPanel() {
  const [status, setStatus] = useState<SimStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const r = await fetch(`${BACKEND}/sim/status`);
      setStatus(await r.json());
    } catch {
      setStatus(null);
    }
  };

  useEffect(() => {
    fetchStatus();
    const iv = setInterval(fetchStatus, 5000);
    return () => clearInterval(iv);
  }, []);

  const action = async (endpoint: string, body?: object) => {
    setLoading(true);
    try {
      await fetch(`${BACKEND}/sim/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      await fetchStatus();
    } catch {}
    setLoading(false);
  };

  const btn = (label: string, onClick: () => void, color = "#21262d") => (
    <button
      onClick={onClick}
      disabled={loading}
      style={{
        background: color, color: "#fff", border: "1px solid #30363d",
        borderRadius: 6, padding: "6px 14px", cursor: loading ? "not-allowed" : "pointer",
        fontSize: 12, fontWeight: 600,
      }}
    >
      {label}
    </button>
  );

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <b style={{ color: "#58a6ff", fontSize: 16 }}>Gazebo Simulator</b>
        <span style={{
          color: status?.connected ? "#3fb950" : "#f85149",
          fontSize: 12, fontWeight: 600,
        }}>
          {status?.connected ? `Connected — ${status.world}` : "Disconnected"}
        </span>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        {btn("Connect", () => action("connect"), "#238636")}
        {btn("Launch Empty", () => action("launch", { world_file: "" }))}
        {btn("Pause", () => action("pause"))}
        {btn("Resume", () => action("resume"))}
        {btn("Reset", () => action("reset"), "#da3633")}
        {btn("Disconnect", () => action("disconnect"))}
      </div>

      {status?.entities && status.entities.length > 0 && (
        <div>
          <b style={{ color: "#8b949e", fontSize: 12 }}>Topics ({status.entities.length})</b>
          <div style={{ maxHeight: 200, overflow: "auto", marginTop: 4 }}>
            {status.entities.map((e, i) => (
              <div key={i} style={{ color: "#c9d1d9", fontSize: 11, padding: "2px 0", fontFamily: "monospace" }}>
                {e}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
