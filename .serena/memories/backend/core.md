# backend/core

- Intended root: `apps/api` (currently absent in blueprint checkout).
- Architecture: FastAPI routes call services; services orchestrate domain/repositories/ports; repositories are only SQL location; adapters implement protocols in `app/services/ports`; domain has no I/O/framework imports.
- Key intended entrypoints: `app/main.py` app factory/router mount, `app/config.py` only env reader, `app/services/generation/grounded_llm.py` only outbound LLM prompt path, `alembic/` migrations, `tests/{unit,integration,e2e,fixtures}`.
- Import invariants from `ARCHITECTURE.md`: routes must not call repositories/adapters; services must not import concrete adapters; domain imports nothing upward; raw SQL forbidden outside repositories.
- Generation flow: retrieve source chunks, wrap context delimiters, grounded LLM refuses outside context, citation validator enforces overlap, persist only with source citation fields.
- Tests should use deterministic FakeLLM unless explicitly marked LLM smoke and excluded from CI.