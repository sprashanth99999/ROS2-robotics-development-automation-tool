"""Uvicorn runner with automatic free-port discovery.

Called by __main__.py (python -m roboforge) and by Electron's
backend-process.ts which reads the port from stdout.
"""

from __future__ import annotations

import argparse
import socket
import sys

import uvicorn

from roboforge.config.loader import load_config


def find_free_port() -> int:
    """Bind to port 0 and let the OS assign a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run() -> None:
    """Parse CLI args and start uvicorn."""
    parser = argparse.ArgumentParser(description="RoboForge AI backend")
    parser.add_argument("--port", type=int, default=None, help="Port (0 = auto)")
    parser.add_argument("--host", type=str, default=None)
    args = parser.parse_args()

    cfg = load_config()

    host = args.host or cfg.server.host
    port = args.port if args.port is not None else cfg.server.port
    if port == 0:
        port = find_free_port()

    # Print the chosen port so Electron's backend-process.ts can parse it.
    # Format: ROBOFORGE_PORT=<port>
    print(f"ROBOFORGE_PORT={port}", flush=True)
    sys.stdout.flush()

    uvicorn.run(
        "roboforge.main:create_app",
        factory=True,
        host=host,
        port=port,
        log_level="info",
    )
