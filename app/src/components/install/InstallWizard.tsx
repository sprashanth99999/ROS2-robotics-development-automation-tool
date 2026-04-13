import { useEffect } from "react";
import { useInstallStore } from "../../state/installStore";
import { useInstallAgent } from "../../features/install/useInstallAgent";
import { InstallStepRow } from "./InstallStep";

export function InstallWizard() {
  const { steps, phase, currentStep, error } = useInstallStore();
  const { fetchPlan, runInstall } = useInstallAgent();
  const reset = useInstallStore((s) => s.reset);

  useEffect(() => {
    if (phase === "idle") fetchPlan("ubuntu22");
  }, [phase, fetchPlan]);

  const progress = steps.length > 0 ? Math.round((currentStep / steps.length) * 100) : 0;

  return (
    <div style={{ padding: 16, maxWidth: 600 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <b style={{ color: "#58a6ff", fontSize: 16 }}>ROS2 Install Wizard</b>
        <span style={{ color: "#8b949e", fontSize: 12 }}>
          {phase === "running" ? `${progress}%` : phase}
        </span>
      </div>

      {phase === "running" && (
        <div style={{ background: "#21262d", borderRadius: 4, height: 6, marginBottom: 12 }}>
          <div style={{ background: "#238636", height: "100%", borderRadius: 4, width: `${progress}%`, transition: "width 0.3s" }} />
        </div>
      )}

      {error && (
        <div style={{ color: "#f85149", background: "#1a0f0f", padding: 8, borderRadius: 6, marginBottom: 12, fontSize: 13 }}>
          {error}
        </div>
      )}

      <div>
        {steps.map((s) => (
          <InstallStepRow key={s.id} step={s} />
        ))}
      </div>

      <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
        {phase === "ready" && (
          <button
            onClick={() => runInstall("ubuntu22", "humble", true)}
            style={{ background: "#238636", color: "#fff", border: "none", borderRadius: 6, padding: "8px 20px", cursor: "pointer", fontWeight: 600 }}
          >
            Dry Run
          </button>
        )}
        {phase === "ready" && (
          <button
            onClick={() => runInstall("ubuntu22", "humble", false)}
            style={{ background: "#da3633", color: "#fff", border: "none", borderRadius: 6, padding: "8px 20px", cursor: "pointer", fontWeight: 600 }}
          >
            Install (sudo)
          </button>
        )}
        {(phase === "done" || phase === "error") && (
          <button
            onClick={reset}
            style={{ background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d", borderRadius: 6, padding: "8px 20px", cursor: "pointer" }}
          >
            Reset
          </button>
        )}
      </div>
    </div>
  );
}
