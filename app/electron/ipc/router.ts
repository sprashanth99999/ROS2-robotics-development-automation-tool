// IPC main-process handler registration.
import { ipcMain } from "electron";
import { CH } from "./channels";
import { getBackendPort } from "../backend-process";

export function registerIpcHandlers() {
  ipcMain.handle(CH.BACKEND_PORT, () => getBackendPort());

  ipcMain.handle(CH.HEALTH, async () => {
    const port = getBackendPort();
    if (!port) return { status: "offline" };
    try {
      const r = await fetch(`http://127.0.0.1:${port}/health`);
      return await r.json();
    } catch {
      return { status: "error" };
    }
  });
}
