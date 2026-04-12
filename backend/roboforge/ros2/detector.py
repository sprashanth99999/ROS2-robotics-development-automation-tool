"""ROS2 installation detector."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Ros2Detection:
    installed: bool = False
    distro: str | None = None
    setup_bash: str | None = None
    version: str | None = None
    path: str | None = None

    @property
    def summary(self) -> str:
        if not self.installed:
            return "ROS2 not detected"
        return f"ROS2 {self.distro} at {self.path}"


# Known ROS2 distro paths (Linux)
DISTRO_PATHS = {
    "humble": "/opt/ros/humble",
    "iron": "/opt/ros/iron",
    "jazzy": "/opt/ros/jazzy",
    "rolling": "/opt/ros/rolling",
}


def detect_ros2() -> Ros2Detection:
    """Check if ROS2 is installed. Tries env vars then known paths."""
    # Check AMENT_PREFIX_PATH (set after sourcing setup.bash)
    ament = os.environ.get("AMENT_PREFIX_PATH", "")
    if ament:
        for distro, prefix in DISTRO_PATHS.items():
            if prefix in ament:
                setup = f"{prefix}/setup.bash"
                return Ros2Detection(
                    installed=True, distro=distro,
                    setup_bash=setup if Path(setup).exists() else None,
                    path=prefix,
                )

    # Check ROS_DISTRO env
    ros_distro = os.environ.get("ROS_DISTRO")
    if ros_distro and ros_distro in DISTRO_PATHS:
        prefix = DISTRO_PATHS[ros_distro]
        return Ros2Detection(
            installed=True, distro=ros_distro,
            setup_bash=f"{prefix}/setup.bash",
            path=prefix,
        )

    # Scan known paths
    for distro, prefix in DISTRO_PATHS.items():
        setup = Path(prefix) / "setup.bash"
        if setup.exists():
            return Ros2Detection(
                installed=True, distro=distro,
                setup_bash=str(setup), path=prefix,
            )

    # Check if ros2 binary exists
    ros2_bin = shutil.which("ros2")
    if ros2_bin:
        return Ros2Detection(installed=True, path=str(Path(ros2_bin).parent))

    return Ros2Detection()
