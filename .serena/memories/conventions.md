# conventions
- ExecPlan discipline is the main repo convention: one active plan, milestones in order, validate after each milestone, and update Progress, Surprises & Discoveries, Decision Log, and final retrospective.
- Anti-drift: edit only files listed in the active ExecPlan Files to Change; final `git diff --name-only` must match or extras need justification.
- Anti-hallucination: verify package APIs, route paths, env vars, table/column names, commands, and migration ids from disk/source before using them.
- New files must fit the repo map in `ARCHITECTURE.md`; new top-level dirs need the map updated first unless already covered.
- Security invariants: no secrets in logs/commits; redact auth bodies; parameterized SQL only; Pydantic validates HTTP inputs; all outbound LLM prompts go through grounded generation code once used.
- Data invariant: persisted `Question` rows require non-null `source_doc_id`, `source_page`, and `source_span` at both schema and service levels.
- Docs rule: changed command -> `COMMANDS.md`; changed route/contract -> `.agent/specs/SPEC-003-api-contracts.md`; changed data model -> `.agent/specs/SPEC-002-data-model.md` plus Alembic migration; non-trivial architecture -> `DECISIONS.md` ADR.
- Obsidian/Serena hygiene: `REPO_BRIEF.md` is the compact vault-friendly index; `.serena/project.yml` stays headless, LSP-backed, and should ignore generated/build/cache/local-state paths but not source, tests, docs, config, or scripts.
- `.obsidian/workspace.json` is local editor state only; keep it out of commits unless explicitly requested.