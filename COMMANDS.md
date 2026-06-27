# COMMANDS.md — Exact Allowed Commands

**Coding agents MUST NOT invent commands.** If a command you need is not
listed, update this file first with evidence from the repository (the
`pyproject.toml` script entry, `package.json` script block, or installed
CLI's `--help`), then use it.

## Working Directory Rule
All commands run from the **repository root** unless explicitly noted.
Scripts in `scripts/` enforce this with
`cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`.

## Package Manager Rule
- Python: `uv` (lockfile `uv.lock`).
- Node:   `pnpm` (lockfile `pnpm-lock.yaml`).

Do not use `pip install`, `npm install`, `yarn`.

## Quick Reference

| Purpose | Command |
|---|---|
| Preflight | `scripts/preflight.sh` |
| Install all deps | `scripts/install.sh` |
| Lint | `scripts/lint.sh` |
| Format check | `scripts/format-check.sh` |
| Typecheck | `scripts/typecheck.sh` |
| Unit tests | `scripts/test-unit.sh` |
| Integration tests | `scripts/test-integration.sh` |
| E2E tests | `scripts/test-e2e.sh` |
| Build | `scripts/build.sh` |
| Security check | `scripts/security-check.sh` |
| Dependency audit | `scripts/dependency-audit.sh` |
| Smoke test | `scripts/smoke-test.sh` |
| Full verification | `scripts/verify.sh` |
| Production readiness check | `scripts/production-readiness-check.sh` |

## Underlying Tool Commands

| Layer | Command |
|---|---|
| Python install | `uv sync --directory apps/api --all-extras --frozen` |
| Python lock refresh | `uv lock --directory apps/api` |
| Node install | `pnpm install --frozen-lockfile` |
| Node lock refresh | `pnpm install --lockfile-only` |
| Python lint | `uv run --directory apps/api ruff check .` |
| Python format check | `uv run --directory apps/api ruff format --check .` |
| Python typecheck | `uv run --directory apps/api mypy app` |
| Python unit tests | `uv run --directory apps/api pytest tests/unit -q` |
| Python integration tests | `uv run --directory apps/api pytest tests/integration -q` |
| Node lint | `pnpm --filter web lint` |
| Node format check | `pnpm --filter web format:check` |
| Node typecheck | `pnpm --filter web typecheck` |
| Node unit tests | `pnpm --filter web test:unit` |
| E2E (Playwright) | `pnpm --filter web test:e2e` |
| API image build | `docker build -f apps/api/Dockerfile -t pharmsmartce-api:dev .` |
| Web build | `pnpm --filter web build` |
| Python security | `uv run --directory apps/api pip-audit` |
| Node security | `pnpm audit --prod` |
| Smoke | `uv run --directory apps/api python -m app.cli.smoke` |

## Local Development

```sh
docker compose -f infra/docker-compose.yml up -d db redis minio
uv run --directory apps/api uvicorn app.main:app --reload --port 8000
pnpm --filter web dev
uv run --directory apps/api python -m app.workers.main
```

## Local Database Setup

```sh
docker compose -f infra/docker-compose.yml up -d db
uv run --directory apps/api alembic upgrade head
uv run --directory apps/api python -m app.cli.seed_dev
```

## Migrations

```sh
uv run --directory apps/api alembic revision --autogenerate -m "<desc>"
uv run --directory apps/api alembic upgrade head
uv run --directory apps/api alembic downgrade -1   # LOCAL ONLY
```

Forbidden outside local: `alembic downgrade base`, `alembic stamp` against
staging/prod.

## Forbidden Commands

- `rm -rf /`, `rm -rf ~`, anything outside this repo
- `git push --force` against `main` or any protected branch
- `DROP DATABASE`, `DROP SCHEMA`, `TRUNCATE` against non-local DBs
- `alembic downgrade base` against non-local DBs
- `aws s3 rm --recursive`, `fly destroy`, `flyctl secrets unset` in prod
- `docker system prune -a`
- `pip install` (use uv), `npm install` / `yarn` (use pnpm)
- `git reset --hard` while there are uncommitted changes the agent did not make

## Recovery

| Symptom | Action |
|---|---|
| `uv` not found | Re-run `scripts/install.sh`. Still missing → S1. |
| `pnpm` not found | Re-run `scripts/install.sh`. Still missing → S1. |
| `docker` not found | S1. |
| `models/*.gguf` missing | Re-run `scripts/install.sh`. If blocked → S1. |
| Migration fails locally | Check `alembic current`; forward-fix. Never `downgrade base`. |
| Tests flake | Run `-p no:randomly` or `--repeat 3`. Else quarantine per `TESTING.md`. |
| `OPENAI_MONTHLY_USD_CAP` exceeded | Auto-fallback to local LLM. Do not raise the cap (S3). |
