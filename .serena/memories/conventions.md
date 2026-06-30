# Conventions
- Keep changes aligned with `AGENTS.md` and `COMMANDS.md`; do not implement directly from `ROADMAP.md`.
- Update the paired doc when behavior changes: command -> `COMMANDS.md`; route/contract -> `.agent/specs/SPEC-003-api-contracts.md`; data model -> `.agent/specs/SPEC-002-data-model.md` plus Alembic migration; non-trivial architecture -> `DECISIONS.md`.
- Prefer deterministic tests and grounded adapters over live or probabilistic behavior; use `FakeLLM` in normal tests.
- Keep `.obsidian/workspace.json` local-only; treat `.serena/` memories as agent state, not product code.
- Preserve generated/build/cache/secret boundaries in `.gitignore`, `.dockerignore`, and Serena ignored paths; do not broaden ignores to source, tests, docs, config, or important scripts.
- On Windows, repo scripts sometimes need repo-local temp/cache setup; prefer the documented wrappers over ad hoc shell forms.