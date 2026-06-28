# tech_stack
- Languages: Python 3.11 backend, TypeScript frontend, Markdown control docs, Bash scripts, YAML/JSON config.
- Backend stack in `apps/api/pyproject.toml`: FastAPI 0.138.1, Pydantic 2.9.2, Pydantic Settings 2.5.2, SQLAlchemy 2.0.36, Alembic 1.13.3, asyncpg 0.31.0, structlog 24.4.0, Uvicorn 0.32.0.
- Frontend stack in `apps/web/package.json`: Next.js 15.5.18, React 18.3.1, React DOM 18.3.1, TypeScript 5.6.3, Tailwind 3.4.14, Vitest 2.1.4, Playwright 1.61.1, Prettier 3.3.3, ESLint 8.57.1.
- Runtime/storage: Docker Compose for Postgres 15-alpine, Redis 7-alpine, and MinIO; local data lives under repo-local `var/`-style paths, and uploaded CE docs stay out of git.
- Package managers are fixed by `COMMANDS.md`: Python uses `uv` with `uv.lock`; Node uses `pnpm` with `pnpm-lock.yaml`.
- Dependency additions require exact pins, an audit via `scripts/dependency-audit.sh`, and a Decision Log/ADR entry if the change is non-trivial.
- On Windows, Serena may need the repo-local or user-local shims for `uv`/`uvx` and the UTF-8 `serena.cmd` wrapper for clean startup.