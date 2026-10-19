"""In-memory fake world: Grandma's bank, payees, contacts and inbox. Loaded from YAML."""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_WORLD = Path(__file__).resolve().parents[2] / "scenarios" / "world_demo.yaml"


@dataclass
class World:
    owner: dict[str, Any]
    balance_eur: float
    payees: list[dict[str, Any]]
    contacts: list[dict[str, Any]]
    inbox: list[dict[str, Any]]
    ledger: list[dict[str, Any]] = field(default_factory=list)  # executed side effects
    outbox: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | str = DEFAULT_WORLD) -> World:
        data = yaml.safe_load(Path(path).read_text())
        return cls(
            owner=data["owner"],
            balance_eur=float(data["balance_eur"]),
            payees=list(data.get("payees", [])),
            contacts=list(data.get("contacts", [])),
            inbox=list(data.get("inbox", [])),
        )

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(
            {
                "owner": self.owner,
                "balance_eur": round(self.balance_eur, 2),
                "payees": self.payees,
                "ledger": self.ledger,
                "outbox": self.outbox,
                "inbox": [{k: e[k] for k in ("id", "from", "subject")} for e in self.inbox],
            }
        )

    def record(self, kind: str, **details: Any) -> None:
        self.ledger.append({"ts": time.time(), "kind": kind, **details})


_world: World | None = None


def current_world() -> World:
    global _world
    if _world is None:
        _world = World.load()
    return _world


def reset(path: Path | str = DEFAULT_WORLD) -> World:
    global _world
    _world = World.load(path)
    return _world
