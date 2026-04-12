"""Shared exception hierarchy for the RoboForge backend.

All custom exceptions inherit from RoboForgeError so callers can catch a
single base class. FastAPI exception handlers (registered in main.py) map
these to appropriate HTTP responses.
"""

from __future__ import annotations


class RoboForgeError(Exception):
    """Base for all RoboForge-specific errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.code = code


class ConfigError(RoboForgeError):
    """Invalid or missing configuration."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIG_ERROR")


class ProviderError(RoboForgeError):
    """AI provider call failed (auth, rate limit, network)."""

    def __init__(self, message: str, provider: str = "unknown") -> None:
        super().__init__(message, code="PROVIDER_ERROR")
        self.provider = provider


class Ros2Error(RoboForgeError):
    """ROS2 environment or runtime error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="ROS2_ERROR")


class AgentError(RoboForgeError):
    """Agent execution error (tool failure, loop timeout)."""

    def __init__(self, message: str, agent_role: str = "unknown") -> None:
        super().__init__(message, code="AGENT_ERROR")
        self.agent_role = agent_role


class ProjectError(RoboForgeError):
    """Project CRUD or template error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="PROJECT_ERROR")
