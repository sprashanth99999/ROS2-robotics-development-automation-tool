"""Filesystem tools for agents."""

from __future__ import annotations

import os
from pathlib import Path

from .registry import tool


@tool("read_file", "Read file contents")
async def read_file(path: str) -> str:
    p = Path(path).resolve()
    if not p.is_file():
        return f"[error] not found: {path}"
    return p.read_text(encoding="utf-8", errors="replace")[:50_000]


@tool("write_file", "Write content to file")
async def write_file(path: str, content: str) -> str:
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} chars → {p}"


@tool("list_dir", "List directory contents")
async def list_dir(path: str = ".") -> str:
    p = Path(path).resolve()
    if not p.is_dir():
        return f"[error] not a directory: {path}"
    entries = sorted(p.iterdir())
    lines = []
    for e in entries[:200]:
        prefix = "d " if e.is_dir() else "f "
        lines.append(prefix + e.name)
    return "\n".join(lines) if lines else "(empty)"
