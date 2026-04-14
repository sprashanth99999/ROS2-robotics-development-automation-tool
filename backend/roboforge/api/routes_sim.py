"""Simulation routes — Gazebo control."""

from __future__ import annotations

from fastapi import APIRouter, Body

from roboforge.sim.gazebo_modern import gazebo

router = APIRouter(prefix="/sim", tags=["sim"])


@router.get("/status")
async def sim_status():
    s = await gazebo.status()
    return {"connected": s.connected, "simulator": s.simulator,
            "world": s.world, "paused": s.paused, "entities": s.entities}


@router.post("/connect")
async def sim_connect():
    ok = await gazebo.connect()
    return {"connected": ok}


@router.post("/disconnect")
async def sim_disconnect():
    await gazebo.disconnect()
    return {"disconnected": True}


@router.post("/launch")
async def sim_launch(world_file: str = Body("", embed=True)):
    return await gazebo.launch_world(world_file)


@router.post("/spawn")
async def sim_spawn(
    model: str = Body(..., embed=True),
    name: str = Body(..., embed=True),
    position: list[float] = Body([0, 0, 0], embed=True),
):
    return await gazebo.spawn(model, name, position)


@router.post("/remove")
async def sim_remove(name: str = Body(..., embed=True)):
    ok = await gazebo.remove(name)
    return {"removed": ok, "name": name}


@router.post("/pause")
async def sim_pause():
    await gazebo.pause()
    return {"paused": True}


@router.post("/resume")
async def sim_resume():
    await gazebo.resume()
    return {"resumed": True}


@router.post("/reset")
async def sim_reset():
    await gazebo.reset()
    return {"reset": True}
