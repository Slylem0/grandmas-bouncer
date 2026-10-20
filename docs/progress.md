# Progress log

Newest first. One entry per work session: what was done, numbers measured, blockers, next step.

## 2026-10-19
- Chose idea: Grandma's Bouncer (#guardrails). Submission draft saved on Builder Center (title, description, tags).
- Verified environment: RTX 3050 Laptop 4 GB, 23 GB RAM, uv + Python 3.12, AWS us-east-1.
- Verified Bedrock access: Sonnet 4.6 and Nova 2 Lite work; Claude 5.5 and Haiku 4.5 do not (see ADR 0002).
- Read strands-decider 0.2.0 and strands-agents 1.61.1 source; wrote `.kiro/steering/decider-api.md`.
- Created harness: AGENTS.md, CLAUDE.md, Kiro steering + spec (requirements/design/tasks), 6 subagents, ADRs 0001-0003.
- Next: Phase 0 (install, start Decider, check whether 4 GB VRAM is enough or fall back to CPU).

## 2026-10-19 (evening)
- Decider on RTX 3050 4 GB: CUDA OOM while loading (verified). Serving on CPU: README smoke answer 0.8581 matches upstream; ~0.8-1.2 s for 86 tokens, 4-7 s for our 350-650 token states.
- EC2 G-instance on-demand quota in us-east-1 is 0: renting a GPU needs a quota increase.
- Sonnet 4.6 now blocked (Anthropic use-case form). Agent default switched to Nova Pro (ADR 0002 update).
- Question change: `destination_trusted` replaces "every argument grounded" (real bills state amounts in emails).
- Benchmark (64 cases; test split 41): Decider ranks well but probabilities are not calibrated for this task (legit `destination_trusted` 0.63-0.95, attacks 0.15-0.44). Per-question bands tuned on dev.
  Test: decider-only tuned 95.1% acc / 0 false blocks; Nova 2 Lite 97.6%; cascade Decider -> Nova 2 Lite 100% with 7% escalated, $0.025 vs $0.35 per 1k checks. Latency is the weak point on CPU.
- Next: decide on GPU (quota request / other), agent end-to-end demo run, harder scenarios.
