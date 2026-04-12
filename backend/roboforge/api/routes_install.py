"""Install routes — plan + SSE runner."""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from roboforge.install.plan import generate_plan
from roboforge.install.runner import run_plan
from roboforge.ros2.detector import detect_ros2
from roboforge.utils.os_detect import detect_os, OSInfo

router = APIRouter(prefix="/install", tags=["install"])


def _mock_os(os_name: str) -> OSInfo:
    """Create mock OSInfo for plan preview."""
    mocks = {
        "ubuntu22": OSInfo(system="Linux", distro="ubuntu", version="22.04", arch="x86_64"),
        "ubuntu24": OSInfo(system="Linux", distro="ubuntu", version="24.04", arch="x86_64"),
        "windows": OSInfo(system="Windows", distro="windows", version="11", arch="x86_64"),
    }
    return mocks.get(os_name, detect_os())


@router.get("/detect")
async def detect():
    """Detect current OS and ROS2 installation."""
    os_info = detect_os()
    ros2 = detect_ros2()
    return {
        "os": {"system": os_info.system, "distro": os_info.distro,
               "version": os_info.version, "arch": os_info.arch, "wsl": os_info.wsl},
        "ros2": {"installed": ros2.installed, "distro": ros2.distro,
                 "path": ros2.path, "summary": ros2.summary},
    }


@router.get("/plan")
async def get_plan(
    os: str = Query(None, description="Mock OS: ubuntu22, ubuntu24, windows"),
    distro: str = Query("humble", description="ROS2 distro"),
):
    """Generate install plan (preview only, no execution)."""
    os_info = _mock_os(os) if os else detect_os()
    plan = generate_plan(os_info, distro=distro)
    return plan.to_dict()


@router.post("/run")
async def run_install(
    os: str = Query(None),
    distro: str = Query("humble"),
    dry_run: bool = Query(True),
):
    """Execute install plan with SSE progress stream."""
    os_info = _mock_os(os) if os else detect_os()
    plan = generate_plan(os_info, distro=distro)

    if plan.error:
        return {"error": plan.error}

    return StreamingResponse(
        run_plan(plan, dry_run=dry_run),
        media_type="text/event-stream",
    )
