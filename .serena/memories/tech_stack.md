# tech_stack

- Current checkout content: Markdown control docs, `.agent` plan/spec/checklist docs, `apps/api`, `apps/web`, `infra/`, `scripts/`, `REPO_BRIEF.md`, `.serena/`, `.obsidian/`.
- Backend stack now pinned in `apps/api/pyproject.toml`: Python 3.11, FastAPI 0.138.1, Pydantic 2.9.2, Pydantic Settings 2.5.2, SQLAlchemy 2.0.36, Alembic 1.13.3, asyncpg 0.31.0, structlog 24.4.0, Uvicorn 0.32.0.
- Frontend stack pinned in `apps/web/package.json`: Next.js 15.5.18, React 18.3.1, React DOM 18.3.1, TypeScript 5.6.3, Tailwind 3.4.14, Vitest 2.1.4, Playwright 1.61.1, Prettier 3.3.3, ESLint 8.57.1.
- RAG/LLM still targets FAISS, sentence-transformers embeddings, and CPU-only local LLM by default; OpenAI remains optional behind feature flag and cap.
- Local runtime uses Docker Compose for Postgres 15-alpine, Redis 7-alpine, and MinIO; dev data stays in `var/` and uploaded CE docs stay out of git.
- Package managers are fixed by `COMMANDS.md`: Python uses `uv` with `uv.lock`; Node uses `pnpm` with `pnpm-lock.yaml`; in this Windows shell `python -m uv` is the reliable launcher when `uv` is not on PATH.
- Dependency additions require exact pins, audit via `scripts/dependency-audit.sh`, and ADR/Decision Log when non-trivial.