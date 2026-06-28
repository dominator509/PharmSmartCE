# suggested_commands
- Repo command authority is COMMANDS.md; if a needed command is missing, update COMMANDS.md first with evidence before use.
- On this Windows/Codex environment, honor parent RTK rule from AGENTS.md: prefix external shell commands with 
tk; PowerShell builtins like Get-Content/Get-ChildItem do not need it.
- Preferred search/listing: 
tk rg --files, 
tk rg -n  pattern path; avoid broad slow recursive reads.
- Main documented scripts from repo root: scripts/preflight.sh, scripts/install.sh, scripts/lint.sh, scripts/format-check.sh, scripts/typecheck.sh, scripts/test-unit.sh, scripts/test-integration.sh, scripts/test-e2e.sh, scripts/build.sh, scripts/security-check.sh, scripts/dependency-audit.sh, scripts/smoke-test.sh, scripts/verify.sh, scripts/production-readiness-check.sh.
- Backend command forms used here: python -m uv run --directory apps/api ruff check ., python -m uv run --directory apps/api ruff format --check ., python -m uv run --directory apps/api mypy app, python -m uv run --directory apps/api pytest tests/unit -q, python -m uv run --directory apps/api pytest tests/integration -q, python -m uv run --directory apps/api python -m app.cli.smoke, python -m uv run --directory apps/api alembic upgrade head.
- Frontend command forms: pnpm --filter web lint, pnpm --filter web format:check, pnpm --filter web typecheck, pnpm --filter web test:unit, pnpm --filter web test:e2e, pnpm --filter web build.
- Local services command is docker compose -f infra/docker-compose.yml up -d db redis minio; docker compose -f infra/docker-compose.yml ps is the quick health check; destructive/prod operations are STOP-gated by AGENTS.md.
- Windows file inspection usually goes faster with Get-Content, Get-ChildItem, 
g -n, and 
g --files; use python -m uv when uv is missing from PATH.
- For Serena health checks on this machine, use the UTF-8 wrapper C:\Users\domin\.local\bin\serena.cmd so Click output does not trip CP1252.
