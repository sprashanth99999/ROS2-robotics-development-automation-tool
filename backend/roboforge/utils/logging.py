"""Centralized logging setup for the RoboForge backend.

Call setup_logging() once at startup. All modules use:
    from roboforge.utils.logging import get_logger
    logger = get_logger(__name__)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_INITIALISED = False


def setup_logging(log_dir: Path | None = None, level: int = logging.INFO) -> None:
    """Configure root logger with console + optional file handler."""
    global _INITIALISED  # noqa: PLW0603
    if _INITIALISED:
        return

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    root = logging.getLogger("roboforge")
    root.setLevel(level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    root.addHandler(console)

    # File handler (if log_dir provided)
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_dir / "roboforge.log", encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)

    _INITIALISED = True


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the roboforge namespace."""
    return logging.getLogger(f"roboforge.{name}")
