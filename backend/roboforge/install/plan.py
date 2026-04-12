"""Install plan generator — produces steps for ROS2 installation."""

from __future__ import annotations

from dataclasses import dataclass, field

from roboforge.utils.os_detect import OSInfo


@dataclass
class InstallStep:
    id: str
    name: str
    command: str
    description: str
    sudo: bool = False
    optional: bool = False
    check: str | None = None  # command to verify step done


@dataclass
class InstallPlan:
    os: OSInfo
    distro: str = "humble"
    steps: list[InstallStep] = field(default_factory=list)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.steps)

    def to_dict(self) -> dict:
        return {
            "distro": self.distro,
            "os": self.os.distro,
            "os_version": self.os.version,
            "total_steps": self.total,
            "error": self.error,
            "warnings": self.warnings,
            "steps": [
                {"id": s.id, "name": s.name, "command": s.command,
                 "description": s.description, "sudo": s.sudo, "optional": s.optional}
                for s in self.steps
            ],
        }


def generate_plan(os_info: OSInfo, distro: str = "humble") -> InstallPlan:
    """Generate install plan based on OS."""
    plan = InstallPlan(os=os_info, distro=distro)

    if not os_info.is_linux:
        if os_info.system == "Windows":
            plan.warnings.append("ROS2 on Windows requires WSL2. Install WSL2 first.")
            plan.steps.append(InstallStep(
                id="wsl", name="Install WSL2",
                command="wsl --install -d Ubuntu-22.04",
                description="Install Windows Subsystem for Linux with Ubuntu 22.04",
            ))
            return plan
        plan.error = f"Unsupported OS: {os_info.distro}"
        return plan

    if os_info.distro != "ubuntu":
        plan.error = f"Only Ubuntu supported. Detected: {os_info.distro}"
        return plan

    if os_info.version not in ("22.04", "24.04"):
        plan.warnings.append(f"Ubuntu {os_info.version} not officially supported. Proceeding anyway.")

    # Ubuntu install steps
    plan.steps = [
        InstallStep(
            id="locale", name="Set locale",
            command="sudo locale-gen en_US en_US.UTF-8 && sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8",
            description="Ensure UTF-8 locale", sudo=True,
            check="locale | grep -q UTF-8",
        ),
        InstallStep(
            id="universe", name="Enable universe repo",
            command="sudo apt install -y software-properties-common && sudo add-apt-repository universe -y",
            description="Add Ubuntu universe repository", sudo=True,
        ),
        InstallStep(
            id="gpg", name="Add ROS2 GPG key",
            command="sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg",
            description="Download and install ROS2 GPG key", sudo=True,
        ),
        InstallStep(
            id="repo", name="Add ROS2 apt repo",
            command=f'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list',
            description="Add ROS2 package repository", sudo=True,
        ),
        InstallStep(
            id="update", name="apt update",
            command="sudo apt update",
            description="Refresh package index", sudo=True,
        ),
        InstallStep(
            id="install", name=f"Install ROS2 {distro}",
            command=f"sudo apt install -y ros-{distro}-desktop",
            description=f"Install ROS2 {distro} desktop (full)", sudo=True,
            check=f"dpkg -l | grep -q ros-{distro}-desktop",
        ),
        InstallStep(
            id="colcon", name="Install colcon",
            command="sudo apt install -y python3-colcon-common-extensions",
            description="Install colcon build tool", sudo=True,
        ),
        InstallStep(
            id="rosdep", name="Init rosdep",
            command="sudo rosdep init && rosdep update",
            description="Initialize rosdep dependency manager", sudo=True,
            check="rosdep --version",
        ),
        InstallStep(
            id="source", name="Source setup",
            command=f'echo "source /opt/ros/{distro}/setup.bash" >> ~/.bashrc',
            description=f"Auto-source ROS2 {distro} on shell start",
            check=f"grep -q 'ros/{distro}/setup.bash' ~/.bashrc",
        ),
    ]

    return plan
