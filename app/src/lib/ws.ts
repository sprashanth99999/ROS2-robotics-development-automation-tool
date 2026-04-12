// Auto-reconnecting WebSocket for real-time backend events.
type Listener = (data: unknown) => void;

export class ReconnectingWs {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Listener>> = new Map();
  private url: string;
  private retryMs: number;

  constructor(url: string, retryMs = 3000) {
    this.url = url;
    this.retryMs = retryMs;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        const type = msg.type as string;
        this.listeners.get(type)?.forEach((cb) => cb(msg.payload));
        this.listeners.get("*")?.forEach((cb) => cb(msg));
      } catch { /* ignore malformed */ }
    };
    this.ws.onclose = () => setTimeout(() => this.connect(), this.retryMs);
    this.ws.onerror = () => this.ws?.close();
  }

  on(type: string, cb: Listener) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type)!.add(cb);
    return () => this.listeners.get(type)?.delete(cb);
  }

  send(data: unknown) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  close() { this.ws?.close(); }
}
