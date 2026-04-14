import { useEffect, useState, useRef } from "react";

const BACKEND = "http://127.0.0.1:8765";
const GIS_SRC = "https://accounts.google.com/gsi/client";

declare global {
  interface Window {
    google?: any;
  }
}

type User = { email: string; name: string; picture: string } | null;

export function GoogleAuthSection() {
  const [clientId, setClientId] = useState<string>("");
  const [inputId, setInputId] = useState<string>("");
  const [configured, setConfigured] = useState(false);
  const [user, setUser] = useState<User>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const btnRef = useRef<HTMLDivElement>(null);

  const refreshUser = () => {
    fetch(`${BACKEND}/auth/me`).then(r => r.ok ? r.json() : null).then(setUser).catch(() => {});
  };

  useEffect(() => {
    fetch(`${BACKEND}/auth/config`).then(r => r.json()).then((d) => {
      if (d.client_id) { setClientId(d.client_id); setConfigured(true); }
    }).catch(() => {});
    refreshUser();
  }, []);

  useEffect(() => {
    if (!configured || !clientId || user) return;
    const existing = document.querySelector(`script[src="${GIS_SRC}"]`);
    if (!existing) {
      const s = document.createElement("script");
      s.src = GIS_SRC; s.async = true; s.defer = true;
      s.onload = initGoogle;
      document.head.appendChild(s);
    } else { initGoogle(); }

    function initGoogle() {
      if (!window.google?.accounts?.id) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (resp: any) => handleCredential(resp.credential),
      });
      if (btnRef.current) {
        btnRef.current.innerHTML = "";
        window.google.accounts.id.renderButton(btnRef.current, {
          theme: "filled_blue", size: "medium", text: "signin_with", shape: "rectangular",
        });
      }
    }
  }, [configured, clientId, user]);

  const handleCredential = async (idToken: string) => {
    setLoading(true); setError("");
    try {
      const r = await fetch(`${BACKEND}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
      });
      if (r.ok) { const d = await r.json(); setUser(d.user); }
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

  const logout = async () => {
    await fetch(`${BACKEND}/auth/logout`, { method: "POST" });
    setUser(null);
  };

  return (
    <div style={{ marginBottom: 20, padding: 12, background: "#161b22", borderRadius: 6, border: "1px solid #30363d" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <b style={{ color: "#c9d1d9", fontSize: 13 }}>Google Account</b>
        <span style={{
          fontSize: 10, padding: "2px 8px", borderRadius: 10, fontWeight: 600,
          background: user ? "#238636" : "#30363d",
          color: user ? "#fff" : "#8b949e",
        }}>
          {user ? "SIGNED IN" : "OPTIONAL"}
        </span>
      </div>
      <div style={{ color: "#8b949e", fontSize: 11, marginBottom: 10 }}>
        For Gemini (Google AI Studio) and Gmail access. Claude uses API key below.
      </div>

      {user ? (
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {user.picture && <img src={user.picture} alt="" style={{ width: 28, height: 28, borderRadius: 14 }} />}
          <div style={{ flex: 1 }}>
            <div style={{ color: "#c9d1d9", fontSize: 12, fontWeight: 600 }}>{user.name}</div>
            <div style={{ color: "#8b949e", fontSize: 11 }}>{user.email}</div>
          </div>
          <button onClick={logout} style={{ background: "#da3633", color: "#fff", border: "none", borderRadius: 4, padding: "6px 12px", cursor: "pointer", fontSize: 11 }}>
            Sign out
          </button>
        </div>
      ) : !configured ? (
        <div>
          <div style={{ fontSize: 10, color: "#8b949e", marginBottom: 6 }}>
            Paste OAuth 2.0 Client ID from console.cloud.google.com/apis/credentials (Web app, origin http://localhost:5173)
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <input
              type="text"
              placeholder="xxxxx.apps.googleusercontent.com"
              value={inputId}
              onChange={(e) => setInputId(e.target.value)}
              style={{ flex: 1, background: "#0d1117", color: "#c9d1d9", border: "1px solid #30363d", borderRadius: 4, padding: "6px 10px", fontSize: 11, fontFamily: "monospace", outline: "none" }}
            />
            <button
              onClick={saveClientId}
              disabled={!inputId.trim()}
              style={{ background: "#238636", color: "#fff", border: "none", borderRadius: 4, padding: "6px 14px", cursor: "pointer", fontSize: 11, fontWeight: 600, opacity: inputId.trim() ? 1 : 0.5 }}
            >
              Save
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div ref={btnRef} />
          {loading && <div style={{ color: "#8b949e", fontSize: 11, marginTop: 6 }}>Verifying...</div>}
          {error && <div style={{ color: "#f85149", fontSize: 11, marginTop: 6 }}>{error}</div>}
          <button
            onClick={() => { setConfigured(false); setClientId(""); }}
            style={{ background: "none", color: "#8b949e", border: "none", cursor: "pointer", fontSize: 10, marginTop: 6, textDecoration: "underline" }}
          >
            Change Client ID
          </button>
        </div>
      )}
    </div>
  );
}
