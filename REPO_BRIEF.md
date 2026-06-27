# PharmSmartCE Repo Brief

Compact durable context for Codex, Serena, and Obsidian links. Authority order
still comes from `AGENTS.md`; this brief is a navigation aid, not a spec.

## Purpose
PharmSmartCE is a planned cloud SaaS for pharmacist continuing education. It
generates dynamic per-user CE questions grounded only in uploaded CE source
material, with every question and rationale linked to a verifiable source
citation.

## Current Repo Shape
This checkout now has the EP-001 empty-app foundation in place: root project
docs, `.agent/` specs and ExecPlans, command entrypoints, `apps/api`,
`apps/web`, `packages/shared`, and `infra/docker-compose.yml`. Domain logic,
database schema, auth, deployment, and production readiness remain later
ExecPlan work.

## Planned Stack
- Backend: Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic, Postgres.
- RAG/storage: FAISS, S3-compatible object storage, local `var/` for dev.
- LLM: self-hosted CPU-only `llama-cpp-python` by default; optional OpenAI
  adapter behind feature flag and cost cap.
- Frontend: Next.js 14 App Router, TypeScript, React Query, Tailwind.
- Tooling: `uv` for Python, `pnpm` for Node, Docker Compose for local services.

## Important Entrypoints
- Agent control: `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`.
- Product and architecture: `PROJECT_BRIEF.md`, `ARCHITECTURE.md`, `.agent/specs/`.
- Execution plans: `.agent/execplans/EP-000-repository-discovery.md` through
  `.agent/execplans/EP-010-production-readiness.md`.
- Operations docs: `ENVIRONMENT.md`, `SECURITY.md`, `TESTING.md`,
  `OBSERVABILITY.md`, `OPERATIONS.md`, `DEPLOYMENT.md`, `RELEASE.md`,
  `ROLLBACK.md`, `PRODUCTION_READINESS.md`.

## Commands
Use only commands documented in `COMMANDS.md`. Key commands:
- Preflight: `scripts/preflight.sh`
- Lint: `scripts/lint.sh`
- Format check: `scripts/format-check.sh`
- Typecheck: `scripts/typecheck.sh`
- Unit tests: `scripts/test-unit.sh`
- Integration tests: `scripts/test-integration.sh`
- E2E tests: `scripts/test-e2e.sh`
- Build: `scripts/build.sh`
- Full verification: `scripts/verify.sh`
- Production readiness: `scripts/production-readiness-check.sh`

## Important Directories
- `.agent/`: plans, specs, prompts, templates, and checklists.
- `apps/api/`: FastAPI app scaffold with `/healthz`, uv lockfile, Dockerfile,
  and smoke test.
- `apps/web/`: Next.js App Router scaffold with Tailwind, Vitest, Playwright,
  Dockerfile, and smoke tests.
- `packages/shared/`: shared package placeholder.
- `infra/`: local Docker Compose services for Postgres, Redis, and MinIO.
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
- Determine the active ExecPlan when implementation resumes; README points to
  `.agent/execplans/` but no active marker file exists.
- Confirm whether Pack 1/Pack 2 have been converted into an initialized Git
  repository before relying on `git diff` or `git status`.
- Docker works for repository verification through the unsandboxed command path
  in the current Windows setup; plain sandboxed Docker CLI calls still receive
  daemon pipe permission errors.
