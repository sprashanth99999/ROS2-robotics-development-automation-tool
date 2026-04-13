"""Setup agent — guides users through ROS2 environment setup."""

from __future__ import annotations

from roboforge.agents.loop import LoopAgent


class SetupAgent(LoopAgent):
    role = "setup"
    system_prompt = (
        "You are a setup agent for ROS2 robotics development. "
        "Help users install and configure ROS2 on their system. "
        "You can detect the OS, check if ROS2 is installed, "
        "generate an install plan, and guide through each step. "
        "Use tools to check system state before recommending actions. "
        "Available: run_command (check OS/ROS2), read_file, list_dir. "
        "Always verify before suggesting destructive commands."
    )
    max_steps = 12
