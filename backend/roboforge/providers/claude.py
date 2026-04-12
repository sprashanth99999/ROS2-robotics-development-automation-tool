"""Claude (Anthropic) provider — streaming via the Messages API."""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from roboforge.providers.base import Message, Provider, ProviderConfig, StreamChunk
from roboforge.providers.registry import register
from roboforge.utils.logging import get_logger

logger = get_logger("providers.claude")

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"


@register
class ClaudeProvider(Provider):
    name = "claude"
    default_model = "claude-sonnet-4-20250514"

    async def stream(self, messages: list[Message]) -> AsyncIterator[StreamChunk]:
        model = self.config.model or self.default_model
        # Separate system message from conversation
        system_text = ""
        conv: list[dict] = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
            else:
                conv.append({"role": m.role, "content": m.content})

        body: dict = {
            "model": model,
            "max_tokens": self.config.max_tokens,
            "stream": True,
            "messages": conv,
        }
        if system_text:
            body["system"] = system_text
        if self.config.tools:
            body["tools"] = self.config.tools

        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", ANTHROPIC_API, json=body, headers=headers) as resp:
                if resp.status_code != 200:
                    err = await resp.aread()
                    logger.error("Claude API %d: %s", resp.status_code, err.decode())
                    yield StreamChunk(text=f"[Claude API error {resp.status_code}]", finish_reason="error")
                    return

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        evt = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    evt_type = evt.get("type", "")
                    if evt_type == "content_block_delta":
                        delta = evt.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield StreamChunk(text=delta.get("text", ""))
                        elif delta.get("type") == "input_json_delta":
                            yield StreamChunk(text=delta.get("partial_json", ""))
                    elif evt_type == "message_delta":
                        yield StreamChunk(
                            finish_reason=evt.get("delta", {}).get("stop_reason", "end_turn")
                        )
