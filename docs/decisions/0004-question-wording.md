# 0004: Question wording chosen on the dev split

- Status: accepted (2026-10-19)
- Context: `benchmarks/question_lab.py`, dev split (23 cases), Decider 2B v1 on CPU. Best single-cut accuracy per question:

| variant | destination_trusted | user_requested_action |
|---|---|---|
| A abstract wording + preamble | 1.000 (margin +0.150) | 0.739 |
| B no preamble | 0.957 | 0.913 |
| C concrete user-request wording + preamble | 1.000 (margin +0.150) | 0.870 |
| D B + C | 0.957 | 0.826 |

- Decision: C. Keep the provenance preamble (it makes `destination_trusted` separate perfectly on dev) and phrase `user_requested_action` with concrete examples of tasks the user asks for.
- Consequences: report on the test split only. Raw numbers in `benchmarks/results/question_lab.json`.
