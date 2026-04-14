# RoboForge AI — Root Agent Instructions

You are working in **RoboForge AI**, an open-source desktop app that gives
robotics developers an AI-powered ROS2 workspace. This repo is built
incrementally in **22 phases** (see `~/.claude/plans/kind-gathering-llama.md`).
**Each session works on exactly one phase.**

## Current build phase

Check `git log --oneline | head -1` to see the last completed phase. The next
phase is whichever has not yet been committed in the build sequence.

## Token-budget rules — READ BEFORE EVERY ACTION

These are the most important rules in this repo. Violating them wastes the
user's tokens and breaks the per-session isolation strategy.

1. **Per-file cap ~200 lines.** If a file is approaching this, split it.
2. **Load only nearest-ancestor `CLAUDE.md`.** Each module dir has its own
   `CLAUDE.md` with module-local rules. Never preemptively read sibling
   modules' `CLAUDE.md` files.
3. **Read only files listed in the current phase's "Read" column** of
   `docs/build-plan.md`. Don't browse the repo for context. If you genuinely
   need cross-module info, spawn a read-only Explore subagent — don't load
   it into the main context.
4. **No cross-module imports except through interface files.**
   - `agents/*` may import `providers/base` but never `providers/claude`.
   - `app/components/*/...` may import `shared/ts` but never sibling
     component dirs.
   - This is enforced by `import-linter` (added in Phase 1).
5. **Skeleton-first.** If a file you need doesn't exist yet but is listed
   in the plan, stub its interface (signatures + docstrings + `raise
   NotImplementedError`) — don't expand scope.
6. **Generators for repetition.** Five AI providers and five agent roles
   share a template. Use `scripts/make-provider.ts` (Phase 7) and
   `scripts/make-agent.ts` (Phase 19) — don't hand-write duplicates.
7. **One phase = one commit.** Use the commit message from the phase row.
   Sessions always start from a known-green commit.

## Default tech choices (committed defaults — don't re-litigate)

| Layer            | Choice                       |
|------------------|------------------------------|
| JS pkg manager   | pnpm (workspaces in `pnpm-workspace.yaml`) |
| Py pkg manager   | uv (`.python-version` = 3.11) |
| Frontend         | Electron + Vite + React + TypeScript strict |
| UI               | Tailwind + shadcn/ui          |
| State            | Zustand (one store per slice) |
| Backend          | Python FastAPI + uvicorn      |
| Schemas          | JSON Schema → codegen TS + pydantic |
| AI providers     | custom abstraction (no LangChain) |
| Vector store     | LanceDB (primary), chroma stub |
| Embeddings       | fastembed (ONNX, no torch)    |
| 3D viewer        | Three.js + urdf-loader        |
| ROS2 default     | Humble on Ubuntu 22.04        |
| Terminal         | xterm.js + node-pty           |

## Workflow

1. `git log --oneline | head -3` — confirm last phase.
2. Open `docs/build-plan.md` (Phase 1+) to find the next phase row.
3. Read ONLY the files in the "Read" column.
4. Write the files in the "Write" column. Stay under line caps.
5. Run the verification command from the phase row.
6. Commit with the phase's conventional message.

## Things to avoid

- Don't run `pnpm install` or `uv sync` opportunistically — they belong
  to specific phases.
- Don't add docstrings or comments to code you didn't change.
- Don't introduce new top-level dependencies without updating the plan.
- Don't write files outside the phase's scope, even if "while you're there".
- Don't load `claude-skills/` from the parent directory — it is reference
  material only, NOT a dependency.

## Caveman mode (token reduction)

Respond terse. All technical substance stay. Only fluff die.
- Drop: articles, filler, pleasantries, hedging
- Pattern: `[thing] [action] [reason]. [next step].`
- Code blocks unchanged. Errors quoted exact.
- Abbreviate: DB/auth/config/req/res/fn/impl
- Arrows for causality: X → Y
- Full clarity for: security warnings, irreversible ops, multi-step sequences

## Code review graph

`code-review-graph` MCP tools available. Token-efficient reviews:
1. First call: `get_minimal_context(task="<desc>")` — ~100 tokens
2. Use `detail_level="minimal"` for subsequent calls
3. Target: ≤5 tool calls per task, ≤800 tokens graph context
4. `next_tool_suggestions` field guides optimal next step

## When stuck

Use `AskUserQuestion` rather than guessing. Token cost of one question ≪
token cost of an unwanted refactor.
