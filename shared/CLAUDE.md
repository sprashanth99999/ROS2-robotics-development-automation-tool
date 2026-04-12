# shared/ — Language-Neutral Contracts

## Purpose
Single source of truth for all data shapes exchanged between the Electron
frontend (`app/`) and the Python backend (`backend/`). Everything here is
a JSON Schema; generated TS and pydantic types live in `ts/` and `py/`.

## Rules
- **Never hand-edit `ts/index.ts` or `py/__init__.py`** — they are generated
  by `scripts/codegen-types.ts`. Edit the `.json` schema, then run
  `pnpm codegen`.
- Each schema file maps to one top-level type.
- Schemas use JSON Schema draft 2020-12.
- Keep schemas flat and under 80 lines each.

## Allowed consumers
- `app/` imports from `@roboforge/shared` (the TS side).
- `backend/` imports from `shared.py` (added to `sys.path` by the backend).
- No other module should import from here directly.

## Public surface
| Schema file            | TS type             | Pydantic model         |
|------------------------|---------------------|------------------------|
| ipc-envelope.json      | IpcEnvelope         | IpcEnvelope            |
| provider-message.json  | ProviderMessage     | ProviderMessage        |
| agent-event.json       | AgentEvent          | AgentEvent             |
| ros2-topic.json        | Ros2Topic           | Ros2Topic              |
| node-graph.json        | NodeGraph           | NodeGraph              |
| project-config.json    | ProjectConfig       | ProjectConfig          |
| install-status.json    | InstallStatus       | InstallStatus          |
