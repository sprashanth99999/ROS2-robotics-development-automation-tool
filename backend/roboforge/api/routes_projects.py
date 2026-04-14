"""Project CRUD routes."""

from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from roboforge.projects.manager import (
    list_projects, get_project, create_project, delete_project, update_project,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
async def api_list():
    return [p.to_dict() for p in list_projects()]


@router.get("/{project_id}")
async def api_get(project_id: str):
    p = get_project(project_id)
    if not p:
        return JSONResponse({"error": "not found"}, 404)
    return p.to_dict()


@router.post("")
async def api_create(
    name: str = Body(..., embed=True),
    template: str = Body("empty", embed=True),
    ros2_distro: str = Body("humble", embed=True),
):
    p = create_project(name, template, ros2_distro)
    return p.to_dict()


@router.delete("/{project_id}")
async def api_delete(project_id: str):
    ok = delete_project(project_id)
    if not ok:
        return JSONResponse({"error": "not found"}, 404)
    return {"deleted": True}


@router.patch("/{project_id}")
async def api_update(project_id: str, name: str = Body(None, embed=True),
                     urdf_path: str = Body(None, embed=True)):
    kwargs = {}
    if name:
        kwargs["name"] = name
    if urdf_path:
        kwargs["urdf_path"] = urdf_path
    p = update_project(project_id, **kwargs)
    if not p:
        return JSONResponse({"error": "not found"}, 404)
    return p.to_dict()
