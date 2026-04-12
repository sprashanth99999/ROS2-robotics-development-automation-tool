# RoboForge AI — top-level dev commands.
# Phases that introduce real implementations replace the placeholder echos.

.PHONY: help install dev build test lint typecheck codegen clean phase-status

help:
	@echo "RoboForge AI — Makefile targets"
	@echo "  install     Install JS + Python deps (pnpm install + uv sync)"
	@echo "  dev         Run app + backend in dev mode (Phase 4+)"
	@echo "  build       Production build (Phase 22)"
	@echo "  test        Run all tests (Phase 22)"
	@echo "  lint        ESLint + ruff (Phase 1+)"
	@echo "  typecheck   tsc --noEmit + mypy (Phase 1+)"
	@echo "  codegen     JSON Schemas -> TS + pydantic (Phase 1)"
	@echo "  clean       Remove build artifacts and caches"
	@echo "  phase-status Show last completed phase commit"

install:
	pnpm install
	uv sync

dev:
	@echo "[phase 4+] pnpm dev"

build:
	@echo "[phase 22] pnpm build"

test:
	@echo "[phase 22] pnpm test && uv run pytest"

lint:
	@echo "[phase 1+] pnpm lint && uv run ruff check ."

typecheck:
	@echo "[phase 1+] pnpm typecheck && uv run mypy backend"

codegen:
	@echo "[phase 1] pnpm codegen"

clean:
	rm -rf node_modules dist build out coverage .vite .pytest_cache .mypy_cache .ruff_cache
	rm -rf backend/**/__pycache__ backend/.venv

phase-status:
	@git log --oneline -1 --grep="^feat\|^chore" || echo "no phase commits yet"
