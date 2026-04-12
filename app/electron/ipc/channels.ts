// Typed IPC channel names shared between main and renderer.
export const CH = {
  HEALTH: "roboforge:health",
  BACKEND_PORT: "roboforge:backend-port",
  CONFIG_GET: "roboforge:config:get",
  CONFIG_SET: "roboforge:config:set",
  SECRET_GET: "roboforge:secret:get",
  SECRET_SET: "roboforge:secret:set",
  SECRET_DELETE: "roboforge:secret:delete",
} as const;

export type Channel = (typeof CH)[keyof typeof CH];
