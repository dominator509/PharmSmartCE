# TESTING.md

## Test Pyramid (Target Mix)
| Layer | Share | Where |
|---|---|---|
| Unit | ~60% | `apps/api/tests/unit/`, `apps/web/tests/unit/` |
| Integration | ~30% | `apps/api/tests/integration/` (testcontainers Postgres + real FAISS) |
| E2E | ~10% | `apps/web/tests/e2e/` (Playwright) |

## Coverage Targets (Launch Gates)
- Backend line ≥ **80%**, branch ≥ **70%**.
- Frontend statements ≥ **70%**.
- Golden-set: citation accuracy ≥ **99%**, uniqueness ≥ **95%**.

## Unit Rules
- No I/O. No DB. No real LLM. No HTTP.
- LLM tests use `FakeLLM` (`apps/api/app/adapters/llm/fake_adapter.py`):
  output is a deterministic function of `sha256(prompt)`.
- A unit test is only "good" if it would fail without the change.

## Integration Rules
- `testcontainers[postgres]` per session.
- Real FAISS (file-backed, `tmp_path`).
- LLM is `FakeLLM` unless `@pytest.mark.llm_smoke` (excluded from CI).
- Each test rolls back its transaction or truncates between tests.

## E2E Rules (Playwright)
- Run against local docker compose stack.
- Happy path: register → login → upload source → start session → answer all
  → see clickable citations → see CE result.
- One `@smoke` E2E runs against staging after deploy.

## Contract Tests
- OpenAPI snapshot at `apps/api/openapi.json`.
- `tests/integration/test_openapi_snapshot.py` fails on drift without
  explicit update.

## Smoke Tests
- `scripts/smoke-test.sh` → `python -m app.cli.smoke`:
  1. `/healthz` 200.
  2. `/readyz` 200 (DB, FAISS, LLM warm).
  3. Register throwaway user.
  4. Upload fixture PDF.
  5. Poll ingest ≤ 60 s.
  6. Start session.
  7. Assert ≥ 6 questions, each with non-null citation fields + hyperlink
     resolves.

## Regression Tests
Every bug fix lands with a test that failed before the fix.
`tests/integration/regression/test_generation_*.py`.

## Performance Tests
- `tests/integration/perf/test_generation_latency.py` runs with FakeLLM at
  CI; asserts orchestration overhead ≤ 2 s. Real-LLM perf measured in
  `EP-002` and tracked.

## Accessibility Tests
- `pnpm --filter web test:a11y` runs axe-core on key pages; no `serious`
  violations.

## Security Tests
- `test_authz.py` — 401/403 matrix for every route.
- `test_injection_filter.py` — PDFs with `ignore previous instructions`,
  `<<<context_end>>>`, `system:` are flagged and fail closed.
- `test_openai_cost_cap.py` — when monthly cost ≥ cap, generation falls
  back to local LLM.

## Test Data
- `polyfactory` for domain entities; factories for ORM models.
- Fixture PDFs: `apps/api/tests/fixtures/sample_ce/` (3 PDFs, 20–40 pages).
- Golden set: `apps/api/tests/fixtures/golden_set.jsonl` (50 hand-labeled
  triples).

## Mocking Rules
- Mock at adapter boundaries only. Never mock domain. Never mock repositories
  — use a real Postgres in integration tests.

## Required Tests per Feature
| Layer | Test |
|---|---|
| Domain | One test per new invariant (must raise on violation). |
| Service | One success + one failure path. |
| Repository | One round-trip test. |
| API | One contract test. |
| E2E (if user-visible) | One Playwright test. |

## Validation Matrix
| Spec | Tests |
|---|---|
| SPEC-001 | `tests/unit/domain/test_*.py` |
| SPEC-002 | `tests/integration/repositories/test_*.py` |
| SPEC-003 | `tests/integration/api/test_*.py` + OpenAPI snapshot |
| SPEC-004 | `apps/web/tests/e2e/*.spec.ts` |
| SPEC-005 | `tests/integration/security/*.py` |
| SPEC-006 | `tests/integration/api/test_error_shape.py` |
| SPEC-007 | `tests/integration/test_observability_*.py` |
| SPEC-008 | `scripts/production-readiness-check.sh` |

## Flaky Test Policy
- 1st flake (7-day window): `@pytest.mark.flaky(reruns=2)` + note in active
  ExecPlan `Surprises & Discoveries`.
- 2nd flake: `@pytest.mark.quarantine` (excluded from CI) + owner + 1-week
  deadline.
- 3rd flake or expired deadline: delete and replace with a redesigned test.

## Definition of Test Done
Tests run via scripts in `COMMANDS.md`; all gates pass in CI; new behavior
has a failing-without-the-change test; no test is skipped without a written
reason + tracking note.
