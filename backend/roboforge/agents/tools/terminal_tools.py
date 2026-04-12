"""Terminal/shell tools for agents."""

from __future__ import annotations

import asyncio

from .registry import tool


@tool("run_command", "Run shell command and return output")
async def run_command(command: str, cwd: str = ".") -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode(errors="replace")[:20_000]
        return f"[exit {proc.returncode}]\n{output}"
    except asyncio.TimeoutError:
        return "[error] command timed out (30s)"
    except Exception as e:
        return f"[error] {e}"
