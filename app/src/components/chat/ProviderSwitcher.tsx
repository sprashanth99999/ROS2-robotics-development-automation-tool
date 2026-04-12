import { useProviderStore } from "../../state/providerStore";

const PROVIDERS = ["claude", "openai", "gemini", "mistral", "ollama"];

export function ProviderSwitcher() {
  const active = useProviderStore((s) => s.active);
  const setActive = useProviderStore((s) => s.setActive);

  return (
    <select
      value={active}
      onChange={(e) => setActive(e.target.value)}
      style={{
        background: "#161b22", color: "#8b949e", border: "1px solid #30363d",
        borderRadius: 4, padding: "4px 8px", fontSize: 12, outline: "none",
      }}
    >
      {PROVIDERS.map((p) => (
        <option key={p} value={p}>{p}</option>
      ))}
    </select>
  );
}
