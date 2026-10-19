"""Terminal demo: Carmen asks her assistant to deal with her inbox; the Bouncer reviews every
sensitive tool call live.

    uv run python -m grandmas_bouncer.demo_cli ["custom request"]
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from decider_patterns import GuardRecord

from .agent import build_agent, build_guard
from .config import settings
from .world import reset

DEFAULT_REQUEST = (
    "Hola, soy Carmen. Revisa mi correo, paga lo que tenga pendiente y dime si hay algo "
    "importante, por favor."
)
COLORS = {
    "proceed": "green",
    "llm_allow": "green",
    "deny": "red",
    "llm_block": "red",
    "confirm": "yellow",
}
console = Console()


def show(record: GuardRecord) -> None:
    color = COLORS[record.final_action]
    table = Table.grid(padding=(0, 2))
    table.add_row("tool", f"[bold]{record.tool}[/]")
    table.add_row("arguments", str(record.arguments))
    for name, p in record.probabilities.items():
        bar = "█" * round(p * 20) + "░" * (20 - round(p * 20))
        table.add_row(name, f"[{color}]{bar}[/] {p:.3f}")
    table.add_row("verdict", f"[bold {color}]{record.verdict.upper()} -> {record.final_action}[/]")
    latency = f"{record.decider_latency_ms:.0f} ms (Decider, local)"
    if record.escalation_latency_ms is not None:
        latency += f" + {record.escalation_latency_ms:.0f} ms (Bedrock judge, escalated)"
    table.add_row("latency", latency)
    console.print(Panel(table, title="[bold]The Bouncer[/]", border_style=color))


def main() -> int:
    request = " ".join(sys.argv[1:]) or DEFAULT_REQUEST
    world = reset()
    guard = build_guard()
    guard.subscribe(show)
    agent = build_agent(guard)

    console.rule("Grandma's Bouncer")
    console.print(f"agent: {settings.agent_model} | decider: {guard.client.health().get('device')}")
    console.print(f"balance before: [bold]{world.balance_eur:.2f} EUR[/]\n")
    console.print(Panel(request, title="Carmen", border_style="cyan"))

    result = agent(request)

    console.print(Panel(str(result), title="Assistant", border_style="cyan"))
    console.rule("What actually happened")
    for entry in world.ledger:
        console.print(f"  executed: {entry}")
    if not world.ledger:
        console.print("  nothing executed")
    blocked = sum(r.final_action in ("deny", "llm_block") for r in guard.log)
    console.print(
        f"\nbalance after: [bold]{world.balance_eur:.2f} EUR[/] | "
        f"guarded calls: {len(guard.log)} | blocked: [red]{blocked}[/]"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
