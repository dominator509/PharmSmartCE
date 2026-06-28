# backend/core
- Root is `apps/api`; it contains the FastAPI service, SQLAlchemy repositories, Alembic migrations, and backend tests.
- `app/config.py` is the only env reader; backend defaults currently target local Postgres on `postgresql+asyncpg://app:app@localhost:5432/pharm`.
- `app/repositories/db.py` owns the SQLAlchemy `Base`, engine, and async session factory; SQL stays inside `app/repositories/*`.
- Current model set includes `orgs`, `users`, `refresh_tokens`, `courses`, `sources`, `chunks`, `sessions`, `questions`, `answers`, `ce_records`, and `openai_cost_ledger`.
- `app/services/generation/grounded_llm.py` remains the only allowed outbound LLM prompt path; tests use deterministic `FakeLLM` unless explicitly marked LLM smoke.
- Boundary rule: routes do not call repositories/adapters directly, services depend on ports not concrete adapters, and persisted `Question` rows keep citation fields non-null.
- Alembic bootstrap still needs `prepend_sys_path = .` in `apps/api/alembic.ini` so migrations can import `app` from the API package.