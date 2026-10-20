"""FastAPI demo: Carmen's inbox, the chat with her assistant, and the Bouncer's live decisions.

uv run python -m grandmas_bouncer.web    # http://127.0.0.1:8000
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from decider_patterns import GuardRecord

from ..agent import build_agent, build_guard, clean_reply
from ..alerts import family_alert
from ..config import settings
from ..world import current_world, reset

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Grandma's Bouncer")


class Session:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.events: list[dict[str, Any]] = []
        self.start()

    def start(self) -> None:
        reset()
        self.events.clear()
        self.guard = build_guard()
        self.guard.subscribe(self.on_guard)
        self.guard.subscribe_start(
            lambda tool, args: self.push("guard_start", {"tool": tool, "arguments": args})
        )
        self.agent = build_agent(self.guard)
        self.push("world", current_world().snapshot())

    def push(self, kind: str, data: Any) -> None:
        self.events.append({"kind": kind, "ts": time.time(), "data": data})

    def on_guard(self, record: GuardRecord) -> None:
        self.push("guard", asdict(record))
        if record.final_action in ("deny", "llm_block"):
            self.push("family", family_alert(record, current_world()))

    def chat(self, message: str) -> str:
        with self.lock:
            self.push("user", message)
            try:
                reply = clean_reply(self.agent(message))
            except Exception as exc:  # noqa: BLE001 - surface any agent failure in the UI
                reply = f"(error: {exc})"
            self.push("assistant", reply)
            self.push("world", current_world().snapshot())
            return reply


session = Session()


class ChatIn(BaseModel):
    message: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/config")
def config() -> dict[str, Any]:
    try:
        device = session.guard.client.health().get("device", "?")
    except Exception:  # noqa: BLE001
        device = "offline"
    return {
        "agent_model": settings.agent_model,
        "judge_model": settings.judge_model,
        "escalation": settings.escalation,
        "thresholds": {
            q: {"allow": b.allow, "block": b.block}
            for q, b in (
                settings.thresholds.items()
                if isinstance(settings.thresholds, dict)
                else {"all": settings.thresholds}.items()
            )
        },
        "decider_device": device,
    }


@app.post("/chat")
async def chat(body: ChatIn) -> dict[str, str]:
    return {"reply": await asyncio.to_thread(session.chat, body.message)}


@app.post("/reset")
def do_reset() -> dict[str, str]:
    with session.lock:
        session.start()
    return {"ok": "reset"}


@app.get("/email/{email_id}")
def email(email_id: int) -> dict[str, Any]:
    return next((e for e in current_world().inbox if e["id"] == email_id), {})


@app.get("/events")
async def events() -> StreamingResponse:
    async def stream():
        sent = 0
        while True:
            if sent > len(session.events):  # session was reset
                sent = 0
                yield 'data: {"kind": "reset"}\n\n'
            while sent < len(session.events):
                yield f"data: {json.dumps(session.events[sent], default=str)}\n\n"
                sent += 1
            await asyncio.sleep(0.15)

    return StreamingResponse(stream(), media_type="text/event-stream")
