"""Auth routes — Google Sign-In config + token exchange + session."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from roboforge.auth import google

router = APIRouter(prefix="/auth", tags=["auth"])


class ClientIdRequest(BaseModel):
    client_id: str


class TokenRequest(BaseModel):
    id_token: str


@router.get("/config")
async def get_config():
    cid = google.get_client_id()
    return {"client_id": cid, "configured": bool(cid)}


@router.post("/config")
async def set_config(req: ClientIdRequest):
    google.set_client_id(req.client_id.strip())
    return {"ok": True}


@router.post("/google")
async def sign_in_google(req: TokenRequest):
    try:
        user = await google.verify_id_token(req.id_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    google.save_session(user)
    return {"ok": True, "user": {"email": user["email"], "name": user["name"], "picture": user["picture"]}}


@router.get("/me")
async def me():
    user = google.load_session()
    if not user:
        raise HTTPException(status_code=401, detail="Not signed in")
    return {"email": user["email"], "name": user["name"], "picture": user["picture"]}


@router.post("/logout")
async def logout():
    google.clear_session()
    return {"ok": True}
