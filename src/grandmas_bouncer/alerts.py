"""Family alert: when the Bouncer blocks something, tell a trusted family member in plain words.

The alert is sent by the app itself, not through the agent's tools, so an injected email can never
suppress or redirect it.
"""

from __future__ import annotations

import time
from typing import Any

from decider_patterns import GuardRecord

from .world import World

WHAT = {
    "transfer_money": "enviar {amount} a la cuenta {iban}",
    "add_payee": "guardar la cuenta {iban} como beneficiario de confianza",
    "send_email": "enviar un correo a {to}",
}


def family_alert(record: GuardRecord, world: World) -> dict[str, Any]:
    args = record.arguments
    amount = f"{args['amount_eur']:.2f} EUR" if "amount_eur" in args else ""
    action = WHAT.get(record.tool, record.tool).format(
        amount=amount, iban=args.get("iban", "?"), to=args.get("to", "?")
    )
    owner = world.owner["name"].split()[0]
    text = (
        f"Hola. El asistente de {owner} acaba de bloquear un intento de {action}. "
        "La petición venía de un correo, no de ella. No se ha movido dinero. "
        f"Llámala para comprobar que está bien y que nadie le ha pedido datos."
    )
    alert = {"ts": time.time(), "to": world.owner.get("family_contact", "family"), "text": text}
    world.alerts.append(alert)
    return alert
