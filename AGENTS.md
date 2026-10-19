# AGENTS.md

Entry point for any AI coding agent working in this repo (Claude Code, Kiro, Codex, others).

## What this is
**Grandma's Bouncer**: a Strands agent on Amazon Bedrock that manages an elderly user's email and
bills, guarded by a reusable Strands Decider 2B `InterventionHandler` that blocks tool calls
injected by scam emails. Hackathon entry, pattern `#guardrails`, **deadline 2026-10-23 23:59 PT**.

## Read before working (single source of truth)
| File | When |
|---|---|
| `.kiro/steering/product.md` | Always: what and why, the provenance + cascade idea |
| `.kiro/steering/hackathon.md` | Always: deliverables, rubric, deadline |
| `.kiro/steering/tech.md` | Always: verified env, models, commands, risks |
| `.kiro/steering/structure.md` | Always: layout and conventions |
| `.kiro/steering/decider-api.md` | Before touching Decider or interventions code |
| `.kiro/specs/grandmas-bouncer/requirements.md` | What "done" means (EARS criteria) |
| `.kiro/specs/grandmas-bouncer/design.md` | Interfaces, data models, decisions |
| `.kiro/specs/grandmas-bouncer/tasks.md` | What to do next (first unticked task in the current phase) |
| `docs/progress.md` | What happened last session, blockers |
| `docs/decisions/` | Why things are the way they are |

Do not duplicate content from these files elsewhere; link to them.

## Ground rules
1. **Verify, don't recall.** Decider 2B and Strands interventions are newer than most model training
   data. Check `decider-api.md` and the installed source under `.venv/lib/python3.12/site-packages/`.
2. **Never invent numbers.** Latency, accuracy and cost come from `benchmarks/results/` and name the device.
3. **Fail closed.** Any guard error must block money movement, never allow it.
4. `src/decider_patterns/` must never import `grandmas_bouncer`.
5. Fake data only: fictional people, companies, IBAN-like ids with the `XX` prefix.
6. English for code, docs and commits. The human (Pablo) prefers to chat in Spanish.
7. Small Conventional Commits authored only by Pablo: **no `Co-Authored-By` or "Generated with" trailers**. Don't push or publish without his go-ahead.
8. After each task: tick `tasks.md`, append a dated entry to `docs/progress.md`.
9. A decision that changes the design gets an ADR in `docs/decisions/` and an update to `design.md`.

## Commands
```bash
uv sync --extra decider
scripts/serve_decider.sh                         # Decider on :8099 (cuda, falls back to cpu)
uv run pytest -m "not decider and not bedrock"   # fast tests
uv run pytest                                    # all tests (server + AWS needed)
uv run ruff check . && uv run ruff format --check .
uv run python -m grandmas_bouncer.demo_cli
uv run python -m grandmas_bouncer.web
uv run python -m benchmarks.run
```

## Definition of done for any task
- Acceptance criteria in `requirements.md` for that task are met.
- Unit tests added/updated and passing; ruff clean.
- `tasks.md` ticked, `docs/progress.md` updated.

## Subagents (Claude Code: `.claude/agents/`)
| Agent | Owns |
|---|---|
| `decider-engineer` | `src/decider_patterns/`: client, provenance, cascade, guard, question wording |
| `agent-builder` | `src/grandmas_bouncer/`: world, tools, Bedrock agent, CLI and web demo |
| `red-teamer` | `scenarios/`: attack and legit cases, hard cases, EN/ES |
| `benchmarker` | `benchmarks/`: judges, runs, sweep, `summary.md` |
| `storyteller` | README, `docs/article/`, video script, pattern README |
| `reviewer` | Read-only audit against requirements, rubric and ground rules |

Parallelism that works: `decider-engineer` and `agent-builder` in Phase 1-2 (different packages);
`red-teamer` can start scenarios as soon as the YAML case format in `design.md` is fixed.
