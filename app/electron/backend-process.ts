import { spawn, ChildProcess } from "child_process";

let proc: ChildProcess | null = null;
let port: number | null = null;

export function startBackend(): Promise<number> {
  return new Promise((resolve, reject) => {
    proc = spawn("python", ["-m", "roboforge"], {
      cwd: process.env.ROBOFORGE_BACKEND_DIR,
      stdio: ["ignore", "pipe", "pipe"],
    });

    proc.stdout?.on("data", (chunk: Buffer) => {
      const line = chunk.toString();
      const match = line.match(/ROBOFORGE_PORT=(\d+)/);
      if (match) {
        port = parseInt(match[1], 10);
        resolve(port);
      }
    });

    proc.on("error", reject);
    proc.on("exit", (code) => {
      if (!port) reject(new Error(`Backend exited with code ${code}`));
    });

    setTimeout(() => { if (!port) reject(new Error("Backend start timeout")); }, 10000);
  });
}

export function stopBackend() {
  proc?.kill();
  proc = null;
}

export function getBackendPort(): number | null {
  return port;
}
