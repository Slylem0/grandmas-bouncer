@AGENTS.md

@.kiro/steering/product.md
@.kiro/steering/hackathon.md
@.kiro/steering/tech.md
@.kiro/steering/structure.md

## Claude Code specifics
- Load `.kiro/steering/decider-api.md` before editing anything under `src/` or `benchmarks/`.
- Delegate by package to the subagents in `.claude/agents/`; give each one the task id from `tasks.md`.
- The Decider server is a long-running process: start it with `run_in_background`, never in the foreground.
- Talk to Pablo in Spanish; write repo content in English.
