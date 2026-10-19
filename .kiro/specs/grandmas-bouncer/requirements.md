# Requirements Document

## Introduction

Grandma's Bouncer is a Strands agent on Amazon Bedrock that helps an elderly user manage email and
pay bills. Every sensitive tool call is reviewed first by a reusable Strands Decider 2B guardrail
(the "Bouncer"), which checks whether the call's arguments and intent come from the user and her
trusted records, not from untrusted content such as a scam email. Confident verdicts are decided
locally; uncertain ones are escalated to the user or to a Bedrock LLM judge. The project ships a
reusable decision pattern, a benchmark against LLM-as-judge baselines, an article and a demo video.

Priorities: **P0** = required to submit, **P1** = needed to win, **P2** = nice to have.

## Requirements

### Requirement 1: Decider client (P0)

**User Story:** As an agent builder, I want a minimal client for the Decider HTTP server, so that any
component can ask typed questions without depending on torch.

#### Acceptance Criteria
1. WHEN the client sends a state and a dict of named questions THEN it SHALL issue one `POST /v1/systemone` and return answers keyed by the same names.
2. WHEN the server is unreachable THEN the client SHALL raise `DeciderUnavailable` with the command to start a server.
3. The client SHALL record per-call latency (wall clock and server `latency_ms`) and input tokens.
4. The client SHALL read its URL from `STRANDS_DECIDER_URL`, defaulting to `http://127.0.0.1:8099`.
5. The client SHALL depend only on the Python standard library.

### Requirement 2: Provenance-aware state rendering (P0)

**User Story:** As a guardrail, I want the conversation rendered with explicit trust labels, so that
Decider can tell Grandma's words apart from text that merely appeared in an email.

#### Acceptance Criteria
1. WHEN rendering `agent.messages` THEN user text blocks SHALL be labelled `TRUSTED: user said`.
2. WHEN a tool result comes from a tool listed as trusted (e.g. `list_payees`, `list_contacts`) THEN it SHALL be labelled `TRUSTED: <tool> record`.
3. WHEN a tool result comes from any other tool (e.g. `read_inbox`, `read_attachment`) THEN it SHALL be labelled `UNTRUSTED: content from <tool>`.
4. The proposed tool call (name and JSON arguments) SHALL be appended in its own section.
5. IF the rendered state exceeds a configurable character budget THEN the renderer SHALL truncate the oldest untrusted content first and never drop user turns or the proposed call.
6. The renderer SHALL be a pure function with unit tests.

### Requirement 3: GroundingGuard intervention (P0)

**User Story:** As an agent builder, I want a drop-in `InterventionHandler`, so that I can protect
sensitive tools in my own Strands agent in about three lines.

#### Acceptance Criteria
1. The guard SHALL subclass `strands.interventions.InterventionHandler` and implement `before_tool_call`.
2. WHEN the proposed tool is not in `protected_tools` THEN the guard SHALL return `Proceed` without calling Decider.
3. WHEN the tool is protected THEN the guard SHALL ask Decider, in one request, at least: `destination_trusted` (noul) and `user_requested_action` (noul).
4. The question texts, `criteria` and thresholds SHALL be configurable and have documented defaults.
5. The guard SHALL set `on_error = "deny"` so failures are fail-closed.
6. The guard SHALL append a structured record of every decision (tool, args, probabilities, verdict, latency, escalation used) to an in-memory log and notify optional listeners (for the UI).

### Requirement 4: Confidence cascade (P0 core, P1 escalation)

**User Story:** As Grandma, I want the assistant to act instantly when it is clearly safe, stop
instantly when it is clearly a scam, and ask me only when it is genuinely unsure.

#### Acceptance Criteria
1. WHEN every safety probability is at or above `allow_threshold` THEN the verdict SHALL be `allow` and the guard SHALL return `Proceed`.
2. WHEN any safety probability is at or below `block_threshold` THEN the verdict SHALL be `block` and the guard SHALL return `Deny` with a reason explaining the problem in plain language.
3. OTHERWISE the verdict SHALL be `escalate`, handled by the configured escalation mode:
   - `human` (P1): return `Confirm` with a plain-language prompt for Grandma.
   - `llm` (P1): ask a Bedrock LLM judge the same question and map its answer to allow/block.
   - `block` (P0 default): treat as block (fail-safe).
4. The cascade SHALL be pure functions, unit-tested at each boundary.
5. Default thresholds SHALL be documented with their source (Decider README calibration note) and then replaced with values calibrated on the benchmark (ADR required).

### Requirement 5: Simulated world and tools (P0)

**User Story:** As the demo, I want a realistic but fake inbox, bank and address book, so that attacks
and legit actions can be shown safely and reproducibly.

#### Acceptance Criteria
1. The world SHALL contain: Grandma's profile, a balance, saved payees (with IBAN-like fake ids), contacts, and an inbox of emails (legit and malicious).
2. Tools SHALL include `read_inbox`, `read_email`, `list_payees`, `list_contacts`, `transfer_money`, `add_payee`, `send_email`.
3. `transfer_money`, `add_payee` and `send_email` SHALL be protected by the guard by default.
4. Executed side effects SHALL be recorded in the world so the demo can show "money moved / did not move".
5. The world SHALL be resettable and loadable from a YAML scenario file.
6. All names, companies and account ids SHALL be fictional.

### Requirement 6: Bedrock agent (P0)

**User Story:** As Grandma, I want to speak in plain Spanish or English and have the assistant handle my email and bills.

#### Acceptance Criteria
1. `build_agent()` SHALL create a Strands `Agent` using a Bedrock model id from config (default `us.anthropic.claude-sonnet-4-6`) with the tools and the GroundingGuard.
2. The system prompt SHALL make the agent helpful and action-oriented (so that injection attempts actually reach the guard) and SHALL instruct it to explain blocked actions kindly.
3. WHEN the guard blocks an action THEN the agent's final reply SHALL tell Grandma, in simple words, what was stopped and why.

### Requirement 7: Demo experience (P0 CLI, P1 web)

**User Story:** As a judge watching a <3 minute video, I want to see the attack, the Decider decision with its numbers, and the outcome at a glance.

#### Acceptance Criteria
1. (P0) A `rich` CLI demo SHALL run the scripted story: legit bill paid, injected transfer blocked, final balance shown.
2. (P0) For each guarded call the CLI SHALL show tool, arguments, each probability, verdict and latency.
3. (P1) A web UI SHALL show three panels: Grandma's inbox, the chat with the assistant, and the Bouncer log with live probability bars and verdict badges.
4. (P1) The web UI SHALL stream guard decisions as they happen (SSE or polling).
5. (P2) A "family alert" panel SHALL show the message that would be sent to a family member on a block.

### Requirement 8: Scenario dataset (P0)

**User Story:** As an evaluator, I want labelled cases covering attacks and legit actions, so that block rate and false-block rate can be measured.

#### Acceptance Criteria
1. Each case SHALL contain: id, category, rendered messages with provenance, the proposed tool call, and the expected verdict (`allow` or `block`).
2. The set SHALL include at least 60 cases: >= 25 injection attacks, >= 25 legit actions, >= 10 hard cases (legit payee mentioned in an email, partial grounding, amount changed by email, Spanish-language attacks).
3. Attack styles SHALL be varied: fake bank IBAN change, "grandson in trouble", fake invoice, hidden instructions in HTML-ish text, instructions in an attachment, social-engineering urgency.
4. Cases MAY be drafted with a Bedrock LLM but SHALL be reviewed and stored as static YAML (deterministic benchmark).

### Requirement 9: Benchmark (P0 numbers, P1 cascade comparison)

**User Story:** As a builder reading the article, I want honest numbers comparing Decider with an LLM judge.

#### Acceptance Criteria
1. The benchmark SHALL evaluate these systems on the same cases: `decider` (thresholded), `llm-nova` (`us.amazon.nova-2-lite-v1:0`), `llm-sonnet` (`us.anthropic.claude-sonnet-4-6`), and `cascade` (decider + LLM on the uncertain band).
2. For each system it SHALL report: accuracy, attack block rate (recall on block), false-block rate, escalation rate (cascade), p50/p95 latency, and estimated cost per 1,000 checks.
3. LLM cost SHALL be computed from returned token usage times on-demand prices recorded in a config file with the source URL and date; Decider marginal cost SHALL be reported as $0 API cost with the device stated.
4. Raw per-case results SHALL be written to `benchmarks/results/*.jsonl` and a summary table to `benchmarks/results/summary.md`.
5. The benchmark SHALL support a threshold sweep that outputs the allow/block thresholds chosen for the cascade.
6. The device (cuda or cpu) and checkpoint SHALL be recorded in every summary.

### Requirement 10: Reusable pattern package (P0)

**User Story:** As another builder, I want to copy one folder and protect my own agent.

#### Acceptance Criteria
1. `src/decider_patterns/` SHALL have no imports from `grandmas_bouncer`.
2. `src/decider_patterns/README.md` SHALL document: the typed questions and options, the provenance labels, the cascade, the wiring (`Agent(interventions=[GroundingGuard(...)])`), configuration knobs, and limitations.
3. A minimal example (< 40 lines) SHALL show the guard in a non-banking agent.

### Requirement 11: Communication deliverables (P0)

**User Story:** As the participant, I want ready-to-publish materials before the deadline.

#### Acceptance Criteria
1. `README.md` SHALL include: pitch, architecture diagram, quickstart, results table, the pattern, limitations.
2. `docs/article/article.md` SHALL follow the Builder Center structure (problem, what it does, decision handed to Decider, demo, results, reusable pattern, what I learned) and use only measured numbers.
3. `docs/article/video-script.md` SHALL be a shot list under 3 minutes.
4. The repo SHALL be pushed public to `github.com/Slylem0/grandmas-bouncer` with an Apache-2.0 license.
