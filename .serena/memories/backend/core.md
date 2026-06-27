# backend/core

- Root is `apps/api`; it now contains the FastAPI service, SQLAlchemy repositories, Alembic migrations, and unit tests.
- `app/config.py` is the only env reader; backend defaults currently include `database_url = postgresql+asyncpg://app:app@localhost:5432/pharm` for local host-mapped Postgres.
- `app/repositories/db.py` owns the SQLAlchemy `Base`, engine, and async session factory; all SQL should stay inside `app/repositories/*`.
- Current model set includes `orgs`, `users`, `refresh_tokens`, `courses`, `sources`, `chunks`, `sessions`, `questions`, `answers`, `ce_records`, and `openai_cost_ledger`.
- `app/services/generation/grounded_llm.py` remains the only allowed outbound LLM prompt path; tests use deterministic `FakeLLM` unless explicitly marked LLM smoke.
- Import and boundary rules from `ARCHITECTURE.md` still hold: routes do not call repositories/adapters directly, services depend on ports not concrete adapters, domain stays pure, and persisted `Question` rows keep non-null citation fields.
- Alembic bootstrap needs `prepend_sys_path = .` in `apps/api/alembic.ini` so migrations can import `app` when run from the API package.