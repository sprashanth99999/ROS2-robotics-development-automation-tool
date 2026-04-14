"""Simulator bridge ABC."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimStatus:
    connected: bool = False
    simulator: str = ""
    world: str = ""
    paused: bool = False
    sim_time: float = 0.0
    entities: list[str] = field(default_factory=list)


class SimBridge(ABC):
    """Base class for simulator bridges."""

    name: str = "base"

    @abstractmethod
    async def connect(self) -> bool: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def status(self) -> SimStatus: ...

    @abstractmethod
    async def spawn(self, model: str, name: str, position: list[float]) -> dict: ...

    @abstractmethod
    async def remove(self, name: str) -> bool: ...

    @abstractmethod
    async def pause(self) -> None: ...

    @abstractmethod
    async def resume(self) -> None: ...

    @abstractmethod
    async def reset(self) -> None: ...
