"""Colcon build wrapper."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator

from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class BuildResult:
    success: bool = False
    output: str = ""
    packages: list[str] | None = None


async def build(workspace: str, packages: list[str] | None = None,
                env: dict[str, str] | None = None) -> BuildResult:
    """Run colcon build in workspace."""
    cmd = f"cd {workspace} && colcon build"
    if packages:
        cmd += " --packages-select " + " ".join(packages)
    cmd += " --symlink-install"

    bus.emit("colcon:build_start", {"workspace": workspace, "packages": packages})

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)
        output = stdout.decode(errors="replace")

        success = proc.returncode == 0
        bus.emit("colcon:build_done", {"success": success})
        return BuildResult(success=success, output=output[-5000:], packages=packages)
    except asyncio.TimeoutError:
        return BuildResult(output="build timed out (300s)")
    except Exception as e:
        return BuildResult(output=str(e))


async def build_stream(workspace: str, packages: list[str] | None = None,
                       env: dict[str, str] | None = None) -> AsyncIterator[str]:
    """Stream colcon build output line by line."""
    cmd = f"cd {workspace} && colcon build"
    if packages:
        cmd += " --packages-select " + " ".join(packages)
    cmd += " --symlink-install --event-handlers console_direct+"

    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        env=env,
    )
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        yield line.decode(errors="replace")
    await proc.wait()
