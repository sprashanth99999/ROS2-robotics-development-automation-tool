import { useTerminalStore } from "../../state/terminalStore";
import { TerminalPanel } from "./TerminalPanel";

export function TerminalTabs() {
  const { sessions, activeId, addSession, removeSession, setActive } = useTerminalStore();

  const newTab = () => {
    const id = crypto.randomUUID();
    addSession({ id, name: `Shell ${sessions.length + 1}`, active: true });
  };

  // Auto-create first session
  if (sessions.length === 0) {
    return (
      <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#0d1117" }}>
        <div style={{ padding: 8, borderBottom: "1px solid #21262d", display: "flex", alignItems: "center", gap: 8 }}>
          <b style={{ color: "#58a6ff", fontSize: 12 }}>Terminal</b>
          <button
            onClick={newTab}
            style={{ background: "#21262d", color: "#c9d1d9", border: "none", borderRadius: 4, padding: "2px 10px", cursor: "pointer", fontSize: 12 }}
          >
            + New
          </button>
        </div>
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#8b949e" }}>
          Click "+ New" to open a terminal
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#0d1117" }}>
      <div style={{ padding: "4px 8px", borderBottom: "1px solid #21262d", display: "flex", alignItems: "center", gap: 4, fontSize: 12 }}>
        {sessions.map((s) => (
          <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 2 }}>
            <button
              onClick={() => setActive(s.id)}
              style={{
                background: s.id === activeId ? "#161b22" : "none",
                color: s.id === activeId ? "#58a6ff" : "#8b949e",
                border: "none", borderRadius: 4, padding: "2px 8px", cursor: "pointer",
              }}
            >
              {s.name}
            </button>
            <button
              onClick={() => removeSession(s.id)}
              style={{ background: "none", border: "none", color: "#f85149", cursor: "pointer", fontSize: 10, padding: 0 }}
            >
              x
            </button>
          </div>
        ))}
        <button
          onClick={newTab}
          style={{ background: "none", border: "none", color: "#8b949e", cursor: "pointer", fontSize: 14, marginLeft: 4 }}
        >
          +
        </button>
      </div>
      {sessions
        .filter((s) => s.id === activeId)
        .map((s) => (
          <TerminalPanel key={s.id} />
        ))}
    </div>
  );
}
