"""Tool registry — agents discover tools by name."""

from __future__ import annotations

from typing import Any, Callable, Awaitable

ToolFn = Callable[..., Awaitable[str]]

_tools: dict[str, dict[str, Any]] = {}


def tool(name: str, description: str = ""):
    """Decorator to register an agent tool."""
    def decorator(fn: ToolFn) -> ToolFn:
        _tools[name] = {
            "name": name,
            "description": description,
            "fn": fn,
        }
        return fn
    return decorator


def get_tool(name: str) -> dict[str, Any] | None:
    return _tools.get(name)


async def call_tool(name: str, args: dict[str, Any]) -> str:
    """Call registered tool by name. Returns result string."""
    entry = _tools.get(name)
    if not entry:
        return f"[error] tool '{name}' not found"
    try:
        return await entry["fn"](**args)
    except Exception as e:
        return f"[error] {e}"


def list_tools() -> list[dict[str, str]]:
    return [{"name": t["name"], "description": t["description"]} for t in _tools.values()]


def tool_schemas() -> list[dict[str, Any]]:
    """Return tool definitions for LLM function calling."""
    schemas = []
    for t in _tools.values():
        fn = t["fn"]
        import inspect
        params = {}
        sig = inspect.signature(fn)
        for pname, p in sig.parameters.items():
            params[pname] = {"type": "string", "description": pname}
        schemas.append({
            "name": t["name"],
            "description": t["description"],
            "parameters": {"type": "object", "properties": params},
        })
    return schemas
