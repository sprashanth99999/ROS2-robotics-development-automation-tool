"""OS detection utility."""

from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass


@dataclass
class OSInfo:
    system: str  # Linux, Windows, Darwin
    distro: str  # ubuntu, fedora, windows, macos, unknown
    version: str  # 22.04, 11, 14.0
    arch: str  # x86_64, aarch64
    wsl: bool = False

    @property
    def is_linux(self) -> bool:
        return self.system == "Linux"

    @property
    def supported_ros2(self) -> bool:
        return self.distro in ("ubuntu",) and self.version in ("22.04", "24.04")


def detect_os() -> OSInfo:
    system = platform.system()
    arch = platform.machine()
    distro = "unknown"
    version = platform.version()
    wsl = False

    if system == "Linux":
        try:
            with open("/etc/os-release") as f:
                lines = {k: v.strip('"') for line in f for k, _, v in [line.strip().partition("=")]}
            distro = lines.get("ID", "unknown")
            version = lines.get("VERSION_ID", "")
        except FileNotFoundError:
            pass
        # WSL check
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    wsl = True
        except FileNotFoundError:
            pass
    elif system == "Windows":
        distro = "windows"
        version = platform.version()
    elif system == "Darwin":
        distro = "macos"
        version = platform.mac_ver()[0]

    return OSInfo(system=system, distro=distro, version=version, arch=arch, wsl=wsl)
