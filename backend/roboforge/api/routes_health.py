"""Health-check endpoint — always the first route registered.

GET /health  → 200 with system status summary.
Used by Electron to confirm the backend is alive before showing the UI.
"""

from __future__ import annotations

import platform
import sys

from fastapi import APIRouter, Depends

from roboforge import __version__
from roboforge.api.deps import get_app_config
from roboforge.config.schema import AppConfig

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(config: AppConfig = Depends(get_app_config)) -> dict:
    return {
        "status": "ok",
        "version": __version__,
        "python": sys.version,
        "platform": platform.system(),
        "ros2_distro": config.ros2.distro,
        "ai_default_provider": config.ai.default_provider,
    }
