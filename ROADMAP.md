# ROADMAP.md

## ⚠️ DO NOT IMPLEMENT FROM THIS FILE

This roadmap is **strategic only**. Implementation MUST happen through an
active ExecPlan in `.agent/execplans/`. An agent that opens this file
looking for "what to build next" must immediately switch to the active
ExecPlan. If an ExecPlan is missing for a phase, create one from
`.agent/templates/execplan-template.md` first.

## Phase Map

| Phase | Name | ExecPlans | Specs |
|---|---|---|---|
| P0 | Repository Discovery & Foundation | EP-000, EP-001 | SPEC-000 |
| P1 | Core Domain + LLM/RAG Plumbing | EP-002 | SPEC-001 |
| P2 | Data & Persistence | EP-003 | SPEC-002 |
| P3 | API / Service Layer | EP-004 | SPEC-003, SPEC-006 |
| P4 | UI / Client Layer | EP-005 | SPEC-004 |
| P5 | Auth, Permissions, Security | EP-006 | SPEC-005 |
| P6 | Testing Hardening | EP-007 | (cross-cutting) |
| P7 | Observability & Operations | EP-008 | SPEC-007 |
| P8 | Deployment & Release | EP-009 | (cross-cutting) |
| P9 | Production Readiness | EP-010 | SPEC-008 |

## P0 — Repository Discovery & Foundation
- **Purpose:** Inventory greenfield repo; bootstrap `apps/api`, `apps/web`,
  `infra`, `scripts`. Make `verify.sh` green at empty-app level.
- **Deps:** none.
- **Exit:** `preflight.sh`/`install.sh` succeed on fresh clone; `verify.sh`
  green; CI workflow present and green; `.env.example` covers all vars.

## P1 — Core Domain + LLM/RAG
- **Purpose:** Domain entities + `GroundedLLM` + `RAGRetriever` +
  `CitationValidator` + `FakeLLM`. In-memory; no DB.
- **Deps:** P0.
- **Exit:** Unit tests cover all invariants; `GroundedLLM` refuses outside
  context; `CitationValidator` rejects misaligned citations; latency
  benchmark documented.

## P2 — Data & Persistence
- **Purpose:** Postgres schema + Alembic + repositories + integration tests;
  FAISS persistence.
- **Deps:** P1.
- **Exit:** Entities have repos; migrations apply from empty DB and
  round-trip; integration tests via testcontainers; citation NOT NULL
  verified by a failing-then-passing test.

## P3 — API / Service Layer
- **Purpose:** FastAPI routes for course CRUD, session start, question fetch,
  answer submit.
- **Deps:** P2.
- **Exit:** OpenAPI committed at `apps/api/openapi.json`; contract tests
  pass; RFC 7807 errors.

## P4 — UI / Client Layer
- **Purpose:** Next.js pages for login, course list, course detail, session,
  results.
- **Deps:** P3.
- **Exit:** Playwright happy path green; Lighthouse mobile ≥ 80 (informational).

## P5 — Auth, Permissions, Security
- **Purpose:** Email/password + Argon2id + JWT + refresh; per-route authz;
  rate limits; security headers; OpenAI cost cap circuit breaker.
- **Deps:** P3.
- **Exit:** All routes default-deny without auth; refresh rotation tested;
  `security-check.sh` clean.

## P6 — Testing Hardening
- **Purpose:** Raise coverage; regression; golden-set eval harness.
- **Deps:** P3.
- **Exit:** Backend coverage ≥ 80%; golden-set citation accuracy ≥ 99%,
  uniqueness ≥ 95%.

## P7 — Observability & Operations
- **Purpose:** structlog, `/healthz`, `/readyz`, `/metrics`, Sentry, runbooks.
- **Deps:** P3.
- **Exit:** Health endpoints differentiate liveness vs readiness; named
  metrics scraped; runbooks present.

## P8 — Deployment & Release
- **Purpose:** Docker images, Fly.io staging, smoke, promote to prod.
- **Deps:** P5, P7.
- **Exit:** `smoke-test.sh` against staging passes; rollback drill executed.

## P9 — Production Readiness
- **Purpose:** Final gates: security, perf, backup verify, monitoring verify,
  doc review.
- **Deps:** all prior.
- **Exit:** `production-readiness-check.sh` passes; all items in
  `PRODUCTION_READINESS.md` ticked.

## Production Readiness Milestone
When P9 exits successfully and the launch checklist in
`PRODUCTION_READINESS.md` is fully ticked, the system is
**Production-Ready**. The launch decision itself is a human decision (S3/S6).
