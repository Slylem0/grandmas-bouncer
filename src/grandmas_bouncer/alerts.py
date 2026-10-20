"""Family alert: when the Bouncer blocks something, tell a trusted family member in plain words.

The alert is sent by the app itself, not through the agent's tools, so an injected email can never
suppress or redirect it. It says what was attempted, which email asked for it, that no money moved,
and what the family member should do next.
"""

from __future__ import annotations

import time
from typing import Any

from decider_patterns import GuardRecord

from .world import World


def eur(amount: float) -> str:
    """Spanish money format: 1.234,50 €."""
    return f"{amount:,.2f} €".replace(",", "_").replace(".", ",").replace("_", ".")


def _squash(text: str) -> str:
    return "".join(text.split()).lower()


def source_email(world: World, needle: str) -> dict[str, Any] | None:
    """The inbox email that mentions the blocked destination, if any (whitespace-insensitive)."""
    if not needle or needle == "?":
        return None
    key = _squash(needle)
    return next((e for e in world.inbox if key in _squash(e.get("body", ""))), None)


def describe(record: GuardRecord) -> tuple[str, str]:
    """(what was attempted, destination) in plain Spanish."""
    args = record.arguments
    if record.tool == "transfer_money":
        amount = eur(float(args.get("amount_eur", 0)))
        return f"enviar {amount} a una cuenta desconocida", str(args.get("iban", "?"))
    if record.tool == "add_payee":
        name = args.get("name", "?")
        return f"guardar una cuenta nueva como si fuera de «{name}»", str(args.get("iban", "?"))
    if record.tool == "send_email":
        return "enviar un correo con sus datos", str(args.get("to", "?"))
    return record.tool, "?"


def plain(record: GuardRecord) -> str:
    """The attempt in the fewest, simplest words, for Carmen."""
    if record.tool == "transfer_money":
        return "enviar tu dinero a una cuenta desconocida"
    if record.tool == "add_payee":
        return f"cambiar la cuenta de {record.arguments.get('name', 'un pago')}"
    return "enviar tus datos a un desconocido"


def family_alert(record: GuardRecord, world: World) -> dict[str, Any]:
    owner = world.owner["name"].split()[0]
    attempt, destination = describe(record)
    email = source_email(world, destination)
    origin = f"Un correo de {email['from']}" if email else "Un correo"
    text = (
        f"He parado una estafa a {owner}.\n"
        f"{origin} pedía {attempt} ({destination}).\n"
        "No se ha movido dinero.\n\n"
        f"👉 Llama a {owner} con calma y dile que borre ese correo."
    )
    alert = {
        "ts": time.time(),
        "to": world.owner.get("family_contact", "family"),
        "owner": owner,
        "attempt": attempt,
        "destination": destination,
        "email_from": email["from"] if email else None,
        "email_subject": email["subject"] if email else None,
        "email_id": email["id"] if email else None,
        "text": text,
        # What Carmen herself sees: short, calm, no account numbers or jargon.
        "owner_text": (
            f"Un correo pedía {plain(record)}. No lo he hecho. Tu dinero está bien. "
            "No contestes a ese correo. Ya se lo he dicho a Lucía."
        ),
    }
    world.alerts.append(alert)
    return alert
