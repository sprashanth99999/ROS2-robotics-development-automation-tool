"""Agent execution routes."""

from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from roboforge.agents.planner import PlannerAgent
from roboforge.agents.setup_agent import SetupAgent

router = APIRouter(prefix="/agents", tags=["agents"])

AGENTS = {
    "planner": PlannerAgent,
    "setup": SetupAgent,
}


@router.post("/{agent_role}/run")
async def run_agent(
    agent_role: str,
    user_input: str = Body(..., embed=True),
    provider: str = Body("claude", embed=True),
):
    cls = AGENTS.get(agent_role)
    if not cls:
        return JSONResponse({"error": f"agent '{agent_role}' not found"}, 404)

    agent = cls()
    result = await agent.run(user_input, context={"provider": provider})

    return {
        "success": result.success,
        "final_answer": result.final_answer,
        "error": result.error,
        "steps": [
            {
                "thought": s.thought[:500],
                "tool_call": {
                    "name": s.tool_call.name,
                    "args": s.tool_call.args,
                    "result": (s.tool_call.result or "")[:2000],
                    "error": s.tool_call.error,
                } if s.tool_call else None,
                "response": s.response[:1000],
            }
            for s in result.steps
        ],
    }


@router.get("")
async def list_agents():
    return [{"role": k, "description": v.system_prompt[:100]} for k, v in AGENTS.items()]
