"""In-process async pub/sub event bus. Backend modules publish events,
WebSocket endpoint broadcasts them to connected Electron renderers."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine

Callback = Callable[[dict], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, set[Callback]] = defaultdict(set)
        self._wildcard: set[Callback] = set()

    def on(self, event_type: str, cb: Callback) -> Callable[[], None]:
        self._subs[event_type].add(cb)
        return lambda: self._subs[event_type].discard(cb)

    def on_all(self, cb: Callback) -> Callable[[], None]:
        self._wildcard.add(cb)
        return lambda: self._wildcard.discard(cb)

    async def emit(self, envelope: dict) -> None:
        event_type = envelope.get("type", "")
        coros = [cb(envelope) for cb in self._subs.get(event_type, set())]
        coros += [cb(envelope) for cb in self._wildcard]
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)


# Module singleton
bus = EventBus()
