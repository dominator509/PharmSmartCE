# Backend core
- Backend lives in `apps/api`; FastAPI app, SQLAlchemy/Alembic persistence, auth, observability, CLI entrypoints, deterministic `FakeLLM`, and grounded generation helpers all sit under that tree.
- Key entrypoints: `app.main:app`, `app.cli.smoke`, `app.cli.rebuild_index`, and `app.cli.evidence_report`.
- The only sanctioned LLM boundary is `apps/api/app/services/generation/grounded_llm.py`; tests use `FakeLLM` unless a smoke test is explicitly marked.
- Persistence invariants matter: `Question` rows must keep non-null source citation fields (`source_doc_id`, `source_page`, `source_span`).
- Local dev depends on dockerized Postgres/Redis/MinIO from `infra/docker-compose.yml`; Windows often needs repo-local temp/cache paths for `uv`/pytest.