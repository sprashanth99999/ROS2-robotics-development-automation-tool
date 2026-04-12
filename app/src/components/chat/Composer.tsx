import { useState, useRef, KeyboardEvent } from "react";

interface Props { onSend: (text: string) => void; disabled?: boolean }

export function Composer({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const t = text.trim();
    if (!t || disabled) return;
    onSend(t);
    setText("");
    ref.current?.focus();
  };

  const onKey = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  return (
    <div style={{ padding: 12, borderTop: "1px solid #21262d", display: "flex", gap: 8 }}>
      <textarea
        ref={ref}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKey}
        placeholder="Message..."
        disabled={disabled}
        rows={1}
        style={{
          flex: 1, background: "#161b22", color: "#c9d1d9", border: "1px solid #30363d",
          borderRadius: 6, padding: "8px 12px", resize: "none", fontFamily: "inherit", fontSize: 14,
          outline: "none",
        }}
      />
      <button
        onClick={submit}
        disabled={disabled || !text.trim()}
        style={{
          background: disabled || !text.trim() ? "#21262d" : "#238636",
          color: "#fff", border: "none", borderRadius: 6, padding: "8px 16px",
          cursor: disabled ? "not-allowed" : "pointer", fontWeight: 600, fontSize: 14,
        }}
      >
        Send
      </button>
    </div>
  );
}
