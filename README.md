# Grandma's Bouncer

An AI assistant that helps an elderly user with email and bills, guarded by a
[Strands Decider 2B](https://github.com/strands-labs/strands-decider) "bouncer" that checks every
sensitive tool call before it runs and blocks the ones a scam email asked for, not Grandma.

Built for the Agent Experience Hackathon: Strands Decider. Pattern: **#guardrails**.

> Work in progress. See `.kiro/specs/grandmas-bouncer/` for the spec and `docs/progress.md` for status.

## Quickstart (dev)
```bash
uv sync --extra decider
scripts/serve_decider.sh          # Decider 2B on :8099
uv run pytest -m "not decider and not bedrock"
```
