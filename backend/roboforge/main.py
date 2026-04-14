"""FastAPI application factory.

create_app() builds the ASGI application with all routers, middleware,
exception handlers, and the startup/shutdown lifespan. Import this in
server.py (uvicorn entry) and in tests (via conftest.py).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from roboforge.api.routes_agents import router as agents_router
from roboforge.api.routes_chat import router as chat_router
from roboforge.api.routes_health import router as health_router
from roboforge.api.routes_install import router as install_router
from roboforge.api.routes_providers import router as providers_router
from roboforge.api.routes_ros2 import router as ros2_router
from roboforge.api.routes_urdf import router as urdf_router
from roboforge.api.routes_sim import router as sim_router
from roboforge.api.ws_terminal import router as terminal_router
from roboforge.sim.bridge_ws import router as sim_ws_router
from roboforge.api.ws_events import router as ws_router
import roboforge.providers.claude  # noqa: F401
import roboforge.providers.openai  # noqa: F401
import roboforge.providers.gemini  # noqa: F401
import roboforge.providers.mistral  # noqa: F401
import roboforge.providers.ollama  # noqa: F401
from roboforge.config.loader import load_config
from roboforge.config.paths import logs_dir
from roboforge.utils.errors import RoboForgeError
from roboforge.utils.logging import get_logger, setup_logging

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle."""
    cfg = load_config()
    setup_logging(log_dir=logs_dir())
    logger.info("RoboForge backend starting (port=%s)", cfg.server.port)
    yield
    logger.info("RoboForge backend shutting down")


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="RoboForge AI",
        version="0.0.1",
        lifespan=lifespan,
    )

    # --- CORS (Electron renderer connects from localhost) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tightened per-config in Phase 5
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception handler for all custom errors ---
    @app.exception_handler(RoboForgeError)
    async def roboforge_error_handler(request: Request, exc: RoboForgeError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": {"code": exc.code, "message": str(exc)}},
        )

    # --- Routers ---
    app.include_router(health_router)
    app.include_router(providers_router)
    app.include_router(chat_router)
    app.include_router(agents_router)
    app.include_router(install_router)
    app.include_router(ros2_router)
    app.include_router(urdf_router)
    app.include_router(sim_router)
    app.include_router(sim_ws_router)
    app.include_router(terminal_router)
    app.include_router(ws_router)

    return app
