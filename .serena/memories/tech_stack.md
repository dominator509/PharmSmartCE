# tech_stack

- Current checkout content: Markdown control docs, `.agent` plan/spec/checklist docs, POSIX shell scripts under `scripts/`, Obsidian settings, Serena config.
- Planned backend: Python 3.11, FastAPI, Pydantic/Pydantic Settings, SQLAlchemy, Alembic, Postgres, structlog, Prometheus, OTel/Sentry hooks.
- Planned RAG/LLM: FAISS, sentence-transformers embeddings, `llama-cpp-python` CPU-only default, optional OpenAI adapter off by default with feature flag + monthly USD cap.
- Planned storage/runtime: S3-compatible object storage, local `var/uploads` and `var/faiss` in dev, Redis/background workers, Docker Compose for local db/redis/minio.
- Planned frontend: Next.js 14 App Router, TypeScript, React Query, Tailwind; shared TS types generated from OpenAPI into `packages/shared`.
- Package managers are fixed by `COMMANDS.md`: Python uses `uv` with `uv.lock`; Node uses `pnpm` with `pnpm-lock.yaml`; no pip/npm/yarn installs.
- Dependency additions require exact pins, audit via `scripts/dependency-audit.sh`, and ADR/Decision Log when non-trivial.