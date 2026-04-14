"""Gazebo Harmonic (gz-sim) bridge via gz CLI + transport."""

from __future__ import annotations

import asyncio

from roboforge.sim.base import SimBridge, SimStatus
from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


class GazeboBridge(SimBridge):
    name = "gazebo"

    def __init__(self):
        self._connected = False
        self._world = ""

    async def _run(self, cmd: str) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            return stdout.decode(errors="replace").strip()
        except Exception as e:
            return f"[error] {e}"

    async def connect(self) -> bool:
        out = await self._run("gz sim --versions 2>/dev/null || ign gazebo --version 2>/dev/null")
        if "error" in out.lower() or not out:
            log.warning("Gazebo not found")
            return False
        self._connected = True
        bus.emit("sim:connected", {"simulator": "gazebo"})
        log.info("Gazebo detected: %s", out.splitlines()[0] if out else "unknown")
        return True

    async def disconnect(self) -> None:
        self._connected = False
        bus.emit("sim:disconnected", {"simulator": "gazebo"})

    async def status(self) -> SimStatus:
        if not self._connected:
            return SimStatus(simulator="gazebo")
        # Try to get world info
        out = await self._run("gz topic -l 2>/dev/null")
        entities = [l for l in out.splitlines() if l.startswith("/")]
        return SimStatus(
            connected=True, simulator="gazebo",
            world=self._world or "default",
            entities=entities[:20],
        )

    async def launch_world(self, world_file: str = "") -> dict:
        """Launch Gazebo with a world file."""
        cmd = "gz sim"
        if world_file:
            cmd += f" {world_file}"
        cmd += " &"  # background
        out = await self._run(cmd)
        self._world = world_file or "empty"
        bus.emit("sim:world_launched", {"world": self._world})
        return {"launched": True, "world": self._world, "output": out[:500]}

    async def spawn(self, model: str, name: str, position: list[float]) -> dict:
        x, y, z = position[0], position[1], position[2] if len(position) > 2 else 0
        cmd = f'gz service -s /world/default/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 5000 --req \'sdf_filename: "{model}", name: "{name}", pose: {{position: {{x: {x}, y: {y}, z: {z}}}}}\''
        out = await self._run(cmd)
        bus.emit("sim:spawned", {"name": name, "model": model})
        return {"name": name, "output": out[:500]}

    async def remove(self, name: str) -> bool:
        cmd = f'gz service -s /world/default/remove --reqtype gz.msgs.Entity --reptype gz.msgs.Boolean --timeout 5000 --req \'name: "{name}", type: 2\''
        out = await self._run(cmd)
        bus.emit("sim:removed", {"name": name})
        return "true" in out.lower()

    async def pause(self) -> None:
        await self._run("gz service -s /world/default/control --reqtype gz.msgs.WorldControl --reptype gz.msgs.Boolean --timeout 3000 --req 'pause: true'")

    async def resume(self) -> None:
        await self._run("gz service -s /world/default/control --reqtype gz.msgs.WorldControl --reptype gz.msgs.Boolean --timeout 3000 --req 'pause: false'")

    async def reset(self) -> None:
        await self._run("gz service -s /world/default/control --reqtype gz.msgs.WorldControl --reptype gz.msgs.Boolean --timeout 3000 --req 'reset: {all: true}'")
        bus.emit("sim:reset", {})


# Module singleton
gazebo = GazeboBridge()
