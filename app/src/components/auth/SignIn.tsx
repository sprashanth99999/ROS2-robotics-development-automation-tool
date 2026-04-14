import { useEffect, useState, useRef } from "react";

const BACKEND = "http://127.0.0.1:8765";
const GIS_SRC = "https://accounts.google.com/gsi/client";

declare global {
  interface Window {
    google?: any;
  }
}

export function SignIn({ onSignedIn }: { onSignedIn: () => void }) {
  const [clientId, setClientId] = useState<string>("");
  const [inputId, setInputId] = useState<string>("");
  const [configured, setConfigured] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const btnRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${BACKEND}/auth/config`).then(r => r.json()).then((d) => {
      if (d.client_id) { setClientId(d.client_id); setConfigured(true); }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!configured || !clientId) return;
    if (!document.querySelector(`script[src="${GIS_SRC}"]`)) {
      const s = document.createElement("script");
      s.src = GIS_SRC; s.async = true; s.defer = true;
      document.head.appendChild(s);
      s.onload = () => initGoogle();
    } else { initGoogle(); }

    function initGoogle() {
      if (!window.google?.accounts?.id) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (resp: any) => handleCredential(resp.credential),
      });
      if (btnRef.current) {
        window.google.accounts.id.renderButton(btnRef.current, {
          theme: "filled_blue", size: "large", text: "signin_with", shape: "rectangular",
        });
      }
    }
  }, [configured, clientId]);

  const handleCredential = async (idToken: string) => {
    setLoading(true); setError("");
    try {
      const r = await fetch(`${BACKEND}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
      });
      if (r.ok) onSignedIn();
      else { const d = await r.json(); setError(d.detail || "Sign-in failed"); }
    } catch (e: any) { setError(String(e)); }
    setLoading(false);
  };

  const saveClientId = async () => {
    if (!inputId.trim()) return;
    await fetch(`${BACKEND}/auth/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_id: inputId.trim() }),
    });
    setClientId(inputId.trim()); setConfigured(true); setInputId("");
  };

  return (
    <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#0d1117", color: "#c9d1d9", fontFamily: "monospace" }}>
      <div style={{ maxWidth: 440, padding: 32, background: "#161b22", borderRadius: 8, border: "1px solid #30363d" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: "#58a6ff", marginBottom: 4 }}>RoboForge AI</div>
          <div style={{ fontSize: 12, color: "#8b949e" }}>Sign in to access your workspace</div>
        </div>

        {!configured ? (
          <div>
            <div style={{ fontSize: 12, color: "#8b949e", marginBottom: 8 }}>
              First-time setup: paste your Google OAuth Client ID.
            </div>
            <div style={{ fontSize: 11, color: "#8b949e", marginBottom: 12 }}>
              Get one at <b style={{ color: "#58a6ff" }}>console.cloud.google.com/apis/credentials</b>
              {" "}→ Create OAuth 2.0 Client → Web app → add <code style={{ background: "#0d1117", padding: "2px 4px", borderRadius: 3 }}>http://localhost:5173</code> to authorized origins.
            </div>
            <input
              type="text"
              placeholder="xxxxx.apps.googleusercontent.com"
              value={inputId}
              onChange={(e) => setInputId(e.target.value)}
              style={{ width: "100%", background: "#0d1117", color: "#c9d1d9", border: "1px solid #30363d", borderRadius: 4, padding: "8px 12px", fontSize: 12, fontFamily: "monospace", marginBottom: 8, boxSizing: "border-box" }}
            />
            <button
              onClick={saveClientId}
              disabled={!inputId.trim()}
              style={{ width: "100%", background: "#238636", color: "#fff", border: "none", borderRadius: 4, padding: "8px 16px", cursor: "pointer", fontSize: 12, fontWeight: 600, opacity: inputId.trim() ? 1 : 0.5 }}
            >
              Save & Continue
            </button>
          </div>
        ) : (
          <div>
            <div ref={btnRef} style={{ display: "flex", justifyContent: "center", marginBottom: 12 }} />
            {loading && <div style={{ textAlign: "center", color: "#8b949e", fontSize: 11 }}>Verifying...</div>}
            {error && <div style={{ color: "#f85149", fontSize: 11, textAlign: "center", marginBottom: 8 }}>{error}</div>}
            <button
              onClick={() => { setConfigured(false); setClientId(""); }}
              style={{ width: "100%", background: "transparent", color: "#8b949e", border: "1px solid #30363d", borderRadius: 4, padding: "6px 12px", cursor: "pointer", fontSize: 11, marginTop: 8 }}
            >
              Change Client ID
            </button>
          </div>
        )}

        <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid #30363d", fontSize: 10, color: "#8b949e", textAlign: "center" }}>
          After sign-in → Settings tab → add Claude API key to code with AI.
        </div>
      </div>
    </div>
  );
}
