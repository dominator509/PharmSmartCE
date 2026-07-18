# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Dockerized API and web release images, plus repo-local `.dockerignore`.
- Fly staging/production deployment configs for API, web, and worker apps.
- Release workflow scaffold that builds images, deploys staging, and gates production.
- API smoke CLI scaffold for local and remote release verification.
- Repo-local support, rollback, and observability docs for launch readiness.
- CE record export documentation in `OPERATIONS.md`.
- Perf guard for the session read route query budget.
- Self-service account deletion via `DELETE /auth/account`.

### Changed
- API Docker image now installs `libmagic1` and uses a multi-stage runtime image.
- Web Docker image now runs the Next standalone server.
- Observability alert rows now point at concrete runbook sections.
- Production readiness checklist now reflects the repo-backed support,
  observability, deployment, and privacy evidence gathered so far.
- Production evidence ledger now requires an explicit rollback-policy row
  before the rollback section can pass its consistency check.

### Fixed
- Course creation now commits before the upload request boundary, so the smoke and integration paths can see the new course.
- Serena repo configuration now stays headless and avoids the failing Markdown language server on this workstation.
- Windows validation no longer lets `pip-audit` fall back to the user-level pip cache, so dependency and production-readiness audits stay green on managed profiles.
- The launch-gate comment unit test now prefers Git Bash and runs from the repo root instead of assuming a WSL `/mnt/c/...` path.
- Backend pytest now uses `--import-mode=importlib`, which avoids duplicate test-module basename collisions during the full coverage audit.
- The web e2e runner now keeps Windows `taskkill` teardown noise out of successful accessibility and smoke runs.
- The security gate now falls back to a repo-local tracked-file secret scan when `gitleaks` is unavailable on the workstation.
- The production evidence ledger now records the current launch-comment template output against the active release-candidate SHA.
- The production evidence ledger now also records fresh local backup/restore and FAISS rebuild proof from the current worktree.
