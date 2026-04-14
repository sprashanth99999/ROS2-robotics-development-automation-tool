"""Reviewer agent — reviews code for bugs, style, ROS2 best practices."""

from __future__ import annotations

from roboforge.agents.loop import LoopAgent


class ReviewerAgent(LoopAgent):
    role = "reviewer"
    system_prompt = (
        "You are a code review agent for ROS2 projects. "
        "Read code files and identify bugs, anti-patterns, missing error handling, "
        "thread safety issues, and ROS2 best practice violations. "
        "Use read_file to examine code. Use ask_ai for second opinion if unsure. "
        "Output structured review: severity (error/warning/info), line, message."
    )
    max_steps = 10
