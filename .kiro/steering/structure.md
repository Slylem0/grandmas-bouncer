---
inclusion: always
---

# Repository structure and conventions

```
.
├── AGENTS.md                     # Entry point for any AI coding agent (Claude Code, Kiro, Codex)
├── CLAUDE.md                     # Claude Code entry: imports AGENTS.md + steering
├── README.md                     # Public README (English) for judges and builders
├── .kiro/
│   ├── steering/                 # Shared project context (single source of truth)
│   │   ├── product.md            #   what & why
│   │   ├── tech.md               #   stack, env, models, commands, risks
│   │   ├── structure.md          #   this file
│   │   ├── decider-api.md        #   verified Decider + interventions API
│   │   └── hackathon.md          #   rules, rubric, deliverables, deadline
│   └── specs/grandmas-bouncer/   # Kiro spec: requirements.md, design.md, tasks.md
├── .claude/agents/               # Claude Code subagents (one role each)
├── docs/
│   ├── decisions/                # ADRs: NNNN-title.md, append-only
│   ├── article/                  # Builder Center article draft + video script
│   └── progress.md               # Running log: what was done, what is next, blockers
├── src/
│   ├── decider_patterns/         # THE REUSABLE ASSET. No dependency on grandmas_bouncer.
│   │   ├── client.py             #   tiny sync HTTP client (urllib, like upstream)
│   │   ├── grounding_guard.py    #   GroundingGuard(InterventionHandler)
│   │   ├── provenance.py         #   render conversation with TRUSTED/UNTRUSTED labels
│   │   ├── cascade.py            #   thresholds -> verdict (pure functions)
│   │   └── README.md             #   the recipe: question, options, wiring, how to use
│   └── grandmas_bouncer/         # The demo agent (depends on decider_patterns)
│       ├── config.py             #   model ids, thresholds, URLs (env-overridable)
│       ├── world.py              #   fake bank, inbox, payees, contacts (in-memory)
│       ├── tools.py              #   @tool functions: read_inbox, list_payees, transfer_money, send_email, add_payee
│       ├── agent.py              #   build_agent(): Strands Agent + Bedrock + GroundingGuard
│       ├── demo_cli.py           #   rich terminal demo
│       └── web/                  #   FastAPI app + single static HTML page
├── scenarios/                    # Benchmark cases, YAML, one file per category
├── benchmarks/                   # run.py, judges (decider / bedrock llm), metrics, results/
├── scripts/                      # setup and helper shell scripts
└── tests/                        # pytest; markers: decider, bedrock
```

## Conventions
- Language: **code, comments, docs, commits in English** (public judges). Chat with the user in Spanish.
- `decider_patterns` must stay importable on its own: no imports from `grandmas_bouncer`.
- Pure logic (cascade, provenance rendering, metrics) is unit-tested without network.
- Network tests are marked `@pytest.mark.decider` or `@pytest.mark.bedrock`.
- Config via env vars with defaults in `config.py`; no secrets in the repo.
- Fake data only: fictional names, companies and IBAN-like strings (use the `XX00` test prefix style, never real accounts).
- **Never invent numbers.** Every metric in README/article comes from `benchmarks/results/` and names the device.
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), small and focused.
- After finishing a task: tick it in `.kiro/specs/grandmas-bouncer/tasks.md` and append to `docs/progress.md`.
- Significant decisions (model choice, threshold policy, architecture change) get an ADR in `docs/decisions/`.
