"""IPC envelope helpers — create and validate the shared IpcEnvelope shape."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def make_envelope(event_type: str, payload: Any = None, reply_to: str | None = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "error": None,
        "replyTo": reply_to,
    }


def make_error_envelope(event_type: str, code: str, message: str, reply_to: str | None = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": None,
        "error": {"code": code, "message": message, "details": None},
        "replyTo": reply_to,
    }
