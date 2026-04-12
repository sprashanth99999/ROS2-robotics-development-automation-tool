// Renderer-side IPC wrapper. Uses window.api exposed by preload.
declare global {
  interface Window {
    api: {
      invoke: (channel: string, ...args: unknown[]) => Promise<unknown>;
      on: (channel: string, cb: (...args: unknown[]) => void) => void;
    };
  }
}

export const ipc = {
  invoke: <T = unknown>(channel: string, ...args: unknown[]): Promise<T> =>
    window.api.invoke(channel, ...args) as Promise<T>,
  on: (channel: string, cb: (...args: unknown[]) => void) =>
    window.api.on(channel, cb),
};
