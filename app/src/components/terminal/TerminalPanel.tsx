import { useEffect, useRef } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";

const WS_URL = "ws://127.0.0.1:8765/ws/terminal";

export function TerminalPanel() {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const term = new Terminal({
      theme: {
        background: "#0d1117",
        foreground: "#c9d1d9",
        cursor: "#58a6ff",
        selectionBackground: "#264f78",
      },
      fontFamily: "Consolas, 'Courier New', monospace",
      fontSize: 13,
      cursorBlink: true,
    });

    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current);
    fit.fit();
    termRef.current = term;

    // Connect WS
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      term.writeln("\x1b[32m[roboforge]\x1b[0m Terminal connected");
    };
    ws.onmessage = (e) => {
      term.write(e.data);
    };
    ws.onclose = () => {
      term.writeln("\r\n\x1b[31m[disconnected]\x1b[0m");
    };

    // Send keystrokes
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    // Resize handler
    const onResize = () => fit.fit();
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("resize", onResize);
      ws.close();
      term.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ flex: 1, padding: 4, background: "#0d1117", minHeight: 200 }}
    />
  );
}
