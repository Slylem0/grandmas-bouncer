# Progress log

Newest first. One entry per work session: what was done, numbers measured, blockers, next step.

## 2026-10-19
- Chose idea: Grandma's Bouncer (#guardrails). Submission draft saved on Builder Center (title, description, tags).
- Verified environment: RTX 3050 Laptop 4 GB, 23 GB RAM, uv + Python 3.12, AWS us-east-1.
- Verified Bedrock access: Sonnet 4.6 and Nova 2 Lite work; Claude 5.5 and Haiku 4.5 do not (see ADR 0002).
- Read strands-decider 0.2.0 and strands-agents 1.61.1 source; wrote `.kiro/steering/decider-api.md`.
- Created harness: AGENTS.md, CLAUDE.md, Kiro steering + spec (requirements/design/tasks), 6 subagents, ADRs 0001-0003.
- Next: Phase 0 (install, start Decider, check whether 4 GB VRAM is enough or fall back to CPU).
