# 0003: Cascade thresholds

- Status: proposed (2026-10-19)
- Context: Decider README: on unseen short tasks, answers with confidence >= 0.9 are right ~95% of the time. For a noul answer, confidence = |2p - 1|, so p >= 0.95 or p <= 0.05.
- Decision (initial): allow if every safety probability >= 0.95; block if any <= 0.05; otherwise escalate.
- To do: replace with values from `benchmarks/sweep.py` on the `dev` split; report on `test`. Update status to accepted with the numbers.
