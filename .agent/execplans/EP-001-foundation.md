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
- **Validation command:** `grep -c '^[A-Z0-9_]*=' .env.example`
- **Expected result:** Count >= 31.
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
- [x] M1: Bootstrap apps/api - 2026-06-27 - `uv run --directory apps/api pytest tests/unit -q` passed: 1 smoke test.
- [x] M2: Bootstrap apps/web (Next.js 14 + TS + Tailwind) - 2026-06-27 - `pnpm --filter web test:unit` passed: 1 smoke test.
- [x] M3: Create infra/docker-compose.yml - 2026-06-27 - `docker compose -f infra/docker-compose.yml config` parsed successfully.
- [x] M4: Create .env.example - 2026-06-27 - `grep -c '^[A-Z0-9_]*=' .env.example` returned 31; coverage check found no missing `ENVIRONMENT.md` vars.
- [x] M5: Create .github/workflows/ci.yml - 2026-06-27 - `test -f .github/workflows/ci.yml` exited 0.
- [ ] M6: Make scripts/verify.sh green

## 13. Surprises & Discoveries
- 2026-06-27 - M1: `uv` initially tried to use `C:\Users\domin\AppData\Local\uv\cache` and hit permission denied in the managed Codex environment. Setting `UV_CACHE_DIR=C:\dev\PharmSmartCE\.tools\uv-cache` allowed validation to pass; `.tools/` is gitignored.
- 2026-06-27 - M1: First pytest run failed with `ModuleNotFoundError: No module named 'app'`; adding `pythonpath = ["."]` under pytest config fixed the local package import.
- 2026-06-27 - M2: Vitest could not create temp dirs under `C:\tmp` in this managed run; setting `TEMP`/`TMP` to ignored `.tools/tmp` fixed test startup.
- 2026-06-27 - M2: Initial smoke test reached the page but failed with `React is not defined`; importing React explicitly in `app/page.tsx` keeps Vitest's simple render path green.
- 2026-06-27 - M3: Docker Compose config parses, but Docker still warns it cannot read `C:\Users\domin\.docker\config.json` in the managed environment.
- 2026-06-27 - M4: Original validation regex `^[A-Z_]*=` undercounted `.env.example` because variables such as `S3_ENDPOINT` include digits.
- 2026-06-27 - M6: `scripts/verify.sh` passes lint, format, typecheck, unit, integration skip, and E2E, then fails at Docker build because the Docker daemon pipe `npipe:////./pipe/docker_engine` is permission-denied/not ready in this Windows environment. Docker Desktop and `com.docker.service` were started, but `docker version` still reports permission denied connecting to the engine.
- 2026-06-27 - M6: Playwright initially hung after E2E on Windows when using Playwright `webServer` via `pnpm dev`; replacing it with `apps/web/scripts/run-e2e.mjs` made E2E pass and exit cleanly.
(empty — append entries here as they occur)

## 14. Decision Log
- 2026-06-27 - Context: `ENVIRONMENT.md` documents `apps/api/.python-version`, but EP-001 Files to Change omitted it. Decision: Add `apps/api/.python-version` with `3.11` to keep uv aligned with the documented runtime. Alternative: rely on ambient PATH Python (fragile). Consequence: extra file is justified.
- 2026-06-27 - Context: `uv run` generated `apps/api/uv.lock`, but EP-001 Files to Change omitted lockfiles. Decision: Keep and commit the lockfile because repo rules require deterministic package management and forbid floating lock state. Alternative: omit lockfile (non-reproducible). Consequence: extra file is justified.
- 2026-06-27 - Context: API Dockerfile command needs an ASGI server, but EP-001 dependency list omitted `uvicorn`. Decision: Add pinned `uvicorn[standard]==0.32.0`. Alternative: leave image entrypoint broken until later. Consequence: small runtime dependency, exact-pinned.
- 2026-06-27 - Context: `pnpm install` generated `pnpm-lock.yaml`, but EP-001 Files to Change omitted lockfiles. Decision: Keep and commit the lockfile for deterministic Node installs. Alternative: omit lockfile (non-reproducible). Consequence: extra file is justified.
- 2026-06-27 - Context: EP-001 M4 validation command excluded digits in env var names, contradicting `ENVIRONMENT.md` entries such as `S3_ENDPOINT`. Decision: Update the validation regex to `^[A-Z0-9_]*=` and expected count to `>= 31`, matching the authoritative env table. Alternative: add fake env vars without digits (dishonest). Consequence: validation now proves actual coverage.
- 2026-06-27 - Context: CI and fresh local runs need dependencies before `scripts/verify.sh`. Decision: Add `scripts/install.sh` to CI before verify and update `scripts/install.sh` to run `uv sync --directory apps/api --all-extras --frozen`, `pnpm install --frozen-lockfile`, and Playwright Chromium install. Alternative: rely on warm local dependencies (not reproducible). Consequence: command docs and CI now reflect fresh setup.
- 2026-06-27 - Context: Managed Windows environment blocks default user-home caches for uv, Docker config, Playwright browser storage, and Node temp. Decision: Default validation scripts to ignored repo-local `.tools/` cache/temp paths when env vars are unset. Alternative: require manual environment setup for every run. Consequence: scripts are more reliable locally and generated state remains ignored.
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
