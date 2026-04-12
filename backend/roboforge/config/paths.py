"""Resolve canonical filesystem paths for .roboforge/ and project resources.

All runtime data lives under ~/.roboforge/ (or ROBOFORGE_HOME if set).
This module is the single source of truth for every path the backend uses.
"""

from __future__ import annotations

import os
from pathlib import Path

# Override with ROBOFORGE_HOME env var for dev / testing
_HOME_ENV = "ROBOFORGE_HOME"


def roboforge_home() -> Path:
    """Root of the runtime config dir — defaults to ~/.roboforge."""
    if custom := os.environ.get(_HOME_ENV):
        return Path(custom).expanduser().resolve()
    return Path.home() / ".roboforge"


def ensure_dirs() -> Path:
    """Create the .roboforge/ tree if it doesn't exist. Returns the root."""
    root = roboforge_home()
    for sub in (
        "projects",
        "models",
        "templates",
        "logs",
        "ros2_ws",
        "sim_links",
        "migrations",
    ):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def config_file() -> Path:
    return roboforge_home() / "config.yaml"


def db_file() -> Path:
    return roboforge_home() / "db.sqlite"


def logs_dir() -> Path:
    return roboforge_home() / "logs"


def projects_dir() -> Path:
    return roboforge_home() / "projects"


def models_dir() -> Path:
    return roboforge_home() / "models"


def ros2_ws_dir() -> Path:
    return roboforge_home() / "ros2_ws"


def shared_py_path() -> Path:
    """Path to shared/py/ so backend can import generated pydantic models."""
    return Path(__file__).resolve().parents[3] / "shared" / "py"
