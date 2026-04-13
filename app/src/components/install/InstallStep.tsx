import type { InstallStep as Step } from "../../state/installStore";

const STATUS_COLORS: Record<string, string> = {
  pending: "#8b949e",
  running: "#58a6ff",
  done: "#3fb950",
  failed: "#f85149",
  skipped: "#8b949e",
};

const STATUS_ICONS: Record<string, string> = {
  pending: "○",
  running: "◉",
  done: "✓",
  failed: "✗",
  skipped: "—",
};

export function InstallStepRow({ step }: { step: Step }) {
  return (
    <div style={{ padding: "8px 0", borderBottom: "1px solid #21262d" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ color: STATUS_COLORS[step.status], fontWeight: 700, width: 16 }}>
          {STATUS_ICONS[step.status]}
        </span>
        <span style={{ color: "#c9d1d9", fontWeight: 600, fontSize: 13 }}>{step.name}</span>
        <span style={{ color: "#8b949e", fontSize: 11, marginLeft: "auto" }}>{step.status}</span>
      </div>
      <div style={{ color: "#8b949e", fontSize: 11, marginTop: 4, paddingLeft: 24 }}>
        {step.description}
      </div>
      {step.output && (
        <pre style={{ color: "#7ee787", fontSize: 10, background: "#0d1117", padding: 6, margin: "4px 0 0 24px", borderRadius: 4, maxHeight: 80, overflow: "auto" }}>
          {step.output}
        </pre>
      )}
      {step.error && (
        <div style={{ color: "#f85149", fontSize: 11, paddingLeft: 24, marginTop: 2 }}>
          Error: {step.error}
        </div>
      )}
    </div>
  );
}
