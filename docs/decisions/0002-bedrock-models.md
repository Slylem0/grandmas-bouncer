# 0002: Bedrock models

- Status: accepted (2026-10-19)
- Context: Converse calls tested from this account in us-east-1. Works: `us.anthropic.claude-sonnet-4-6`, `us.amazon.nova-2-lite-v1:0`, `us.amazon.nova-pro-v1:0`. Fails: Claude Sonnet/Haiku 5.5 (not available for account), Haiku 4.5 (Anthropic use-case form not submitted).
- Decision: agent brain and strong judge = Sonnet 4.6; cheap judge baseline = Nova 2 Lite. All ids in `config.py`, env-overridable.
- Consequences: if Pablo submits the Anthropic use-case form, Haiku 4.5 can be added as a third judge without code changes.
