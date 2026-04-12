"""Provider registry — lookup by name, list available providers."""

from __future__ import annotations

from typing import Type

from roboforge.providers.base import Provider

_registry: dict[str, Type[Provider]] = {}


def register(cls: Type[Provider]) -> Type[Provider]:
    """Class decorator — registers a provider by its .name attribute."""
    _registry[cls.name] = cls
    return cls


def get_provider_class(name: str) -> Type[Provider] | None:
    return _registry.get(name)


def list_providers() -> list[str]:
    return list(_registry.keys())
