"""OpenAI (GPT-4) provider — streaming via Chat Completions API."""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from roboforge.providers.base import Message, Provider, ProviderConfig, StreamChunk
from roboforge.providers.registry import register

OPENAI_API = "https://api.openai.com/v1/chat/completions"


@register
class OpenAIProvider(Provider):
    name = "openai"
    default_model = "gpt-4o"

    async def stream(self, messages: list[Message]) -> AsyncIterator[StreamChunk]:
        model = self.config.model or self.default_model
        body = {
            "model": model,
            "stream": True,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        headers = {"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", OPENAI_API, json=body, headers=headers) as resp:
                if resp.status_code != 200:
                    yield StreamChunk(text=f"[OpenAI error {resp.status_code}]", finish_reason="error")
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
