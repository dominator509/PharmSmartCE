# Tech stack
- Backend: Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic, uvicorn, pytest, ruff, mypy, faiss-cpu, argon2-cffi.
- Frontend: Next.js 15 App Router, React 18, TypeScript 5.6, Tailwind, Vitest, Playwright, ESLint.
- Package managers: `uv` for Python (`uv.lock`), `pnpm@9.15.0` for Node (`pnpm-lock.yaml`).
- Runtime/images: `python:3.11-slim` API image, `node:20-alpine` web image, local infra in `infra/docker-compose.yml`.
- Serena uses LSP backend for this project; languages in play are python, typescript, bash, yaml, json, markdown.