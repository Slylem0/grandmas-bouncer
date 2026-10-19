---
inclusion: always
---

# Hackathon: Agent Experience Hackathon, Strands Decider

**Deadline: 2026-10-23 23:59 GMT-7 (Pacific).** Today's work must always move toward a submittable state.

## Mandatory deliverables (all required to qualify)
- [ ] Agent using Strands Decider 2B for at least one meaningful decision, paired with Amazon Bedrock.
- [ ] Article on AWS Builder Center describing the agent, what it does, and the decision handed to Decider 2B.
- [ ] Public repo (GitHub user `Slylem0`) with source + **at least one reusable Decider decision pattern**
      (typed question + option set, the wiring e.g. an `InterventionHandler`, and a short usage note).
- [ ] Public demo video **under 3 minutes** showing the agent and the Decider decision working.
- [ ] Declared pattern tag: `#guardrails`. Required tag: `#strands-decider-2b`.
- [ ] Original, unpublished agent.

## Rubric (optimize for this)
| Weight | Criterion | How we win it |
|---|---|---|
| 30% | Creativity and cool factor | Grandma story; live injection attack blocked on screen |
| 30% | Effective use of Decider 2B with Bedrock (+ quality of reusable pattern; measured latency/cost is a bonus) | Provenance-aware guard, confidence cascade, benchmark vs. LLM-as-judge |
| 25% | Communication quality | Clear article, diagram, under-3-min video with a story arc |
| 15% | Originality | Trust-labelled provenance (the scam IBAN *is* in context, so naive grounding fails) |

Judging: Gate 1 (AI + human scoring, top 100) week of Oct 26, Gate 2 (AWS experts) week of Nov 2.
An AI scorer reads the article: be explicit and structured, name the pattern, the question, the options,
the thresholds and the measured results.

## Submission form fields (Builder Center)
- Title: `Grandma's Bouncer: Stopping Scam Emails From Hijacking an AI Assistant with Strands Decider 2B`
- Tags (max 5): `strands-decider-2b`, `guardrails`, `amazon-bedrock`, `ai-agents`, `security`
- Repo: `https://github.com/Slylem0/grandmas-bouncer`
- Cover image: 1200x675, no text.
