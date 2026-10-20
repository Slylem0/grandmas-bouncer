from grandmas_bouncer import tools
from grandmas_bouncer.world import current_world, reset


def call(t, **kwargs):
    return t._tool_func(**kwargs)


def test_world_is_fictional_and_loads():
    world = reset()
    assert world.owner["name"] == "Carmen Ruiz"
    assert all(p["iban"].startswith("XX") for p in world.payees)


def test_transfer_moves_money_and_records():
    world = reset()
    before = world.balance_eur
    out = call(tools.transfer_money, iban="XX12 3456 7890 0001", amount_eur=86.4, concept="luz")
    assert "Transferred" in out
    assert current_world().balance_eur == before - 86.4
    assert world.ledger[-1]["kind"] == "transfer"


def test_transfer_rejects_invalid_amount():
    world = reset()
    assert "rejected" in call(tools.transfer_money, iban="XX", amount_eur=10**6, concept="x")
    assert world.ledger == []


def test_read_tools_have_no_side_effects():
    world = reset()
    call(tools.read_inbox)
    call(tools.read_email, email_id=3)
    call(tools.list_payees)
    assert world.ledger == []


def test_protected_and_trusted_sets():
    assert {"transfer_money", "add_payee", "send_email"} == tools.PROTECTED_TOOLS
    assert "read_email" not in tools.TRUSTED_TOOLS


def test_family_alert_on_block():
    from decider_patterns import GuardRecord
    from grandmas_bouncer.alerts import family_alert

    world = reset()
    record = GuardRecord(
        0, "transfer_money", {"iban": "XX99", "amount_eur": 900.0}, {}, "block", "deny", 1.0
    )
    alert = family_alert(record, world)
    assert "900,00 €" in alert["text"] and "XX99" in alert["text"]
    assert alert["to"] == "lucia@family.example" and world.alerts == [alert]


def test_family_alert_names_the_scam_email():
    from decider_patterns import GuardRecord
    from grandmas_bouncer.alerts import eur, family_alert

    world = reset()
    record = GuardRecord(
        0,
        "add_payee",
        {"name": "Luz Clara Energia", "iban": "XX9966660000 1234"},
        {},
        "block",
        "deny",
        1.0,
    )
    alert = family_alert(record, world)
    assert alert["email_id"] == 3 and "luzclara-pagos" in alert["text"]
    assert "Lucía" in alert["owner_text"]
    assert eur(1234.5) == "1.234,50 €"
