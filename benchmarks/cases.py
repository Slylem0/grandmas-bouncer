"""Load scenario cases and turn them into Strands-shaped messages, so the benchmark renders state
with the exact code the agent uses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from decider_patterns import ProvenancePolicy, render_state
from grandmas_bouncer.tools import TRUSTED_TOOLS

SCENARIOS = Path(__file__).resolve().parents[1] / "scenarios"
FILES = ("legit.yaml", "injection.yaml", "hard.yaml")
POLICY = ProvenancePolicy(trusted_tools=TRUSTED_TOOLS)


def load_cases(split: str = "all") -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for name in FILES:
        cases += yaml.safe_load((SCENARIOS / name).read_text())
    return [c for c in cases if split == "all" or c["split"] == split]


def to_messages(case: dict[str, Any]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for i, m in enumerate(case["messages"]):
        if m["role"] == "tool":
            use_id = f"t{i}"
            messages.append(
                {
                    "role": "assistant",
                    "content": [{"toolUse": {"toolUseId": use_id, "name": m["tool"], "input": {}}}],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"toolResult": {"toolUseId": use_id, "content": [{"text": m["text"]}]}}
                    ],
                }
            )
        else:
            messages.append({"role": m["role"], "content": [{"text": m["text"]}]})
    return messages


def state_for(case: dict[str, Any]) -> str:
    call = case["call"]
    return render_state(to_messages(case), call["tool"], call["input"], POLICY)
