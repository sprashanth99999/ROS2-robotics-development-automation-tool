"""Provider listing and key management endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from roboforge.keychain.service import secrets
from roboforge.providers.registry import list_providers

router = APIRouter(prefix="/providers", tags=["providers"])


class SetKeyRequest(BaseModel):
    provider: str
    api_key: str


@router.get("")
async def get_providers():
    registered = list_providers()
    with_keys = secrets.list_providers_with_keys()
    return [{"name": p, "has_key": p in with_keys} for p in registered]


@router.post("/key")
async def set_key(req: SetKeyRequest):
    secrets.set_provider_key(req.provider, req.api_key)
    return {"ok": True}


@router.delete("/key/{provider}")
async def delete_key(provider: str):
    secrets.delete_provider_key(provider)
    return {"ok": True}
