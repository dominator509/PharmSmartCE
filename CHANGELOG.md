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

### Changed
- API Docker image now installs `libmagic1` and uses a multi-stage runtime image.
- Web Docker image now runs the Next standalone server.
- Observability alert rows now point at concrete runbook sections.
- Production readiness checklist now reflects the repo-backed support,
  observability, deployment, and privacy evidence gathered so far.

### Fixed
- Course creation now commits before the upload request boundary, so the smoke and integration paths can see the new course.
- Serena repo configuration now stays headless and avoids the failing Markdown language server on this workstation.
