"""Planner agent — breaks tasks into steps before execution."""

from __future__ import annotations

from roboforge.agents.loop import LoopAgent


class PlannerAgent(LoopAgent):
    role = "planner"
    system_prompt = (
        "You are a planning agent for ROS2 robotics development. "
        "Break the user's request into numbered steps. "
        "Use tools to gather info, then produce a concrete plan. "
        "Final answer = numbered action list with file paths and commands."
    )
    max_steps = 8
