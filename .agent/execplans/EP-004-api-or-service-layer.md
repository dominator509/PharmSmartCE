# EP-004 — API and Service Layer

**Phase:** P3

## 1. Purpose / Big Picture
Implement FastAPI routes, service layer, exception handlers, and the OpenAPI snapshot per `SPEC-003` and `SPEC-006`. Auth route stubs land here; full auth implementation in EP-006.

## 2. Scope
- AppException hierarchy + RFC 7807 handlers
- Health + metrics routes
- Course CRUD and source upload routes
- Session start / get / answer routes
- Services: AuthService, GenerationService, IngestService, SessionService
- Background ingest worker entrypoint
- Committed OpenAPI snapshot + drift test

## 3. Non-goals
- Full auth implementation (EP-006)
- UI work (EP-005)
- Deployment (EP-009)

## 4. Context and Orientation
Builds on EP-002 (domain) and EP-003 (repos + FAISS). Routes are thin: validate via Pydantic → call service → map exceptions.

## 5. Files to Read First
- `AGENTS.md`
- `ARCHITECTURE.md`
- `.agent/specs/SPEC-003-api-contracts.md`
- `.agent/specs/SPEC-006-error-handling.md`

## 6. Files to Change
- `apps/api/app/api/__init__.py`
- `apps/api/app/api/errors.py`
- `apps/api/app/api/handlers.py`
- `apps/api/app/api/deps.py`
- `apps/api/app/api/routes/health.py`
- `apps/api/app/api/routes/auth.py`
- `apps/api/app/api/routes/courses.py`
- `apps/api/app/api/routes/sessions.py`
- `apps/api/app/services/auth/__init__.py`
- `apps/api/app/services/auth/service.py`
- `apps/api/app/services/generation/service.py`
- `apps/api/app/services/ingest/service.py`
- `apps/api/app/services/session/__init__.py`
- `apps/api/app/services/session/service.py`
- `apps/api/app/workers/__init__.py`
- `apps/api/app/workers/ingest.py`
- `apps/api/app/main.py`
- `apps/api/openapi.json`
- `apps/api/tests/integration/api/test_health.py`
- `apps/api/tests/integration/api/test_courses.py`
- `apps/api/tests/integration/api/test_sessions.py`
- `apps/api/tests/integration/api/test_error_shape.py`
- `apps/api/tests/integration/test_openapi_snapshot.py`

## 7. Interfaces and Contracts
Routes return Pydantic response models matching `SPEC-003`. Service methods are async and accept repository instances via DI. Errors translate to RFC 7807 problem+json with `type`, `title`, `status`, `detail`, `instance`, `request_id`.

## 8. Milestones

### M1: AppException hierarchy + RFC 7807 handlers
- **Files to read:** `.agent/specs/SPEC-006-error-handling.md`
- **Files to change:** `apps/api/app/api/errors.py`, `apps/api/app/api/handlers.py`
- **Exact edits expected:** errors.py defines AppException + subclasses (NotFoundError, AuthError, AuthorizationError, ValidationError, RateLimitError, ExternalServiceError, GroundingError, ConflictError). handlers.py registers exception handlers in main.py; each builds problem+json with the request_id from contextvars.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/api/test_error_shape.py -q`
- **Expected result:** All taxonomy entries return problem+json with correct status.
- **Recovery:** If a handler is not invoked, ensure it is registered before the routes.

### M2: Health, readiness, metrics routes
- **Files to read:** `OBSERVABILITY.md`, `OPERATIONS.md`
- **Files to change:** `apps/api/app/api/routes/health.py`, `apps/api/app/main.py`
- **Exact edits expected:** health.py exposes `/healthz` returning `{status: ok}`; `/readyz` checks DB (SELECT 1 with 500ms timeout) + FAISS dir + LLM warm flag; `/metrics` exposes Prometheus output. main.py mounts the router.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/api/test_health.py -q`
- **Expected result:** /healthz 200; /readyz 200 when subsystems up, 503 when one down (induced by fixture).
- **Recovery:** If /readyz timing flaky, raise timeout to 1s and document in Decision Log.

### M3: Auth route stubs
- **Files to read:** `.agent/specs/SPEC-003-api-contracts.md`
- **Files to change:** `apps/api/app/api/routes/auth.py`, `apps/api/app/services/auth/__init__.py`, `apps/api/app/services/auth/service.py`
- **Exact edits expected:** Endpoints accept Pydantic DTOs and call AuthService stubs that raise NotImplementedError. Full implementation deferred to EP-006. Contract test exists for the request shape and a 501 response code.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/api -q -k 'auth and stub'`
- **Expected result:** Auth stub tests pass (501 with problem+json shape).
- **Recovery:** If shape mismatch, fix the DTO; do not loosen the test.

### M4: Course routes and CourseService
- **Files to read:** `.agent/specs/SPEC-003-api-contracts.md`, `.agent/specs/SPEC-002-data-model.md`
- **Files to change:** `apps/api/app/api/routes/courses.py`, `apps/api/app/api/deps.py`
- **Exact edits expected:** GET /api/courses, GET /api/courses/{id}, POST /api/courses (admin), POST /api/courses/{id}/sources (multipart). deps.py provides `current_user` and `current_admin` Depends. Multipart upload validates size + python-magic sniff; persists via StorageAdapter; enqueues ingest job.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/api/test_courses.py -q`
- **Expected result:** Course CRUD + upload tests pass.
- **Recovery:** If multipart parsing fails, ensure `python-multipart` is in pyproject.toml.

### M5: Session routes and GenerationService
- **Files to read:** `.agent/specs/SPEC-001-core-domain.md`, `.agent/specs/SPEC-003-api-contracts.md`
- **Files to change:** `apps/api/app/api/routes/sessions.py`, `apps/api/app/services/generation/service.py`, `apps/api/app/services/session/service.py`
- **Exact edits expected:** POST /api/sessions/{course_id}/start triggers GenerationService.start_session(user, course_id) which retrieves chunks, generates questions via GroundedLLM, validates with CitationValidator, retries up to GENERATION_RETRY_BUDGET, persists, returns SessionDTO with citation URLs. POST /api/sessions/{id}/answers records and scores via SessionService.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/api/test_sessions.py -q`
- **Expected result:** Session lifecycle test passes with FakeLLM.
- **Recovery:** If generation exceeds retry budget for the fixture, raise budget temporarily and document in Decision Log.

### M6: Ingest worker
- **Files to read:** `ARCHITECTURE.md`
- **Files to change:** `apps/api/app/workers/__init__.py`, `apps/api/app/workers/ingest.py`, `apps/api/app/services/ingest/service.py`
- **Exact edits expected:** IngestService.enqueue persists a job row. Worker polls (Redis or DB queue) and processes via pdf extract → chunk → embed → faiss persist. Idempotency key = source.sha256.
- **Validation command:** `uv run --directory apps/api pytest tests/integration -q -k ingest`
- **Expected result:** Ingest happy-path test passes against testcontainers Postgres.
- **Recovery:** If pdf parser flaky on a fixture, swap fixture; do not patch parser.

### M7: OpenAPI snapshot
- **Files to read:** (none new)
- **Files to change:** `apps/api/openapi.json`, `apps/api/tests/integration/test_openapi_snapshot.py`
- **Exact edits expected:** Test calls `app.openapi()` and compares to the committed `openapi.json`. Failing the snapshot is a signal to update both files in the same change.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/test_openapi_snapshot.py -q`
- **Expected result:** Snapshot matches.
- **Recovery:** If routes legitimately changed, regenerate snapshot and document the change in PR description.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] All contract tests pass
  - [ ] OpenAPI snapshot committed and stable
  - [ ] Authz dependencies in place (full enforcement in EP-006)
  - [ ] Generation happy path passes with FakeLLM
  - [ ] `scripts/verify.sh` exit 0

## 11. Idempotence and Recovery
Re-running the plan is safe. Tests use testcontainers; restart yields a fresh DB. Worker job idempotency key prevents double-ingest.

## 12. Progress
- [x] M1: AppException hierarchy + RFC 7807 handlers - 2026-06-27 - `pytest tests/integration/api/test_error_shape.py -q` passed.
- [x] M2: Health, readiness, metrics routes - 2026-06-27 - `pytest tests/integration/api/test_health.py -q` passed.
- [x] M3: Auth route stubs - 2026-06-27 - `pytest tests/integration/api/test_auth_stub.py -q` passed.
- [x] M4: Course routes and CourseService - 2026-06-27 - `pytest tests/integration/api -q` passed.
- [x] M5: Session routes and GenerationService - 2026-06-27 - `pytest tests/integration/api -q` passed.
- [x] M6: Ingest worker - 2026-06-27 - `pytest tests/integration/api -q` passed.
- [x] M7: OpenAPI snapshot - 2026-06-27 - `pytest tests/integration/test_openapi_snapshot.py -q` passed.

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
The API/service layer now exposes the core course, source, session, and CE record flows with contract-backed routes and snapshot coverage. The main follow-up from this phase was to keep the endpoint shapes stable while later plans filled in auth, smoke, and release behavior.
