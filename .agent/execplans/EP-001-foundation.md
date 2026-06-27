# EP-001 — Foundation

**Phase:** P0

## 1. Purpose / Big Picture
Bootstrap the FastAPI backend (`apps/api`), Next.js frontend (`apps/web`), local infra (`infra/docker-compose.yml`), `.env.example`, and the CI workflow so that `scripts/verify.sh` is green at the empty-app level.

## 2. Scope
- Create `apps/api` with FastAPI + uv + ruff + mypy + pytest + structlog
- Create `apps/web` with Next.js 14 + TS + Tailwind + ESLint + Prettier + Vitest + Playwright
- Create `infra/docker-compose.yml` (Postgres 15, Redis 7, MinIO)
- Create `.env.example` covering every variable in `ENVIRONMENT.md`
- Create `.github/workflows/ci.yml` that runs `scripts/verify.sh`
- Make `scripts/verify.sh` green end-to-end

## 3. Non-goals
- Implementing domain logic (EP-002)
- Implementing database schema (EP-003)
- Authentication (EP-006)
- Deployment (EP-009)

## 4. Context and Orientation
Repository is empty after EP-000. This plan creates the smallest possible two-app scaffold that passes `scripts/verify.sh`. No feature code.

## 5. Files to Read First
- `AGENTS.md`
- `ARCHITECTURE.md`
- `COMMANDS.md`
- `ENVIRONMENT.md`
- `scripts/verify.sh`

## 6. Files to Change
- `apps/api/pyproject.toml`
- `apps/api/app/main.py`
- `apps/api/app/config.py`
- `apps/api/app/__init__.py`
- `apps/api/tests/unit/test_smoke.py`
- `apps/api/Dockerfile`
- `apps/web/package.json`
- `apps/web/tsconfig.json`
- `apps/web/next.config.mjs`
- `apps/web/tailwind.config.ts`
- `apps/web/app/page.tsx`
- `apps/web/app/layout.tsx`
- `apps/web/tests/unit/smoke.test.ts`
- `apps/web/playwright.config.ts`
- `apps/web/Dockerfile`
- `packages/shared/package.json`
- `pnpm-workspace.yaml`
- `infra/docker-compose.yml`
- `.env.example`
- `.github/workflows/ci.yml`

## 7. Interfaces and Contracts
FastAPI app exposes `/healthz` returning `{"status":"ok"}`. Next.js renders an empty home page. No DB or external calls.

## 8. Milestones

### M1: Bootstrap apps/api
- **Files to read:** `ARCHITECTURE.md`, `ENVIRONMENT.md`
- **Files to change:** `apps/api/pyproject.toml`, `apps/api/app/main.py`, `apps/api/app/config.py`, `apps/api/app/__init__.py`, `apps/api/tests/unit/test_smoke.py`
- **Exact edits expected:** pyproject pins fastapi==0.115.4, pydantic==2.9.*, pydantic-settings==2.5.*, sqlalchemy==2.0.*, alembic==1.13.*, structlog==24.*, ruff, mypy, pytest, pytest-cov, httpx. main.py creates FastAPI app and mounts `/healthz`. config.py defines `Settings(BaseSettings)` skeleton with `APP_ENV`, `LOG_LEVEL`. smoke test asserts `/healthz` returns 200.
- **Validation command:** `uv run --directory apps/api pytest tests/unit -q`
- **Expected result:** 1 passed.
- **Recovery:** If imports fail, run `uv sync` again. If still failing, narrow with `pytest -x -vv`.

### M2: Bootstrap apps/web (Next.js 14 + TS + Tailwind)
- **Files to read:** `ARCHITECTURE.md`
- **Files to change:** `apps/web/package.json`, `apps/web/tsconfig.json`, `apps/web/next.config.mjs`, `apps/web/tailwind.config.ts`, `apps/web/app/page.tsx`, `apps/web/app/layout.tsx`, `apps/web/tests/unit/smoke.test.ts`, `apps/web/playwright.config.ts`, `packages/shared/package.json`, `pnpm-workspace.yaml`
- **Exact edits expected:** package.json declares next, react, react-dom, typescript, tailwindcss, eslint, prettier, vitest, @playwright/test (pinned). Scripts: dev, build, start, lint, format:check, typecheck, test:unit, test:e2e. Home page renders an h1 'PharmSmartCE'. Smoke test asserts a known DOM string. pnpm-workspace.yaml lists apps/* and packages/*.
- **Validation command:** `pnpm --filter web test:unit`
- **Expected result:** 1 passed.
- **Recovery:** If vitest is missing, re-run `pnpm install --frozen-lockfile`. If pnpm workspace missing, ensure `pnpm-workspace.yaml` lists `apps/*` and `packages/*`.

### M3: Create infra/docker-compose.yml
- **Files to read:** `ENVIRONMENT.md`
- **Files to change:** `infra/docker-compose.yml`
- **Exact edits expected:** Services: db (postgres:15-alpine), redis (redis:7-alpine), minio (minio/minio). Volumes: pharm_pg_data, pharm_minio_data. Healthchecks.
- **Validation command:** `docker compose -f infra/docker-compose.yml config`
- **Expected result:** Compose file parses without error.
- **Recovery:** If yaml invalid, fix and re-run.

### M4: Create .env.example
- **Files to read:** `ENVIRONMENT.md`
- **Files to change:** `.env.example`
- **Exact edits expected:** Every variable from ENVIRONMENT.md table with placeholder values (no secrets).
- **Validation command:** `grep -c '^[A-Z_]*=' .env.example`
- **Expected result:** Count >= 30.
- **Recovery:** If count low, cross-check against ENVIRONMENT.md and add missing rows.

### M5: Create .github/workflows/ci.yml
- **Files to read:** `COMMANDS.md`
- **Files to change:** `.github/workflows/ci.yml`
- **Exact edits expected:** Workflow on push + pull_request: setup-python 3.11, setup-node 20, install uv + pnpm, run scripts/verify.sh.
- **Validation command:** `test -f .github/workflows/ci.yml`
- **Expected result:** File exists.
- **Recovery:** If actions runner cannot install uv/pnpm, use the official actions astral-sh/setup-uv and pnpm/action-setup.

### M6: Make scripts/verify.sh green
- **Files to read:** `scripts/verify.sh`
- **Files to change:** (none)
- **Exact edits expected:** No file edits expected; this is the end-to-end gate.
- **Validation command:** `scripts/verify.sh`
- **Expected result:** Final line `verify: ok`. Exit 0.
- **Recovery:** If a sub-script fails, fix that script's milestone first. Apply bounded retry per AGENTS §7.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] `scripts/verify.sh` exits 0
  - [ ] `apps/api/tests/unit/test_smoke.py` passes
  - [ ] `apps/web/tests/unit/smoke.test.ts` passes
  - [ ] CI workflow file exists at `.github/workflows/ci.yml`
  - [ ] `.env.example` contains every required env var

## 11. Idempotence and Recovery
Re-running the plan is safe: bootstrap files overwritten verbatim; tests are deterministic; CI workflow re-applies idempotently.

## 12. Progress
- [ ] M1: Bootstrap apps/api
- [ ] M2: Bootstrap apps/web (Next.js 14 + TS + Tailwind)
- [ ] M3: Create infra/docker-compose.yml
- [ ] M4: Create .env.example
- [ ] M5: Create .github/workflows/ci.yml
- [ ] M6: Make scripts/verify.sh green

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
