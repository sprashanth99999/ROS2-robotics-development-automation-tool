"""SSE streaming chat endpoint — POST /chat."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from roboforge.providers.auth import resolve_api_key
from roboforge.providers.base import Message, ProviderConfig
from roboforge.providers.registry import get_provider_class

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    provider: str = "claude"
    model: str | None = None
    messages: list[dict]
    temperature: float = 0.7
    max_tokens: int = 4096


@router.post("/chat")
async def chat(req: ChatRequest):
    cls = get_provider_class(req.provider)
    if not cls:
        raise HTTPException(404, f"Unknown provider: {req.provider}")

    api_key = resolve_api_key(req.provider)
    if not api_key:
        raise HTTPException(401, f"No API key for {req.provider}")

    config = ProviderConfig(
        api_key=api_key,
        model=req.model or "",
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )
    provider = cls(config)
    msgs = [Message(role=m["role"], content=m["content"]) for m in req.messages]

    async def generate():
        async for chunk in provider.stream(msgs):
            data = json.dumps({"text": chunk.text, "finish_reason": chunk.finish_reason})
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
