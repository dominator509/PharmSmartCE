# suggested_commands

- Repo command authority is `COMMANDS.md`; if a needed command is missing, update `COMMANDS.md` first with evidence before use.
- On this Windows/Codex environment, honor parent RTK rule from `AGENTS.md`: prefix external shell commands with `rtk`; PowerShell builtins like `Get-Content`/`Get-ChildItem` do not need it.
- Preferred search/listing: `rtk rg --files`, `rtk rg -n "pattern" path`; avoid broad slow recursive reads.
- Main documented scripts from repo root: `scripts/preflight.sh`, `scripts/install.sh`, `scripts/lint.sh`, `scripts/format-check.sh`, `scripts/typecheck.sh`, `scripts/test-unit.sh`, `scripts/test-integration.sh`, `scripts/test-e2e.sh`, `scripts/build.sh`, `scripts/security-check.sh`, `scripts/dependency-audit.sh`, `scripts/smoke-test.sh`, `scripts/verify.sh`, `scripts/production-readiness-check.sh`.
- Underlying backend commands documented for when scripts delegate: `uv run --directory apps/api ruff check .`, `ruff format --check .`, `mypy app`, `pytest tests/unit -q`, `pytest tests/integration -q`, `python -m app.cli.smoke`.
- Underlying frontend commands documented for when scripts delegate: `pnpm --filter web lint`, `format:check`, `typecheck`, `test:unit`, `test:e2e`, `build`.
- Local services command is documented as `docker compose -f infra/docker-compose.yml up -d db redis minio`; destructive/prod operations are STOP-gated by `AGENTS.md`.