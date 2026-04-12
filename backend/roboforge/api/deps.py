"""FastAPI dependency-injection helpers.

Centralises config / service access so route handlers stay thin.
New dependencies are added here as modules come online in later phases.
"""

from __future__ import annotations

from roboforge.config.loader import get_config
from roboforge.config.schema import AppConfig


def get_app_config() -> AppConfig:
    """Return the validated global AppConfig (loaded once at startup)."""
    return get_config()
