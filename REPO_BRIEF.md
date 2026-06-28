# PharmSmartCE Repo Brief

Compact durable context for Codex, Serena, and Obsidian links. Authority order
still comes from `AGENTS.md`; this brief is a navigation aid, not a spec.

## Purpose
PharmSmartCE is a planned cloud SaaS for pharmacist continuing education. It
generates dynamic per-user CE questions grounded only in uploaded CE source
material, with every question and rationale linked to a verifiable source
citation.

## Current Repo Shape
This checkout now has the EP-001 empty-app foundation plus the EP-002 pure domain/grounding core, the EP-003 persistence slice, the EP-004 route/service layer, the EP-006 auth/security implementation, the EP-007 hardening pass, and the EP-009 release/deploy scaffolding: root project docs, `.agent/` specs and ExecPlans, command entrypoints, `apps/api`, `apps/web`, `packages/shared`, `infra/docker-compose.yml`, and repo-local Fly configs/workflow files. The backend includes `apps/api/app/domain/`, `apps/api/app/services/generation/`, `apps/api/app/services/rate_limit.py`, `apps/api/app/services/ports/`, `apps/api/app/repositories/`, `apps/api/app/adapters/storage/`, `apps/api/app/cli/`, the deterministic `FakeLLM` adapter, the course/session/auth routes, the smoke CLI, and the initial Alembic migration. The web app currently exposes the smoke-test shell plus the auth and course/upload flows (`/`, `/login`, `/register`, `/auth/complete`, `/courses`, `/courses/[id]`, `/sessions/[id]`).

## Planned Stack
- Backend: Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic, Postgres.
- RAG/storage: FAISS, S3-compatible object storage, local `var/` for dev.
- LLM: self-hosted CPU-only `llama-cpp-python` by default; optional OpenAI
  adapter behind feature flag and cost cap.
- Frontend: Next.js 15 App Router, TypeScript, React Query, Tailwind.
- Tooling: `uv` for Python, `pnpm` for Node, Docker Compose for local services.

## Important Entrypoints
- Agent control: `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`.
- Product and architecture: `PROJECT_BRIEF.md`, `ARCHITECTURE.md`, `.agent/specs/`.
- Execution plans: `.agent/execplans/EP-000-repository-discovery.md` through
  `.agent/execplans/EP-010-production-readiness.md`.
- Operations docs: `ENVIRONMENT.md`, `SECURITY.md`, `TESTING.md`,
  `OBSERVABILITY.md`, `OPERATIONS.md`, `SUPPORT.md`, `DEPLOYMENT.md`,
  `RELEASE.md`, `ROLLBACK.md`, `PRODUCTION_READINESS.md`,
  `PRODUCTION_EVIDENCE.md`.

## Commands
Use only commands documented in `COMMANDS.md`. Key commands:
- Preflight: `scripts/preflight.sh`
- Lint: `scripts/lint.sh`
- Format check: `scripts/format-check.sh`
- Format write: `uv run --directory apps/api ruff format .`
- Typecheck: `scripts/typecheck.sh`
- Unit tests: `scripts/test-unit.sh`
- Integration tests: `scripts/test-integration.sh`
- E2E tests: `scripts/test-e2e.sh`
- Build: `scripts/build.sh`
- Full verification: `scripts/verify.sh`
- Production readiness: `scripts/production-readiness-check.sh`
- Evidence report: `scripts/production-evidence-report.sh [--output PATH]`
- Local DB backup / restore verify: `scripts/backup-restore-check.sh`
- Windows helpers: `scripts/bin/uv.cmd` and `scripts/bin/uvx.cmd` mirror the shell shims; `C:\Users\domin\.local\bin\serena.cmd` forces UTF-8 for Serena health checks on this workstation.

## Important Directories
- `.agent/`: plans, specs, prompts, templates, and checklists.
- `apps/api/`: FastAPI app scaffold with `/healthz`, uv lockfile, Dockerfile,
  smoke test, course/upload routes, domain entities, grounded-generation core,
  SQLAlchemy repositories, Alembic migration, and FAISS storage adapter.
- `apps/api/app/cli/`: release smoke entrypoint used by `scripts/smoke-test.sh`.
  It also now includes `rebuild_index.py` for regenerating FAISS artifacts.
- `apps/web/`: Next.js App Router scaffold with Tailwind, Vitest, Playwright,
  Dockerfile, smoke tests, the `lib/api.ts` / `lib/auth.ts` client bridge, and
  the `lib/courseApi.ts` loader for protected course pages.
- `packages/shared/`: shared package placeholder.
- `infra/`: local Docker Compose services plus Fly deployment templates.
- `.github/workflows/`: CI and release workflows.
- `CHANGELOG.md`: unreleased release notes scaffold.
- `apps/api/app/domain/`: pure entities and errors for CE generation invariants.
- `apps/api/app/services/generation/`: grounded generation, citation validation, and
  RAG retrieval stubs.
- `apps/api/app/observability/`: logging, metrics, and optional Sentry wiring.
- `apps/api/app/services/rate_limit.py`: in-process rate limiter used by auth
  and `/api/*` requests.
- `apps/api/app/services/ports/`: protocols for LLM and embedding adapters.
- `apps/api/app/adapters/llm/`: deterministic FakeLLM adapter used in tests.
- `apps/api/app/api/middleware/`: request-id middleware and HTTP request logging.
- `apps/web/lib/`: fetch wrapper and server-action auth bridge for the web UI.
- `apps/web/app/auth/complete/`: client handoff that stores the browser access
  cookie before redirecting to protected pages.
- `apps/web/app/courses/`: list/detail/upload UI for authenticated course work.
- `apps/api/tests/integration/security/`: authz, rate-limit, refresh-rotation,
  and traceback-leak coverage.
- `apps/api/tests/fixtures/golden_set.jsonl` and
  `apps/api/tests/integration/test_generation_golden.py`: deterministic
  golden-set harness for citation accuracy and uniqueness.
- `scripts/`: documented command entrypoints; scripts enforce repo root.
- `.obsidian/`: local Obsidian vault settings only.
- `.serena/`: repo-local Serena activation/navigation config.

## Guardrails
- Do not implement from `ROADMAP.md`; pick or create an ExecPlan first.
- Do not weaken `AGENTS.md` STOP conditions or source-of-truth order.
- Do not commit secrets, LLM weights (`*.gguf`), uploaded CE documents, FAISS
  indexes, build outputs, dependency folders, caches, or local runtime state.
- Every persisted question must keep non-null citation fields; all LLM calls go
  through `apps/api/app/services/generation/grounded_llm.py` once implemented.
- Production or irreversible migrations require explicit approval per
  `AGENTS.md`.

## Current Unknowns / TODOs
- Staging smoke, rollback drill, and production approval remain external gates
  in `PRODUCTION_READINESS.md`.
- Local `uv` and pytest runs on this Windows session may need repo-local
  `UV_CACHE_DIR` / `TMP` / `TEMP` / `TMPDIR` because the default user temp/cache
  path can deny access.
- `scripts/build.sh` now prefers `docker.exe` on Windows and hands the web
  build to `cmd.exe /c pnpm` when available; plain sandboxed Docker CLI calls
  can still hit daemon pipe permission errors, so verify through the repo
  scripts.
