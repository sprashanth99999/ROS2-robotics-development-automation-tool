"""AI provider abstract base — every provider implements this interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class Message:
    role: str  # system | user | assistant | tool
    content: str
    tool_calls: list[dict] | None = None
    tool_result_id: str | None = None


@dataclass
class StreamChunk:
    text: str = ""
    finish_reason: str | None = None
    tool_calls: list[dict] | None = None


@dataclass
class ProviderConfig:
    api_key: str = ""
    model: str = ""
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: list[dict] = field(default_factory=list)


class Provider(ABC):
    """Base class for all AI providers."""

    name: str = "base"
    default_model: str = ""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @abstractmethod
    async def stream(self, messages: list[Message]) -> AsyncIterator[StreamChunk]:
        """Stream response chunks. Must yield at least one chunk."""
        ...

    async def complete(self, messages: list[Message]) -> Message:
        """Non-streaming convenience — collects stream into single message."""
        parts: list[str] = []
        tool_calls = None
        async for chunk in self.stream(messages):
            parts.append(chunk.text)
            if chunk.tool_calls:
                tool_calls = chunk.tool_calls
        return Message(role="assistant", content="".join(parts), tool_calls=tool_calls)
