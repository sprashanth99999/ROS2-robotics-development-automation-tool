"""Provider tools — let agents call AI providers."""

from __future__ import annotations

from roboforge.providers.base import Message, ProviderConfig
from roboforge.providers.registry import get_provider_class
from roboforge.providers.auth import resolve_api_key

from .registry import tool


@tool("ask_ai", "Ask an AI provider a question")
async def ask_ai(prompt: str, provider: str = "claude") -> str:
    cls = get_provider_class(provider)
    if not cls:
        return f"[error] provider '{provider}' not found"
    key = resolve_api_key(provider)
    cfg = ProviderConfig(api_key=key, model=cls.default_model)
    inst = cls(cfg)
    msgs = [Message(role="user", content=prompt)]
    resp = await inst.complete(msgs)
    return resp.content
