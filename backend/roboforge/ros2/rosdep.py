"""Rosdep wrapper — resolve and install package dependencies."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from roboforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class RosdepResult:
    success: bool = False
    output: str = ""
    missing: list[str] | None = None


async def check_deps(workspace: str) -> RosdepResult:
    """Check missing dependencies in workspace."""
    cmd = f"cd {workspace} && rosdep check --from-paths src --ignore-src -r"
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        output = stdout.decode(errors="replace")
        missing = []
        for line in output.splitlines():
            if "not found" in line.lower() or "missing" in line.lower():
                missing.append(line.strip())
        return RosdepResult(success=proc.returncode == 0, output=output[-3000:], missing=missing)
    except Exception as e:
        return RosdepResult(output=str(e))


async def install_deps(workspace: str) -> RosdepResult:
    """Install missing rosdep dependencies."""
    cmd = f"cd {workspace} && rosdep install --from-paths src --ignore-src -r -y"
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
        output = stdout.decode(errors="replace")
        return RosdepResult(success=proc.returncode == 0, output=output[-3000:])
    except Exception as e:
        return RosdepResult(output=str(e))
