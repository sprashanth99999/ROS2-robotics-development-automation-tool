"""Coder agent — generates and modifies ROS2 code."""

from __future__ import annotations

from roboforge.agents.loop import LoopAgent


class CoderAgent(LoopAgent):
    role = "coder"
    system_prompt = (
        "You are a coding agent for ROS2 robotics. "
        "Generate, modify, and fix ROS2 Python/C++ code. "
        "Use read_file to understand existing code before editing. "
        "Use write_file to create or update files. "
        "Use run_command to test builds with colcon. "
        "Follow ROS2 conventions: package.xml, CMakeLists, setup.py."
    )
    max_steps = 15
