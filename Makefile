# RoboForge AI — top-level dev commands.

.PHONY: help install dev build test lint typecheck codegen clean phase-status

help:
	@echo "RoboForge AI — Makefile targets"
	@echo "  install     Install JS + Python deps"
	@echo "  dev         Run Vite + backend concurrently"
	@echo "  build       Production build"
	@echo "  test        Run all tests"
	@echo "  lint        ruff check backend"
	@echo "  codegen     JSON Schemas -> TS + pydantic"
	@echo "  clean       Remove build artifacts"

install:
	cd app && npm install
	cd backend && pip install -e ".[dev]"

dev:
	cd backend && python -m roboforge --port 8765 &
	cd app && npm run dev

build:
	cd app && npm run build

test:
	cd backend && python -m pytest tests/ -q

lint:
	cd backend && python -m ruff check roboforge/

codegen:
	node scripts/codegen-types.mjs

clean:
	rm -rf app/node_modules app/dist app/dist-electron
	rm -rf backend/**/__pycache__ backend/.venv
	rm -rf .pytest_cache .mypy_cache .ruff_cache

phase-status:
	@git log --oneline -1 --grep="^feat\|^chore" || echo "no phase commits yet"
