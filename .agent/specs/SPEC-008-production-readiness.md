# SPEC-008 — Production Readiness

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P9
**Linked ExecPlans:** EP-010

## User-Visible Goal
Confidence that launching the service will not cause customer impact,
data loss, security incident, or runaway cost.

## Required Behaviors
- ALL checklist items in `PRODUCTION_READINESS.md` are ticked.
- `scripts/production-readiness-check.sh` exits 0.
- Staging deploy + smoke + rollback drill completed in the last 30 days.
- Backup verified by test-restore in the last 7 days.
- Synthetic alert firing test green in the last 14 days.

## Required Tests
- `scripts/production-readiness-check.sh` runs `scripts/verify.sh` plus
  additional checks (file presence, `.env.example` completeness, Alembic
  head, no TODO/FIXME in core docs).
- Manual review of each category in `PRODUCTION_READINESS.md`.

## Acceptance Criteria
- [ ] `scripts/production-readiness-check.sh` exit 0.
- [ ] `PRODUCTION_READINESS.md` fully ticked.
- [ ] Human launch gate comment recorded on the release PR.
