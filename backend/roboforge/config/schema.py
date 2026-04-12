"""Pydantic models for the global .roboforge/config.yaml file.

These models define every configurable setting. The loader (config/loader.py)
reads YAML, validates it through these models, and exposes typed access.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AiProviderConfig(BaseModel):
    """Per-provider settings (key stored separately in keychain)."""

    enabled: bool = True
    model: Optional[str] = None  # provider-specific default model override
    base_url: Optional[str] = None  # for Ollama / self-hosted endpoints


class AiConfig(BaseModel):
    """AI integration settings."""

    default_provider: Literal[
        "claude", "gemini", "openai", "mistral", "ollama"
    ] = "claude"
    providers: dict[str, AiProviderConfig] = Field(default_factory=dict)


class Ros2Config(BaseModel):
    """ROS2 environment settings."""

    distro: Literal["humble", "iron", "jazzy"] = "humble"
    setup_bash: Optional[str] = None  # path to setup.bash override
    workspace: Optional[str] = None  # colcon workspace root override


class SimConfig(BaseModel):
    """Simulation settings."""

    gazebo_version: Literal["classic", "harmonic", "fortress"] = "harmonic"
    isaac_sim_path: Optional[str] = None


class ServerConfig(BaseModel):
    """Backend server settings."""

    host: str = "127.0.0.1"
    port: int = 0  # 0 = auto-pick free port
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:*"])


class AppConfig(BaseModel):
    """Root configuration model — maps 1:1 to .roboforge/config.yaml."""

    version: int = 1  # schema version for future migrations
    server: ServerConfig = Field(default_factory=ServerConfig)
    ai: AiConfig = Field(default_factory=AiConfig)
    ros2: Ros2Config = Field(default_factory=Ros2Config)
    sim: SimConfig = Field(default_factory=SimConfig)
