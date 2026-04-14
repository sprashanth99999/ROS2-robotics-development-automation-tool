"""WebSocket bridge for sim events — forwards sim bus events to frontend."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)
router = APIRouter()

_clients: list[WebSocket] = []


@router.websocket("/ws/sim")
async def sim_ws(ws: WebSocket):
    await ws.accept()
    _clients.append(ws)
    log.info("Sim WS client connected (%d total)", len(_clients))

    try:
        while True:
            # Keep alive — client can send pings
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _clients.remove(ws)


def _broadcast(event_type: str, data: dict):
    """Broadcast sim event to all connected WS clients."""
    msg = json.dumps({"type": event_type, **data})
    for ws in _clients:
        try:
            asyncio.get_event_loop().create_task(ws.send_text(msg))
        except Exception:
            pass


# Wire bus events to WS broadcast
bus.on("sim:connected", lambda d: _broadcast("sim:connected", d))
bus.on("sim:disconnected", lambda d: _broadcast("sim:disconnected", d))
bus.on("sim:world_launched", lambda d: _broadcast("sim:world_launched", d))
bus.on("sim:spawned", lambda d: _broadcast("sim:spawned", d))
bus.on("sim:removed", lambda d: _broadcast("sim:removed", d))
bus.on("sim:reset", lambda d: _broadcast("sim:reset", d))
