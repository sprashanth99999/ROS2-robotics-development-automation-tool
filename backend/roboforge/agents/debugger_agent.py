"""Debugger agent — diagnoses runtime errors and crashes."""

from __future__ import annotations

from roboforge.agents.loop import LoopAgent


class DebuggerAgent(LoopAgent):
    role = "debugger"
    system_prompt = (
        "You are a debugging agent for ROS2 systems. "
        "Diagnose crashes, unexpected behavior, and runtime errors. "
        "Use run_command to check logs, ros2 topic echo, node info. "
        "Use read_file to examine crash-related source code. "
        "Provide root cause analysis and fix suggestions."
    )
    max_steps = 12
