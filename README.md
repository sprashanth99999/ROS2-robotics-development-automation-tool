# RoboForge AI

> Unified, AI-powered desktop workspace for ROS2 robotics development.
> Design, simulate, and build robots — locally, with zero manual setup.

**Status:** All 22 phases complete. Functional prototype.

## What this is

A single downloadable desktop app that gives any robotics developer:

- **AI integration** — Claude, Gemini, GPT-4, Mistral, Ollama with streaming + tool-use
- **6 AI agents** — Planner, Setup, Coder, Reviewer, Debugger, Deployer (ReAct loop)
- **RAG pipeline** — FastEmbed + LanceDB vector search over project files
- **Automated setup** — Auto-installs ROS2 (Humble/Jazzy) with live SSE progress
- **ROS2 tools** — Node graph, topic monitor, colcon build, rosdep, rosbridge
- **3D viewer** — Three.js URDF viewer with joint controls
- **Gazebo bridge** — Launch, spawn, pause, reset via gz CLI
- **Terminal** — xterm.js with WebSocket PTY bridge
- **Project manager** — CRUD with templates (pub/sub, service)
- **Secure secrets** — OS keyring + XOR file fallback

## Quick start

```bash
cd roboforge
make install    # npm + pip deps
make dev        # starts backend (8765) + Vite (5173)
```

Or manually:
```bash
cd backend && python -m roboforge --port 8765
cd app && npm run dev
```

## CLI

```bash
python -m roboforge.cli.main serve --port 8765
python -m roboforge.cli.main project list
python -m roboforge.cli.main project create my_robot --template publisher_subscriber
python -m roboforge.cli.main ros2 detect
python -m roboforge.cli.main index /path/to/docs
```

## Architecture

```
roboforge/
├── app/         Electron + Vite + React (7 tabs: Chat, Install, Terminal, Graph, Topics, 3D, Sim)
├── backend/     FastAPI (providers, agents, ros2, sim, rag, projects, urdf)
├── shared/      JSON Schemas + generated TS/Py types
├── scripts/     Codegen, install scripts
```

## API routes (40+)

| Prefix      | Endpoints |
|-------------|-----------|
| /health     | Status    |
| /providers  | Key mgmt  |
| /chat       | SSE stream|
| /agents     | 6 roles   |
| /install    | Plan+run  |
| /ros2       | 16 routes |
| /urdf       | Parse+validate |
| /sim        | Gazebo control |
| /rag        | Index+search |
| /projects   | CRUD      |
| /ws         | Events    |
| /ws/terminal| PTY       |
| /ws/sim     | Sim events|

## Tech stack

| Layer | Choice |
|-------|--------|
| Frontend | Electron + Vite + React 19 + TypeScript |
| State | Zustand |
| 3D | Three.js + urdf-loader |
| Graph | React Flow |
| Charts | Recharts |
| Terminal | xterm.js |
| Backend | FastAPI + uvicorn |
| AI | 5 providers (httpx streaming) |
| Agents | Custom ReAct loop |
| Vectors | LanceDB + FastEmbed |
| Secrets | python-keyring + XOR fallback |

## License

MIT — see `LICENSE`.
