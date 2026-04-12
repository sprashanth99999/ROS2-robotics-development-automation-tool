"""Google Gemini provider — streaming via generateContent API."""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from roboforge.providers.base import Message, Provider, ProviderConfig, StreamChunk
from roboforge.providers.registry import register

GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models"


@register
class GeminiProvider(Provider):
    name = "gemini"
    default_model = "gemini-2.5-flash"

    async def stream(self, messages: list[Message]) -> AsyncIterator[StreamChunk]:
        model = self.config.model or self.default_model
        url = f"{GEMINI_API}/{model}:streamGenerateContent?alt=sse&key={self.config.api_key}"
        contents = []
        for m in messages:
            role = "model" if m.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        body = {"contents": contents, "generationConfig": {"maxOutputTokens": self.config.max_tokens, "temperature": self.config.temperature}}

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", url, json=body) as resp:
                if resp.status_code != 200:
                    yield StreamChunk(text=f"[Gemini error {resp.status_code}]", finish_reason="error")
                    return
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        d = json.loads(line[6:])
                        text = d["candidates"][0]["content"]["parts"][0].get("text", "")
                        fr = d["candidates"][0].get("finishReason")
                        yield StreamChunk(text=text, finish_reason=fr)
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
