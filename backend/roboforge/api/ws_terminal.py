"""WebSocket PTY bridge — spawns shell, pipes stdin/stdout over WS."""

from __future__ import annotations

import asyncio
import os
import platform

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from roboforge.utils.logging import get_logger

log = get_logger(__name__)
router = APIRouter()

SHELL = "bash" if platform.system() != "Windows" else "cmd.exe"


@router.websocket("/ws/terminal")
async def terminal_ws(ws: WebSocket):
    await ws.accept()
    log.info("Terminal WS connected")

    proc = await asyncio.create_subprocess_exec(
        SHELL,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={**os.environ},
    )

    async def read_output():
        try:
            while True:
                data = await proc.stdout.read(4096)
                if not data:
                    break
                await ws.send_text(data.decode(errors="replace"))
        except Exception:
            pass

    reader_task = asyncio.create_task(read_output())

    try:
        while True:
            text = await ws.receive_text()
            if proc.stdin:
                proc.stdin.write(text.encode())
                await proc.stdin.drain()
    except WebSocketDisconnect:
        log.info("Terminal WS disconnected")
    finally:
        reader_task.cancel()
        try:
            proc.terminate()
        except ProcessLookupError:
            pass
