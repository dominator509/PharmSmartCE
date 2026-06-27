# conventions

- ExecPlan discipline is the main repo convention: one active plan, milestones in order, validate after each milestone, update `Progress`, `Surprises & Discoveries`, `Decision Log`, and final retrospective.
- Anti-drift: edit only files listed in active ExecPlan `Files to Change`; end-state `git diff --name-only` must match or extras must be justified/reverted.
- Anti-hallucination: verify package APIs, route paths, env vars, table/column names, commands, and migration ids from disk/source before using them.
- File creation must follow `ARCHITECTURE.md` repo map; new top-level dirs require architecture update/ADR unless already mapped.
- Security invariants: no secrets in logs/commits; redaction processor for auth bodies; parameterized SQL only; Pydantic validates HTTP inputs; no raw LLM calls outside grounded generation service once implemented.
- Data invariant: persisted `Question` rows require non-null `source_doc_id`, `source_page`, `source_span` at schema and service levels.
- Dependency rule: add only when not already available and not practical in <=50 lines; exact version pins only; audit required.
- Docs rule: changed command -> `COMMANDS.md`; changed route/contract -> `SPEC-003`; changed data model -> `SPEC-002` + Alembic migration; non-trivial architecture -> `DECISIONS.md` ADR.
- Current checkout lacks a `.git` directory in shell view; treat git checks as environment/repo-state evidence until initialized/restored.