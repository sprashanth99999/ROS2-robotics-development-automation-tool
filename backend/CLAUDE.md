# backend/ — Python FastAPI Service

## Purpose
Local HTTP + WebSocket server powering all RoboForge AI backend logic:
AI providers, agent orchestration, ROS2 lifecycle, simulation bridges,
RAG pipeline, config management, and project CRUD.

## Tech stack
- Python 3.11, FastAPI + uvicorn, pydantic v2
- No LangChain — custom agent loop in `agents/loop.py`
- SQLite + YAML for config, LanceDB for vector store

## Package layout
`roboforge/` is the importable Python package. Run with:
```bash
python -m roboforge          # starts uvicorn on a free port
python -m roboforge --port 8765  # explicit port
```

## Rules
- Each submodule has its own `CLAUDE.md` — read only the one you're working in.
- Import shared pydantic types via: `from roboforge.config.paths import shared_py_path`
  then add to `sys.path` — or import directly after Phase 2 wires it.
- Cross-module imports: use only the `base.py` / interface file of sibling
  modules, never concrete implementations.
- Per-file cap ~200 lines.

## Submodule map
| Dir          | Purpose                                   | Phase |
|--------------|-------------------------------------------|-------|
| api/         | FastAPI route handlers                    | 2+    |
| ipc/         | Event bus + envelope validation           | 5     |
| config/      | Paths, schema, YAML/SQLite loader         | 2     |
| keychain/    | Secure secret storage                     | 3     |
| providers/   | AI provider abstraction                   | 6–7   |
| agents/      | Agent roles + tool registry               | 9+    |
| ros2/        | ROS2 detection, install, launch, inspect  | 10+   |
| sim/         | Gazebo + Isaac Sim bridges                | 18    |
| rag/         | Vector store + embeddings + indexer       | 20    |
| projects/    | Project CRUD + templates + export         | 21    |
| install/     | Install plan + streamed runner            | 10    |
| urdf/        | URDF parse + generate + validate          | 17    |
| utils/       | Logging, subprocess helpers, OS detect    | 2     |
| cli/         | `roboforge` CLI entrypoint                | 22    |
