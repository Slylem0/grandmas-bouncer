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

## 2026-10-20
- Sonnet 4.6 enabled after the Anthropic use-case form (Marketplace agreement email received).
- Fixed judge bug: `maxTokens=100` truncated Sonnet's answer and the parser read it as "unsafe"; now 400 tokens, JSON first, parse errors flagged and reported. Added adaptive retries after a Bedrock throttling crash.
- Question lab (dev): chose concrete `user_requested_action` wording (ADR 0004).
- Final test-split results (41 cases): Decider tuned 0.951 acc / $0 / 7.0 s CPU; Nova 2 Lite 1.000 / $0.34 per 1k; Sonnet 4.6 0.976 / $2.75; Nova Pro 0.927 / $0.62. Thresholds in ADR 0003.
- GPU quota request: support case opened, pending.
- Next: article, reviewer pass, GPU latency if quota arrives, video on Oct 22.
- GPU quota approved (8 vCPU G instances). Launched `grandmas-bouncer-decider` (g6.xlarge, NVIDIA L4). uv pulling CUDA wheels from PyPI ran at ~1 MB/s; installing torch from the PyTorch cu130 index fixed it (script updated).
- Decider on L4: README smoke 78 ms (86 tokens). Benchmark: same accuracy as CPU (0.951 test), server-side 186 ms p50 / 196 ms p95 for ~670-token states, vs 7.0 s on laptop CPU. Client-side ~0.93 s includes the SSH tunnel from the laptop.
- Web UI: live "checking" card and family alert notification. Web now points at the GPU via tunnel on :8100.
- Remember: `scripts/ec2_decider.sh down` after recording (billing).

## 2026-10-20
- Video script closing line now cites the measured L4 latency (<200 ms); task 4.3 (family alert panel) ticked.
- Next: record video on the GPU setup, then terminate the EC2 instance; make repo public; publish article.
