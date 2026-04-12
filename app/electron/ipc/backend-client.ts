// HTTP + WebSocket client for renderer → backend communication.
import { getBackendPort } from "../backend-process";

export function backendUrl(path: string): string {
  const port = getBackendPort() ?? 8765;
  return `http://127.0.0.1:${port}${path}`;
}

export function backendWsUrl(path: string = "/ws"): string {
  const port = getBackendPort() ?? 8765;
  return `ws://127.0.0.1:${port}${path}`;
}
