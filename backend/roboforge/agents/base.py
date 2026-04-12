"""Agent ABC — all agent roles implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any] = field(default_factory=dict)
    result: str | None = None
    error: str | None = None


@dataclass
class AgentStep:
    thought: str = ""
    tool_call: ToolCall | None = None
    response: str = ""


@dataclass
class AgentResult:
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str = ""
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


class Agent(ABC):
    """Base agent. Subclasses set role + system prompt + allowed tools."""

    role: str = "base"
    system_prompt: str = "You are a helpful assistant."
    max_steps: int = 10

    @abstractmethod
    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResult:
        ...
