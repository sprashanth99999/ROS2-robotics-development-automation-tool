# RoboForge AI

> Unified, AI-powered desktop workspace for ROS2 robotics development.
> Design, simulate, and build robots — locally, with zero manual setup.

**Status:** Phase 0 — repository scaffolding. Not yet runnable.
See `docs/build-plan.md` (added in Phase 1) and the approved implementation
plan in `~/.claude/plans/kind-gathering-llama.md`.

## What this is

A single downloadable desktop app that gives any robotics developer:

- **AI integration layer** — Claude, Gemini, GPT-4, Mistral, Ollama, with
  streaming + tool-use, RAG over your project files, and per-provider
  keychain-stored credentials.
- **Automated environment setup** — auto-installs ROS2 (Humble/Iron/Jazzy),
  Gazebo, and Isaac Sim with live progress logs and health checks.
- **Unified viewer** — 3D URDF viewer, embedded Gazebo viewport, ROS2 node
  graph, embedded terminal, AI chat panel, and live topic monitor in one
  window.
- **AI robot building assistant** — generates URDF/SDF, ROS2 nodes, launch
  files, and MoveIt configs from natural language; debugs build errors.
- **Project management** — git-aware projects, robot templates, package
  manager, and export to ROS2 / Isaac USD / Gazebo bundles.

## Repository layout

```
roboforge/
├── app/         Electron + React + TypeScript desktop shell
├── backend/     Python FastAPI service (AI, agents, ROS2, sim, RAG)
├── shared/      Language-neutral JSON Schemas + generated TS/Py types
├── templates/   Robot templates (diff drive, arm, quadruped, drone, mobile manipulator)
├── scripts/     Dev runners, codegen, scaffolding helpers
├── docs/        Architecture, providers, agents, ROS2, RAG docs
└── tests/       Cross-cutting integration & E2E
```

## Quick start (after Phase 22)

```bash
pnpm install && uv sync
pnpm dev          # Phase 4+
```

## License

MIT — see `LICENSE`.
