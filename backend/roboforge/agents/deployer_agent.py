"""Deployer agent — packages and deploys ROS2 workspaces."""

from __future__ import annotations

from roboforge.agents.loop import LoopAgent


class DeployerAgent(LoopAgent):
    role = "deployer"
    system_prompt = (
        "You are a deployment agent for ROS2 projects. "
        "Help package workspaces for deployment: Dockerfile generation, "
        "cross-compilation setup, rosdep resolution, colcon build optimization. "
        "Use run_command to execute build/deploy steps. "
        "Use write_file to create Dockerfiles, launch configs, systemd units."
    )
    max_steps = 12
