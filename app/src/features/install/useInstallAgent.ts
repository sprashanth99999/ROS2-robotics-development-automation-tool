import { useCallback } from "react";
import { useInstallStore } from "../../state/installStore";

const BACKEND = "http://127.0.0.1:8765";

export function useInstallAgent() {
  const { setSteps, setPhase, updateStep, setCurrentStep, setError } = useInstallStore();

  const fetchPlan = useCallback(async (os?: string, distro = "humble") => {
    setPhase("planning");
    try {
      const params = new URLSearchParams({ distro });
      if (os) params.set("os", os);
      const resp = await fetch(`${BACKEND}/install/plan?${params}`);
      const data = await resp.json();
      if (data.error) {
        setError(data.error);
        setPhase("error");
        return;
      }
      setSteps(
        data.steps.map((s: any) => ({ ...s, status: "pending" as const }))
      );
      setPhase("ready");
    } catch (e) {
      setError(String(e));
      setPhase("error");
    }
  }, [setSteps, setPhase, setError]);

  const runInstall = useCallback(async (os?: string, distro = "humble", dryRun = true) => {
    setPhase("running");
    setCurrentStep(0);
    try {
      const params = new URLSearchParams({ distro, dry_run: String(dryRun) });
      if (os) params.set("os", os);
      const resp = await fetch(`${BACKEND}/install/run?${params}`, { method: "POST" });
      const reader = resp.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          if (!line.startsWith("data: ") || line === "data: [DONE]") {
            if (line === "data: [DONE]") setPhase("done");
            continue;
          }
          try {
            const evt = JSON.parse(line.slice(6));
            if (evt.type === "progress") {
              setCurrentStep(evt.step);
              updateStep(evt.id, {
                status: evt.status,
                output: evt.output,
                error: evt.error,
              });
            } else if (evt.type === "error") {
              setError(evt.error);
              setPhase("error");
            }
          } catch {}
        }
      }
      setPhase("done");
    } catch (e) {
      setError(String(e));
      setPhase("error");
    }
  }, [setPhase, setCurrentStep, updateStep, setError]);

  return { fetchPlan, runInstall };
}
