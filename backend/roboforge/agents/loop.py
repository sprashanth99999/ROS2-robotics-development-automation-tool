"""Core agent loop — ReAct-style think→act→observe."""

from __future__ import annotations

import json
from typing import Any

from roboforge.providers.base import Message, ProviderConfig
from roboforge.providers.registry import get_provider_class
from roboforge.providers.auth import resolve_api_key
from roboforge.agents.base import Agent, AgentResult, AgentStep, ToolCall
from roboforge.agents.tools.registry import call_tool, tool_schemas
from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)

# Import tool modules so @tool decorators register
import roboforge.agents.tools.fs_tools  # noqa: F401
import roboforge.agents.tools.terminal_tools  # noqa: F401
import roboforge.agents.tools.provider_tools  # noqa: F401

TOOL_CALL_TAG = "TOOL_CALL:"
SYSTEM_SUFFIX = """
You have tools. To use one, respond EXACTLY:
TOOL_CALL: {"name": "<tool>", "args": {<args>}}

After seeing the result, continue reasoning. When done, give final answer without TOOL_CALL.

Available tools:
{tools}
"""


class LoopAgent(Agent):
    """Generic ReAct agent. Subclasses override role + system_prompt."""

    role = "loop"
    provider_name: str = "claude"

    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResult:
        result = AgentResult()
        provider_name = (context or {}).get("provider", self.provider_name)

        cls = get_provider_class(provider_name)
        if not cls:
            result.error = f"provider '{provider_name}' not found"
            return result

        key = resolve_api_key(provider_name)
        cfg = ProviderConfig(api_key=key, model=cls.default_model)
        provider = cls(cfg)

        tools_desc = json.dumps(tool_schemas(), indent=2)
        system = self.system_prompt + SYSTEM_SUFFIX.format(tools=tools_desc)

        messages: list[Message] = [
            Message(role="system", content=system),
            Message(role="user", content=user_input),
        ]

        for step_num in range(self.max_steps):
            resp = await provider.complete(messages)
            text = resp.content.strip()

            step = AgentStep(thought=text)
            bus.emit("agent:step", {
                "agent": self.role, "step": step_num, "thought": text[:200],
            })

            if TOOL_CALL_TAG in text:
                # Extract tool call JSON
                idx = text.index(TOOL_CALL_TAG) + len(TOOL_CALL_TAG)
                try:
                    call_data = json.loads(text[idx:].strip())
                    tc = ToolCall(name=call_data["name"], args=call_data.get("args", {}))
                    step.tool_call = tc

                    bus.emit("agent:tool_call", {
                        "agent": self.role, "tool": tc.name, "args": tc.args,
                    })

                    tc.result = await call_tool(tc.name, tc.args)
                    messages.append(Message(role="assistant", content=text))
                    messages.append(Message(role="user", content=f"Tool result:\n{tc.result}"))
                except (json.JSONDecodeError, KeyError) as e:
                    tc = ToolCall(name="parse_error", error=str(e))
                    step.tool_call = tc
                    messages.append(Message(role="assistant", content=text))
                    messages.append(Message(role="user", content=f"[error parsing tool call: {e}]"))
            else:
                step.response = text
                result.steps.append(step)
                result.final_answer = text
                bus.emit("agent:done", {"agent": self.role, "answer": text[:500]})
                return result

            result.steps.append(step)

        result.error = f"max steps ({self.max_steps}) reached"
        result.final_answer = result.steps[-1].thought if result.steps else ""
        return result
