"""Runtime configuration. Every value can be overridden with an environment variable."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from decider_patterns import Thresholds, ThresholdSpec

# Per-question bands written by `python -m benchmarks.summarize` (tuned on the dev split).
TUNED = Path(__file__).resolve().parents[2] / "benchmarks" / "results" / "thresholds.json"


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    agent_model: str = _env("BOUNCER_AGENT_MODEL", "us.amazon.nova-2-lite-v1:0")
    judge_model: str = _env("BOUNCER_JUDGE_MODEL", "us.amazon.nova-2-lite-v1:0")
    region: str = _env("AWS_REGION", "us-east-1")
    decider_url: str = _env("STRANDS_DECIDER_URL", "http://127.0.0.1:8099")
    allow_threshold: float = float(_env("BOUNCER_ALLOW", "0.95"))
    block_threshold: float = float(_env("BOUNCER_BLOCK", "0.05"))
    escalation: str = _env("BOUNCER_ESCALATION", "llm")  # block | human | llm

    thresholds_file: str = _env("BOUNCER_THRESHOLDS", str(TUNED))

    @property
    def thresholds(self) -> ThresholdSpec:
        """Tuned per-question bands if the file exists, else one global band."""
        path = Path(self.thresholds_file)
        if path.exists():
            data = json.loads(path.read_text())
            return {q: Thresholds(allow=b["allow"], block=b["block"]) for q, b in data.items()}
        return Thresholds(allow=self.allow_threshold, block=self.block_threshold)


settings = Settings()
