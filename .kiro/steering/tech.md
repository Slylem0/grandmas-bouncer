---
inclusion: always
---

# Tech stack and environment

## Verified on this machine (2026-10-19)
| Item | Value |
|---|---|
| OS | Linux (Arch-based, Omarchy) |
| GPU | NVIDIA RTX 3050 Laptop, **4 GB VRAM** (tight for a 2B model in bf16; see risks) |
| RAM / CPU | 23 GB / 12 threads |
| Python | 3.12 via `uv` (`.python-version`); system 3.14 is too new for torch wheels |
| AWS region | `us-east-1`, IAM user `pablo-cdk-dev` |

## Packages
- `strands-agents` >= 1.61 — agent loop + `strands.interventions` (`InterventionHandler`, `Proceed`, `Deny`, `Guide`, `Confirm`, `Transform`).
- `strands-decider` >= 0.2 (optional extra `decider`) — model server + CLI. Pulls torch + transformers 5.
- `boto3` — Bedrock calls for the LLM-as-judge baseline.
- `fastapi` + `uvicorn` — demo web UI. `rich` — CLI demo output.
- Dev: `pytest`, `ruff` (line length 100).

## Amazon Bedrock models (invoke access verified)
| Role | Model ID | Status |
|---|---|---|
| Agent brain (generative) | `us.anthropic.claude-sonnet-4-6` | works |
| Cheap LLM-judge baseline | `us.amazon.nova-2-lite-v1:0` | works |
| Strong LLM-judge baseline | `us.anthropic.claude-sonnet-4-6` | works |
| Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | blocked: Anthropic use-case form not submitted |
| Sonnet/Haiku 5.5 | `us.anthropic.claude-*-5-5` | blocked: not available for this account |

Model IDs live in config (`src/grandmas_bouncer/config.py`), never hard-coded in logic.

## Decider 2B
- Checkpoint: `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610` (Apache-2.0, ~4.5 GB download).
- Served locally: `uv run strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099 [--device cuda|cpu]`.
- Agent talks to it over HTTP (`POST /v1/systemone`), URL from env `STRANDS_DECIDER_URL` (default `http://127.0.0.1:8099`).
- Full API reference: `.kiro/steering/decider-api.md`.

## Commands
```bash
uv sync --extra decider                 # install everything
uv run strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099
uv run pytest -m "not decider and not bedrock"   # fast unit tests, no network
uv run pytest                            # full suite (needs server + AWS)
uv run ruff check . && uv run ruff format .
uv run python -m grandmas_bouncer.demo_cli       # terminal demo
uv run python -m grandmas_bouncer.web            # web demo on :8000
uv run python -m benchmarks.run --systems decider,llm-nova,llm-sonnet,cascade
```

## Risks
- **4 GB VRAM: verified CUDA OOM** on 2026-10-19 (3.37 GiB allocated, then OOM while loading). Use
  `--device cpu` (fp32, ~8 GB RAM, slower). Measure both and report the device honestly.
- Decider latency in the README (115 ms) is on an RTX 3090; our numbers will differ. Report ours.
- Strands intervention API is new: confirm signatures against the installed package
  (`.venv/lib/python3.12/site-packages/strands/interventions/`) before relying on memory.
