"""Install runner — executes plan steps with SSE progress."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

from roboforge.install.plan import InstallPlan, InstallStep
from roboforge.ipc.event_bus import bus
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


async def run_step(step: InstallStep, dry_run: bool = False) -> dict:
    """Execute single install step. Returns status dict."""
    result = {"id": step.id, "name": step.name, "status": "pending", "output": "", "error": None}

    if dry_run:
        result["status"] = "skipped"
        result["output"] = f"[dry-run] would execute: {step.command}"
        return result

    try:
        proc = await asyncio.create_subprocess_shell(
            step.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)
        output = stdout.decode(errors="replace")

        if proc.returncode == 0:
            result["status"] = "done"
            result["output"] = output[-2000:]  # tail
        else:
            result["status"] = "failed"
            result["error"] = f"exit code {proc.returncode}"
            result["output"] = output[-2000:]
    except asyncio.TimeoutError:
        result["status"] = "failed"
        result["error"] = "timeout (300s)"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)

    return result


async def run_plan(plan: InstallPlan, dry_run: bool = False) -> AsyncIterator[str]:
    """Execute plan steps, yielding SSE events."""
    total = plan.total

    yield f"data: {json.dumps({'type': 'plan', 'distro': plan.distro, 'total': total})}\n\n"

    for i, step in enumerate(plan.steps):
        progress = {"type": "progress", "step": i + 1, "total": total,
                     "id": step.id, "name": step.name, "status": "running"}
        yield f"data: {json.dumps(progress)}\n\n"

        bus.emit("install:step", {"step": step.id, "index": i + 1, "total": total})

        result = await run_step(step, dry_run=dry_run)

        progress["status"] = result["status"]
        progress["output"] = result.get("output", "")[:500]
        progress["error"] = result.get("error")
        yield f"data: {json.dumps(progress)}\n\n"

        bus.emit("install:step_done", {"step": step.id, "status": result["status"]})

        if result["status"] == "failed" and not step.optional:
            yield f"data: {json.dumps({'type': 'error', 'step': step.id, 'error': result['error']})}\n\n"
            break

    yield "data: [DONE]\n\n"
