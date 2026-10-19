# 0001: Serve Decider over HTTP, stdlib client

- Status: accepted (2026-10-19)
- Context: Decider pulls torch + transformers (~GBs). The upstream Strands example (`examples/strands/`) talks to `strands-decider serve` over HTTP with a urllib client.
- Decision: run Decider as a separate process on `:8099`; `decider_patterns.client` uses only the standard library.
- Consequences: the reusable pattern installs with zero heavy deps; the agent can point at a remote or shared Decider; one extra process to start (`scripts/serve_decider.sh`).
