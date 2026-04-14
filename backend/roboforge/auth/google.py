"""Google Sign-In — verify ID token via Google tokeninfo endpoint.

Flow:
1. Frontend uses Google Identity Services, gets JWT ID token.
2. Frontend POSTs token to /auth/google.
3. Backend calls Google's tokeninfo endpoint to verify signature + aud.
4. Backend stores session {email, name, picture, exp} in session file.

No crypto libs needed — Google does the heavy lifting via tokeninfo.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from roboforge.config.paths import roboforge_home
from roboforge.keychain.service import secrets

AUTH_SERVICE = "auth"
CLIENT_ID_KEY = "google_client_id"
SESSION_FILE = "session.json"
TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def session_path() -> Path:
    return roboforge_home() / SESSION_FILE


def get_client_id() -> str | None:
    return secrets.get(AUTH_SERVICE, CLIENT_ID_KEY)


def set_client_id(client_id: str) -> None:
    secrets.set(AUTH_SERVICE, CLIENT_ID_KEY, client_id)


async def verify_id_token(id_token: str) -> dict:
    """Verify Google ID token. Returns user info dict. Raises on failure."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(TOKENINFO_URL, params={"id_token": id_token})
    if r.status_code != 200:
        raise ValueError(f"Token verification failed: {r.status_code}")
    data = r.json()

    client_id = get_client_id()
    if client_id and data.get("aud") != client_id:
        raise ValueError("Token aud mismatch")
    if int(data.get("exp", 0)) < time.time():
        raise ValueError("Token expired")

    return {
        "email": data.get("email"),
        "name": data.get("name"),
        "picture": data.get("picture"),
        "exp": int(data.get("exp", 0)),
    }


def save_session(user: dict) -> None:
    session_path().write_text(json.dumps(user), encoding="utf-8")


def load_session() -> dict | None:
    p = session_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if int(data.get("exp", 0)) < time.time():
            p.unlink(missing_ok=True)
            return None
        return data
    except Exception:
        return None


def clear_session() -> None:
    session_path().unlink(missing_ok=True)
