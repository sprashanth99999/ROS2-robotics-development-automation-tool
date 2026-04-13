"""ROS2 environment management — source setup, env vars."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from roboforge.ros2.detector import detect_ros2, DISTRO_PATHS
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


def get_ros2_env(distro: str = "humble") -> dict[str, str]:
    """Get env vars after sourcing ROS2 setup.bash."""
    setup = f"/opt/ros/{distro}/setup.bash"
    if not Path(setup).exists():
        return {}
    try:
        cmd = f"bash -c 'source {setup} && env'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        env = {}
        for line in result.stdout.splitlines():
            k, _, v = line.partition("=")
            if k:
                env[k] = v
        return env
    except Exception as e:
        log.warning("Failed to source ROS2 env: %s", e)
        return {}


def source_ros2(distro: str = "humble") -> bool:
    """Inject ROS2 env vars into current process."""
    env = get_ros2_env(distro)
    if not env:
        return False
    for key in ("AMENT_PREFIX_PATH", "CMAKE_PREFIX_PATH", "COLCON_PREFIX_PATH",
                "LD_LIBRARY_PATH", "PATH", "PYTHONPATH", "ROS_DISTRO", "ROS_VERSION"):
        if key in env:
            os.environ[key] = env[key]
    log.info("Sourced ROS2 %s env (%d vars)", distro, len(env))
    return True


def get_workspace_env(ws_path: str, distro: str = "humble") -> dict[str, str]:
    """Get env after sourcing workspace setup.bash."""
    setup = Path(ws_path) / "install" / "setup.bash"
    ros_setup = f"/opt/ros/{distro}/setup.bash"
    if not setup.exists():
        return {}
    try:
        cmd = f"bash -c 'source {ros_setup} 2>/dev/null; source {setup} && env'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        env = {}
        for line in result.stdout.splitlines():
            k, _, v = line.partition("=")
            if k:
                env[k] = v
        return env
    except Exception:
        return {}
