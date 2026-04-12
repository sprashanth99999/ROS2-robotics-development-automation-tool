"""Provider template — copy this file to create a new provider.

Replace PROVIDER_NAME, DEFAULT_MODEL, API_URL, and implement stream().
"""

from __future__ import annotations

from typing import AsyncIterator

from roboforge.providers.base import Message, Provider, ProviderConfig, StreamChunk
from roboforge.providers.registry import register


# @register  # uncomment when ready
class TemplateProvider(Provider):
    name = "PROVIDER_NAME"
    default_model = "DEFAULT_MODEL"

    async def stream(self, messages: list[Message]) -> AsyncIterator[StreamChunk]:
        raise NotImplementedError("Copy this template and implement stream()")
        yield  # type: ignore[misc]  # makes this a generator
