"""A small synchronous client for a running Strands Decider server.

Standard library only, so the pattern can be dropped into any agent without pulling torch.
Start a server with:

    strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

ENV_URL = "STRANDS_DECIDER_URL"
DEFAULT_URL = "http://127.0.0.1:8099"
SERVE_HINT = "strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099"


class DeciderUnavailable(RuntimeError):
    """The server did not answer. The message says how to start one."""


@dataclass
class DeciderResult:
    answers: dict[str, dict[str, Any]]
    latency_ms: float
    server_latency_ms: float | None
    input_tokens: int

    def noul(self, name: str) -> float:
        """P(true) for a yes/no question."""
        return float(self.answers[name]["noul"])


class DeciderClient:
    """One state, many typed questions, one round trip."""

    def __init__(self, url: str | None = None, timeout: float = 60.0) -> None:
        self.url = (url or os.environ.get(ENV_URL, DEFAULT_URL)).rstrip("/")
        self.timeout = timeout

    # ---- question builders ------------------------------------------------

    @staticmethod
    def noul(instructions: str, criteria: Mapping[str, str] | None = None) -> dict[str, Any]:
        """Yes/no. The answer is P(true); `criteria` may describe "true" and "false"."""
        question: dict[str, Any] = {"type": "noul", "instructions": instructions}
        if criteria:
            question["criteria"] = dict(criteria)
        return question

    @staticmethod
    def choice(instructions: str, criteria: Mapping[str, str]) -> dict[str, Any]:
        """Pick one of N. `criteria` maps option name -> what it means."""
        return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}

    @staticmethod
    def score(instructions: str, criteria: list[str]) -> dict[str, Any]:
        """Rate on an ordered rubric, lowest level first."""
        return {"type": "score", "instructions": instructions, "criteria": list(criteria)}

    # ---- calls ------------------------------------------------------------

    def _unavailable(self, exc: Exception) -> DeciderUnavailable:
        return DeciderUnavailable(
            f"no Decider at {self.url} ({exc}). Start one with:\n    {SERVE_HINT}"
        )

    def ask(self, state: Any, questions: Mapping[str, dict[str, Any]]) -> DeciderResult:
        body = json.dumps(
            {"state": state, "model": "strands-decider-latest", "questions": dict(questions)}
        ).encode()
        request = urllib.request.Request(
            f"{self.url}/v1/systemone", data=body, headers={"content-type": "application/json"}
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise self._unavailable(exc) from exc
        latency_ms = (time.perf_counter() - start) * 1000
        return DeciderResult(
            answers=payload["answers"],
            latency_ms=latency_ms,
            server_latency_ms=payload.get("latency_ms"),
            input_tokens=payload.get("usage", {}).get("input_tokens", 0),
        )

    def health(self) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(f"{self.url}/health", timeout=10) as response:
                return json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise self._unavailable(exc) from exc
