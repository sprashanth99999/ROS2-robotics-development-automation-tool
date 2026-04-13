"""ROS2 routes — detect, launch, build, rosbridge."""

from __future__ import annotations

from fastapi import APIRouter, Body, Query
from fastapi.responses import StreamingResponse

from roboforge.ros2.detector import detect_ros2
from roboforge.ros2.env import source_ros2
from roboforge.ros2.launcher import launch_node, launch_file, stop_node, list_running
from roboforge.ros2.colcon import build, build_stream
from roboforge.ros2.rosdep import check_deps, install_deps
from roboforge.ros2.rosbridge import bridge

router = APIRouter(prefix="/ros2", tags=["ros2"])


@router.get("/status")
async def status():
    det = detect_ros2()
    return {
        "installed": det.installed, "distro": det.distro,
        "path": det.path, "rosbridge": bridge.connected,
        "running_nodes": list_running(),
    }


@router.post("/source")
async def source(distro: str = Body("humble", embed=True)):
    ok = source_ros2(distro)
    return {"sourced": ok, "distro": distro}


@router.post("/launch/node")
async def api_launch_node(
    package: str = Body(..., embed=True),
    executable: str = Body(..., embed=True),
):
    r = await launch_node(package, executable)
    return {"pid": r.pid, "name": r.name, "error": r.error}


@router.post("/launch/file")
async def api_launch_file(
    package: str = Body(..., embed=True),
    launch_file: str = Body(..., embed=True),
):
    r = await launch_file(package, launch_file)
    return {"pid": r.pid, "name": r.name, "error": r.error}


@router.post("/stop")
async def api_stop(name: str = Body(..., embed=True)):
    ok = await stop_node(name)
    return {"stopped": ok, "name": name}


@router.get("/running")
async def running():
    return list_running()


@router.post("/build")
async def api_build(workspace: str = Body(..., embed=True),
                    packages: list[str] | None = Body(None, embed=True)):
    r = await build(workspace, packages)
    return {"success": r.success, "output": r.output[-2000:]}


@router.post("/rosdep/check")
async def api_rosdep_check(workspace: str = Body(..., embed=True)):
    r = await check_deps(workspace)
    return {"success": r.success, "missing": r.missing, "output": r.output[-1000:]}


@router.post("/rosdep/install")
async def api_rosdep_install(workspace: str = Body(..., embed=True)):
    r = await install_deps(workspace)
    return {"success": r.success, "output": r.output[-1000:]}


@router.post("/rosbridge/connect")
async def api_bridge_connect(url: str = Body("ws://localhost:9090", embed=True)):
    ok = await bridge.connect()
    return {"connected": ok, "url": url}


@router.post("/rosbridge/disconnect")
async def api_bridge_disconnect():
    await bridge.disconnect()
    return {"disconnected": True}
