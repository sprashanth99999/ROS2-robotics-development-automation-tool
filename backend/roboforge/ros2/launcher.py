"""ROS2 node/launch file launcher."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)

_processes: dict[str, asyncio.subprocess.Process] = {}


@dataclass
class LaunchResult:
    pid: int | None = None
    name: str = ""
    error: str | None = None


async def launch_node(package: str, executable: str, args: list[str] | None = None,
                      env: dict[str, str] | None = None) -> LaunchResult:
    """Launch a ROS2 node via ros2 run."""
    cmd = f"ros2 run {package} {executable}"
    if args:
        cmd += " " + " ".join(args)
    name = f"{package}/{executable}"

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        _processes[name] = proc
        bus.emit("ros2:node_launched", {"name": name, "pid": proc.pid})
        log.info("Launched %s (pid=%s)", name, proc.pid)
        return LaunchResult(pid=proc.pid, name=name)
    except Exception as e:
        return LaunchResult(name=name, error=str(e))


async def launch_file(package: str, launch_file: str, args: list[str] | None = None,
                      env: dict[str, str] | None = None) -> LaunchResult:
    """Launch a ROS2 launch file."""
    cmd = f"ros2 launch {package} {launch_file}"
    if args:
        cmd += " " + " ".join(args)
    name = f"{package}/{launch_file}"

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        _processes[name] = proc
        bus.emit("ros2:launch_started", {"name": name, "pid": proc.pid})
        return LaunchResult(pid=proc.pid, name=name)
    except Exception as e:
        return LaunchResult(name=name, error=str(e))


async def stop_node(name: str) -> bool:
    """Stop a launched node/launch by name."""
    proc = _processes.pop(name, None)
    if not proc:
        return False
    try:
        proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=5)
    except asyncio.TimeoutError:
        proc.kill()
    bus.emit("ros2:node_stopped", {"name": name})
    return True


def list_running() -> list[dict[str, Any]]:
    """List running ROS2 processes."""
    return [
        {"name": n, "pid": p.pid, "running": p.returncode is None}
        for n, p in _processes.items()
    ]
