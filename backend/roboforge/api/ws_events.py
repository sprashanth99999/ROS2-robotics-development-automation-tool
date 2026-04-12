"""WebSocket endpoint that bridges the event bus to connected clients."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

router = APIRouter()
logger = get_logger("ws")

_clients: set[WebSocket] = set()


async def _broadcast(envelope: dict) -> None:
    dead: list[WebSocket] = []
    for ws in _clients:
        try:
            await ws.send_json(envelope)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _clients.discard(ws)


# Subscribe bus → broadcast on startup
_unsub = bus.on_all(_broadcast)


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    _clients.add(ws)
    logger.info("WS client connected (%d total)", len(_clients))
    try:
        while True:
            data = await ws.receive_text()
            # Clients can send messages too (future: commands)
            try:
                msg = json.loads(data)
                await bus.emit(msg)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        _clients.discard(ws)
        logger.info("WS client disconnected (%d remaining)", len(_clients))
