# Suggested commands
- Repo scripts people actually run: `scripts/preflight.sh`, `scripts/install.sh`, `scripts/lint.sh`, `scripts/format-check.sh`, `scripts/typecheck.sh`, `scripts/test-unit.sh`, `scripts/test-integration.sh`, `scripts/test-e2e.sh`, `scripts/build.sh`, `scripts/security-check.sh`, `scripts/dependency-audit.sh`, `scripts/smoke-test.sh`, `scripts/verify.sh`, `scripts/production-readiness-check.sh`, `scripts/production-evidence-report.sh [--output PATH]`.
- Local stack: `docker compose -f infra/docker-compose.yml up -d db redis minio` and `docker compose -f infra/docker-compose.yml ps`.
- Image checks: `docker build -f apps/api/Dockerfile -t pharmsmartce-api:dev .` and `docker build -f apps/web/Dockerfile -t pharmsmartce-web:dev .`.
- Windows helpers: `scripts/bin/uv.cmd`, `scripts/bin/uvx.cmd`, `C:\Users\domin\.local\bin\serena.cmd`.
- After onboarding or memory edits, run `serena memories check` from the project root.