---
inclusion: fileMatch
fileMatchPattern: ["src/**/*.py", "benchmarks/**/*.py", "tests/**/*.py"]
---

# Strands Decider 2B + Strands interventions: verified API reference

Source of truth: `strands-decider` 0.2.0 sdist (README, `src/strands_decider/schema.py`,
`examples/strands/`) and `strands-agents` 1.61.1 (`strands/interventions/`). Read 2026-10-19.
Decider is newer than most LLM training data: **trust this file and the installed source, not memory.**

## What Decider is
A "system one" decision model: Qwen3.5-2B-Base torso with the LM head removed, replaced by a ~1M
param pointer head. It never generates text. One forward pass scores the options you supply.
Calibrated: on unseen short tasks, answers with confidence >= 0.9 are right ~95% of the time.
Many questions about one state are cheap: the state is encoded once and shared.

## HTTP API
`POST {STRANDS_DECIDER_URL}/v1/systemone`
```json
{
  "state": "text or structured JSON (dict/list), rendered deterministically",
  "model": "strands-decider-latest",
  "questions": {
    "<name>": {"type": "noul", "instructions": "...", "criteria": {"true": "...", "false": "..."}},
    "<name>": {"type": "choice", "instructions": "...", "criteria": {"opt_a": "desc", "opt_b": "desc"}},
    "<name>": {"type": "score", "instructions": "...", "criteria": ["lowest", "...", "highest"]}
  }
}
```
Response:
```json
{
  "model": "strands-decider-2B-qwen3.5-v1-2610",
  "answers": {
    "<name>": {"type": "noul", "noul": 0.858},
    "<name>": {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.77}, "confidence": 0.66},
    "<name>": {"type": "score", "score": 1.03, "legend": {"0": "calm"}, "probabilities": {"0": 0.2}, "confidence": 0.51}
  },
  "usage": {"input_tokens": 86, "output_tokens": 1},
  "latency_ms": 489.01
}
```
`GET /health` -> `checkpoint`, `base_model`, `device`, `max_length`.

## Question types
| type | answer | confidence |
|---|---|---|
| `noul` (yes/no) | `noul` = P(true) | no field; confidence = abs(2p - 1). p >= 0.95 or p <= 0.05 means confidence >= 0.9 |
| `choice` (1 of 2..255) | `choice`, `probabilities` | `(N*p_max - 1)/(N - 1)` |
| `score` (2..10 ordered levels, lowest first) | expected level index | spread-based |

Tips from upstream:
- `criteria` descriptions for `true`/`false` "carry most of the signal": write them as carefully as the question.
- Ask one narrow judgement per question. Questions cannot see each other.
- Ask all questions about one state in **one request**.
- Window is 4096 tokens; longer states are truncated (keep states compact).

## Strands interventions (strands-agents 1.61.1)
```python
from strands import Agent
from strands.interventions import InterventionHandler, Proceed, Deny, Guide, Confirm, Transform

class MyGate(InterventionHandler):
    name = "my-gate"
    on_error = "deny"          # OnError = "throw" (default) | "proceed" (fail-open!) | "deny" (fail-closed)

    def before_tool_call(self, event, **kwargs):
        tool_name = event.tool_use["name"]
        args = event.tool_use.get("input") or {}
        messages = event.agent.messages   # full conversation incl. toolResult blocks
        return Proceed()

agent = Agent(model="us.anthropic.claude-sonnet-4-6", tools=[...], interventions=[MyGate()])
```
Hooks: `before_invocation`, `before_tool_call`, `after_tool_call` (Proceed|Transform only),
`before_model_call`, `after_model_call`. Only overridden methods are registered.
Actions:
- `Proceed(reason=None)` — run unchanged.
- `Deny(reason="...")` — block; `reason` is shown to the model as the cancellation message.
- `Guide(feedback="...")` — on before_tool_call: cancels the call, model sees feedback and takes another turn.
- `Confirm(prompt="...", response=None)` — before_tool_call only; without `response` the agent pauses for human approval (interrupt).
- `Transform(apply=fn)` — mutate the event in place.

The handler must be fail-closed (`on_error = "deny"`): if the decider server is down, money must not move.

## Upstream reference example
`examples/strands/tool_call_intervention.py` in the decider repo: a `before_tool_call` gate with two
noul questions (`args_grounded`, `premature`), threshold `YES = 0.45`, returning `Guide` or `Proceed`.
Our pattern extends it with **provenance labels**, a **confidence cascade** and **escalation**.
