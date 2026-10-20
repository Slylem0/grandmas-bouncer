# 0003: Cascade thresholds

- Status: accepted (2026-10-20)
- Context: Decider README: on unseen short tasks, answers with confidence >= 0.9 are right ~95% of the time (noul confidence = |2p - 1|, so p >= 0.95 or <= 0.05). On our scenarios Decider *ranks* legit vs. injected calls well but its raw probabilities sit mid-range (legit `destination_trusted` mostly 0.58-0.95, attacks 0.15-0.50), so the README bands would escalate almost everything.
- Decision: per-question bands, tuned on the dev split (23 cases) by `benchmarks/summarize.py` (fewest errors, then fewest escalations, then widest bands), written to `benchmarks/results/thresholds.json` and loaded by the agent:
  - `destination_trusted`: allow >= 0.6, block <= 0.5
  - `user_requested_action`: allow >= 0.25, block <= 0.02
- Result on the held-out test split (41 cases): see `benchmarks/results/summary.md`.
- Limitation: dev had zero errors with no escalation, so the sweep learned a narrow middle band (2% escalated on test). A larger, harder dev set is needed to learn a band that routes the hard cases to the LLM.
