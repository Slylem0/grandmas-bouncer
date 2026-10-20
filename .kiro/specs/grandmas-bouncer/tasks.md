# Implementation Plan

Deadline 2026-10-23 23:59 PT. Day plan: D1 = Oct 19-20, D2 = Oct 21, D3 = Oct 22, D4 = Oct 23.
Each task names its owner subagent (see `.claude/agents/`). Tick boxes as you go and log in `docs/progress.md`.

## Phase 0: Environment (D1)
- [x] 0.1 `uv sync --extra decider` succeeds; torch sees CUDA. _Owner: main_
- [x] 0.2 Download checkpoint and start the server on `--device cuda`; if OOM on 4 GB, use `--device cpu`. Record device, load time and first `/health` in `docs/progress.md`. Add `scripts/serve_decider.sh` that picks the device. _Req 1_ **Result: CUDA OOM on 4 GB; serving on CPU. EC2 g6.xlarge via `scripts/ec2_decider.sh` once the G-instance quota request (PENDING) is approved.**
- [x] 0.3 Smoke test: README "payouts failing" question via `strands-decider ask`; record latency. _Req 1_
- [x] 0.4 Bedrock smoke: Strands `Agent(model="us.anthropic.claude-sonnet-4-6")` says hello. _Req 6_ (Sonnet later blocked by the Anthropic use-case form; agent runs on Nova, see ADR 0002)

## Phase 1: Reusable pattern core (D1) — owner `decider-engineer`
- [x] 1.1 `decider_patterns/client.py` + unit tests with a fake HTTP server. _Req 1.1-1.5_
- [x] 1.2 `decider_patterns/provenance.py` + unit tests (labels, toolUseId mapping, assistant text not evidence, truncation order). _Req 2_
- [x] 1.3 `decider_patterns/cascade.py` + boundary tests. _Req 4.1-4.4_
- [x] 1.4 `decider_patterns/grounding_guard.py` with escalation `block` + fake-client tests (unprotected passes, allow, block, escalate, fail-closed, listeners). _Req 3, 4_
- [x] 1.5 Live smoke (`@decider`): 3 hand-written states (legit, injected IBAN, injected action) give the expected ordering of probabilities. (covered by the benchmark and the end-to-end demo run)

## Phase 2: Demo agent (D1-D2) — owner `agent-builder`
- [x] 2.1 `world.py` + `scenarios/world_demo.yaml` (Grandma Carmen, balance, payees, contacts, inbox with: legit electricity bill, grandson birthday email, bank-IBAN-change scam with hidden instruction, "grandson in trouble" scam). _Req 5_
- [x] 2.2 `tools.py` with the 7 tools and side-effect ledger + tests. _Req 5.2-5.4_
- [x] 2.3 `config.py` (env-overridable model ids, URL, thresholds, escalation mode). _Req 6.1_
- [x] 2.4 `agent.py` `build_agent()` with system prompt and guard. _Req 6_
- [x] 2.5 `demo_cli.py`: scripted story with rich panels; shows probabilities, verdict, latency, final balance. _Req 7.1-7.2_
- [x] 2.6 End-to-end run (`@bedrock @decider`); fix prompt so the injection actually reaches the guard (the attack must be real, not staged).

## Phase 3: Scenarios and benchmark (D2) — owners `red-teamer`, `benchmarker`
- [x] 3.1 `scenarios/injection.yaml` (>= 25), `legit.yaml` (>= 25), `hard.yaml` (>= 10), EN + ES. _Req 8_
- [x] 3.2 `benchmarks/judges.py`: `DeciderJudge`, `BedrockJudge(model_id)` returning P(safe) + usage; `CascadeJudge`. _Req 9.1_ (built as `grandmas_bouncer/judge.py` + offline cascade in `benchmarks/summarize.py`)
- [x] 3.3 `benchmarks/pricing.yaml` with on-demand prices, source URL and date. _Req 9.3_
- [x] 3.4 `benchmarks/run.py`: runs systems, writes jsonl + `summary.md` with device/checkpoint. _Req 9.2, 9.4, 9.6_
- [x] 3.5 `benchmarks/sweep.py`: threshold sweep; write ADR 0003 with chosen thresholds. _Req 9.5, 4.5_ (per-question sweep lives in `benchmarks/summarize.py`, writes `results/thresholds.json`; ADR 0003 to update with final numbers)
- [x] 3.6 Tune question wording/criteria if the sweep shows a weak question (record before/after numbers, no cherry-picking: keep a held-out split).

## Phase 4: Escalation + web UI (D3) — owner `agent-builder`
- [x] 4.1 Escalation `llm` via Bedrock judge, and `human` via `Confirm`. _Req 4.3_
- [x] 4.2 FastAPI web app + single-page UI with three panels and SSE. _Req 7.3-7.4_
- [ ] 4.3 Family alert panel. _Req 7.5 (P2)_

## Phase 5: Ship (D3-D4) — owner `storyteller`, review by `reviewer`
- [x] 5.1 `decider_patterns/README.md` recipe + `examples/minimal_guard.py` (< 40 lines, non-banking). _Req 10_
- [x] 5.2 `README.md` final (diagram, quickstart, results table from summary.md). _Req 11.1_
- [x] 5.3 `docs/article/article.md` for Builder Center. _Req 11.2_
- [ ] 5.4 `docs/article/video-script.md` (< 3 min shot list) and record video. _Req 11.3_ (script done in `docs/article/video-script.md`; recording pending, Pablo)
- [x] 5.5 `reviewer` pass: requirements checklist, no invented numbers, no real brands/IBANs, tests green.
- [ ] 5.6 LICENSE (Apache-2.0), push public repo `Slylem0/grandmas-bouncer`, publish article with tags, submit before 2026-10-23 23:59 PT. _Req 11.4_
