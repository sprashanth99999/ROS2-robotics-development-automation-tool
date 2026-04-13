"""Rosbridge WebSocket client — connects to rosbridge_server for topic introspection."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)

try:
    import websockets
    HAS_WS = True
except ImportError:
    HAS_WS = False


class RosbridgeClient:
    """Async client for rosbridge_server (ws://localhost:9090)."""

    def __init__(self, url: str = "ws://localhost:9090"):
        self.url = url
        self._ws: Any = None
        self._id = 0
        self._callbacks: dict[str, Callable] = {}

    @property
    def connected(self) -> bool:
        return self._ws is not None

    async def connect(self) -> bool:
        if not HAS_WS:
            log.warning("websockets not installed, rosbridge disabled")
            return False
        try:
            self._ws = await websockets.connect(self.url)
            bus.emit("rosbridge:connected", {"url": self.url})
            log.info("Connected to rosbridge at %s", self.url)
            return True
        except Exception as e:
            log.warning("Rosbridge connect failed: %s", e)
            return False

    async def disconnect(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None
            bus.emit("rosbridge:disconnected", {})

    def _next_id(self) -> str:
        self._id += 1
        return f"roboforge_{self._id}"

    async def call_service(self, service: str, args: dict | None = None) -> dict:
        """Call a ROS2 service via rosbridge."""
        if not self._ws:
            return {"error": "not connected"}
        msg = {"op": "call_service", "id": self._next_id(),
               "service": service, "args": args or {}}
        await self._ws.send(json.dumps(msg))
        resp = await asyncio.wait_for(self._ws.recv(), timeout=10)
        return json.loads(resp)

    async def subscribe(self, topic: str, msg_type: str, callback: Callable) -> str:
        """Subscribe to a ROS2 topic."""
        if not self._ws:
            return ""
        sub_id = self._next_id()
        msg = {"op": "subscribe", "id": sub_id, "topic": topic, "type": msg_type}
        await self._ws.send(json.dumps(msg))
        self._callbacks[sub_id] = callback
        return sub_id

    async def unsubscribe(self, sub_id: str) -> None:
        if not self._ws:
            return
        msg = {"op": "unsubscribe", "id": sub_id}
        await self._ws.send(json.dumps(msg))
        self._callbacks.pop(sub_id, None)

    async def publish(self, topic: str, msg_type: str, data: dict) -> None:
        if not self._ws:
            return
        msg = {"op": "publish", "topic": topic, "msg": data}
        await self._ws.send(json.dumps(msg))

    async def listen(self) -> None:
        """Listen loop — dispatches messages to subscribers."""
        if not self._ws:
            return
        try:
            async for raw in self._ws:
                data = json.loads(raw)
                sub_id = data.get("id")
                if sub_id and sub_id in self._callbacks:
                    self._callbacks[sub_id](data.get("msg", {}))
        except Exception as e:
            log.warning("Rosbridge listen error: %s", e)
            bus.emit("rosbridge:disconnected", {"error": str(e)})


# Module singleton
bridge = RosbridgeClient()
