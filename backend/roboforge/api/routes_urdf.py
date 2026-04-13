"""URDF routes — parse, validate, serve."""

from __future__ import annotations

from fastapi import APIRouter, Body

from roboforge.urdf.parser import parse_urdf
from roboforge.urdf.validate import validate_urdf

router = APIRouter(prefix="/urdf", tags=["urdf"])


@router.post("/parse")
async def api_parse(path: str = Body(None, embed=True), xml: str = Body(None, embed=True)):
    source = path or xml
    if not source:
        return {"error": "provide 'path' or 'xml'"}
    model = parse_urdf(source)
    if model.error:
        return {"error": model.error}
    return model.to_dict()


@router.post("/validate")
async def api_validate(path: str = Body(None, embed=True), xml: str = Body(None, embed=True)):
    source = path or xml
    if not source:
        return {"error": "provide 'path' or 'xml'"}
    model = parse_urdf(source)
    result = validate_urdf(model)
    return {"valid": result.valid, "errors": result.errors, "warnings": result.warnings}
