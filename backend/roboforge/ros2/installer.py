"""ROS2 installer — wraps install plan with pre/post checks."""

from __future__ import annotations

from roboforge.install.plan import generate_plan, InstallPlan
from roboforge.install.runner import run_plan
from roboforge.ros2.detector import detect_ros2
from roboforge.utils.os_detect import detect_os, OSInfo
from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger
from typing import AsyncIterator

log = get_logger(__name__)


async def install_ros2(
    distro: str = "humble",
    os_info: OSInfo | None = None,
    dry_run: bool = True,
) -> AsyncIterator[str]:
    """Full ROS2 install flow: detect → plan → run → verify."""
    os_info = os_info or detect_os()

    # Pre-check
    existing = detect_ros2()
    if existing.installed and existing.distro == distro:
        bus.emit("install:skip", {"reason": f"ROS2 {distro} already installed"})
        yield f'data: {{"type":"skip","reason":"ROS2 {distro} already installed at {existing.path}"}}\n\n'
        yield "data: [DONE]\n\n"
        return

    # Generate plan
    plan = generate_plan(os_info, distro=distro)
    if plan.error:
        bus.emit("install:error", {"error": plan.error})
        yield f'data: {{"type":"error","error":"{plan.error}"}}\n\n'
        yield "data: [DONE]\n\n"
        return

    log.info("Starting ROS2 %s install (%d steps, dry_run=%s)", distro, plan.total, dry_run)
    bus.emit("install:start", {"distro": distro, "steps": plan.total, "dry_run": dry_run})

    # Run plan
    async for event in run_plan(plan, dry_run=dry_run):
        yield event

    # Post-check (only on real install)
    if not dry_run:
        post = detect_ros2()
        if post.installed:
            bus.emit("install:success", {"distro": post.distro, "path": post.path})
        else:
            bus.emit("install:warn", {"msg": "Install completed but ROS2 not detected. May need shell restart."})
