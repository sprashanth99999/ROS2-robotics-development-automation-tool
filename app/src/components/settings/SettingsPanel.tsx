import { useState, useEffect } from "react";

const BACKEND = "http://127.0.0.1:8765";
const PROVIDERS = [
  { id: "claude", label: "Claude (Anthropic)", placeholder: "sk-ant-api03-..." },
  { id: "openai", label: "OpenAI", placeholder: "sk-..." },
  { id: "gemini", label: "Google Gemini", placeholder: "AIza..." },
  { id: "mistral", label: "Mistral", placeholder: "..." },
  { id: "ollama", label: "Ollama (local)", placeholder: "not required" },
];

export function SettingsPanel() {
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BACKEND}/providers`).then(r => r.json()).then((data) => {
      const st: Record<string, string> = {};
      for (const p of data || []) st[p.name] = p.has_key ? "set" : "unset";
      setStatus(st);
    }).catch(() => {});
  }, []);

  const save = async (provider: string) => {
    const key = keys[provider];
    if (!key) return;
    setSaving(provider);
    try {
      const r = await fetch(`${BACKEND}/providers/key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, api_key: key }),
      });
      if (r.ok) {
        setStatus((s) => ({ ...s, [provider]: "set" }));
        setKeys((k) => ({ ...k, [provider]: "" }));
      }
    } catch {}
    setSaving(null);
  };

  const remove = async (provider: string) => {
    setSaving(provider);
    try {
      await fetch(`${BACKEND}/providers/key/${provider}`, { method: "DELETE" });
      setStatus((s) => ({ ...s, [provider]: "unset" }));
    } catch {}
    setSaving(null);
  };

  return (
    <div style={{ padding: 24, maxWidth: 600 }}>
      <b style={{ color: "#58a6ff", fontSize: 16, display: "block", marginBottom: 4 }}>
        AI Provider API Keys
      </b>
      <div style={{ color: "#8b949e", fontSize: 11, marginBottom: 20 }}>
        Keys stored in OS keyring (fallback: XOR-encrypted file). Never committed.
      </div>

      {PROVIDERS.map((p) => (
        <div key={p.id} style={{ marginBottom: 16, padding: 12, background: "#161b22", borderRadius: 6, border: "1px solid #30363d" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <b style={{ color: "#c9d1d9", fontSize: 13 }}>{p.label}</b>
            <span style={{
              fontSize: 10, padding: "2px 8px", borderRadius: 10, fontWeight: 600,
              background: status[p.id] === "set" ? "#238636" : "#30363d",
              color: status[p.id] === "set" ? "#fff" : "#8b949e",
            }}>
              {status[p.id] === "set" ? "CONFIGURED" : "NOT SET"}
            </span>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <input
              type="password"
              placeholder={p.placeholder}
              value={keys[p.id] || ""}
              onChange={(e) => setKeys((k) => ({ ...k, [p.id]: e.target.value }))}
              style={{
                flex: 1, background: "#0d1117", color: "#c9d1d9",
                border: "1px solid #30363d", borderRadius: 4,
                padding: "6px 10px", fontSize: 12, outline: "none",
                fontFamily: "monospace",
              }}
            />
            <button
              onClick={() => save(p.id)}
              disabled={!keys[p.id] || saving === p.id}
              style={{
                background: "#238636", color: "#fff", border: "none",
                borderRadius: 4, padding: "6px 14px", cursor: "pointer",
                fontSize: 12, fontWeight: 600,
                opacity: (!keys[p.id] || saving === p.id) ? 0.5 : 1,
              }}
            >
              {saving === p.id ? "..." : "Save"}
            </button>
            {status[p.id] === "set" && (
              <button
                onClick={() => remove(p.id)}
                disabled={saving === p.id}
                style={{
                  background: "#da3633", color: "#fff", border: "none",
                  borderRadius: 4, padding: "6px 10px", cursor: "pointer", fontSize: 12,
                }}
              >
                Remove
              </button>
            )}
          </div>
        </div>
      ))}

      <div style={{ marginTop: 20, padding: 12, background: "#0d1117", border: "1px solid #30363d", borderRadius: 6, fontSize: 11, color: "#8b949e" }}>
        <b style={{ color: "#c9d1d9" }}>Get a key:</b>
        <div>Claude: console.anthropic.com</div>
        <div>OpenAI: platform.openai.com/api-keys</div>
        <div>Gemini: aistudio.google.com/apikey</div>
        <div>Mistral: console.mistral.ai</div>
        <div>Ollama: runs locally, no key needed</div>
      </div>
    </div>
  );
}
