"""Ollama provider — local models via OpenAI-compatible API."""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from roboforge.providers.base import Message, Provider, ProviderConfig, StreamChunk
from roboforge.providers.registry import register

DEFAULT_URL = "http://localhost:11434/v1/chat/completions"


@register
class OllamaProvider(Provider):
    name = "ollama"
    default_model = "llama3.2"

    async def stream(self, messages: list[Message]) -> AsyncIterator[StreamChunk]:
        model = self.config.model or self.default_model
        url = self.config.base_url or DEFAULT_URL
        body = {
            "model": model,
            "stream": True,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }

        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream("POST", url, json=body) as resp:
                if resp.status_code != 200:
                    yield StreamChunk(text=f"[Ollama error {resp.status_code}]", finish_reason="error")
                    return
                async for line in resp.aiter_lines():
                    if not line.startswith("data: ") or line == "data: [DONE]":
                        continue
                    try:
                        d = json.loads(line[6:])
                        delta = d["choices"][0].get("delta", {})
                        fr = d["choices"][0].get("finish_reason")
                        yield StreamChunk(text=delta.get("content", ""), finish_reason=fr)
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
