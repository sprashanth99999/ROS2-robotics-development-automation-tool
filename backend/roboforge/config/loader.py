"""Load, validate, and persist .roboforge/config.yaml.

First-run creates the file from defaults. Subsequent runs merge saved YAML
with the schema defaults so new fields get populated automatically.
"""

from __future__ import annotations

import yaml

from roboforge.config.paths import config_file, ensure_dirs
from roboforge.config.schema import AppConfig

# Module-level singleton — initialised by load_config()
_config: AppConfig | None = None


def load_config() -> AppConfig:
    """Read config.yaml (or create defaults) and return a validated AppConfig."""
    global _config  # noqa: PLW0603

    ensure_dirs()
    path = config_file()

    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _config = AppConfig.model_validate(raw)
    else:
        _config = AppConfig()
        save_config(_config)

    return _config


def save_config(cfg: AppConfig) -> None:
    """Write AppConfig to config.yaml (pretty YAML)."""
    path = config_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = cfg.model_dump(mode="json")
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")


def get_config() -> AppConfig:
    """Return the loaded config singleton. Raises if load_config() hasn't been called."""
    if _config is None:
        return load_config()
    return _config
