# EP-008 — Observability & Operations

**Phase:** P7

## 1. Purpose / Big Picture
Wire structlog with redaction, request_id middleware, Prometheus metrics, deep `/healthz` and `/readyz` checks, Sentry, a synthetic fault test that triggers an alert in staging, and per-alert runbooks.

## 2. Scope
- structlog config + RedactProcessor + request_id middleware
- Prometheus registry + named metrics in services
- `/healthz` + `/readyz` with DB + FAISS + LLM warm checks
- Sentry init gated on `SENTRY_DSN`
- Synthetic fault E2E test that triggers a staging alert
- Runbooks committed for each alert

## 3. Non-goals
- New product features
- Replacing the logging library
- OTel beyond an env-toggled opt-in

## 4. Context and Orientation
Builds on EP-004 service layer. Wires observability so EP-009 deploy and EP-010 prod-readiness have signal.

## 5. Files to Read First
- `AGENTS.md`
- `OBSERVABILITY.md`
- `OPERATIONS.md`
- `SECURITY.md`
- `.agent/specs/SPEC-007-observability.md`

## 6. Files to Change
- `apps/api/app/observability/__init__.py`
- `apps/api/app/observability/logging.py`
- `apps/api/app/observability/metrics.py`
- `apps/api/app/observability/sentry.py`
- `apps/api/app/api/middleware/request_id.py`
- `apps/api/app/api/routes/health.py`
- `apps/api/app/main.py`
- `apps/api/app/services/generation/service.py`
- `apps/api/app/services/ingest/service.py`
- `apps/api/tests/integration/test_observability_redaction.py`
- `apps/api/tests/integration/test_observability_metrics_shape.py`
- `apps/api/tests/integration/test_healthz_readyz.py`
- `apps/api/tests/integration/test_alert_smoke.py`
- `.agent/runbooks/api_5xx_high.md`
- `.agent/runbooks/api_latency_p95_high.md`
- `.agent/runbooks/grounding_failure_high.md`
- `.agent/runbooks/openai_cap_reached.md`
- `.agent/runbooks/readyz_failing.md`

## 7. Interfaces and Contracts
Logging via structlog with `RedactProcessor`. Required fields: `request_id`, `user_id`, `org_id`, `route`, `method`, `status`, `duration_ms`, `app_env`, `image_sha`. Prometheus exposes named metrics from `OBSERVABILITY.md`. `/readyz` 200 only when DB + FAISS + LLM warm. Sentry `capture_exception` when `SENTRY_DSN` set.

## 8. Milestones

### M1: structlog + RedactProcessor + request_id middleware
- **Files to read:** `OBSERVABILITY.md`, `SECURITY.md`
- **Files to change:** `apps/api/app/observability/__init__.py`, `apps/api/app/observability/logging.py`, `apps/api/app/api/middleware/request_id.py`, `apps/api/app/main.py`
- **Exact edits expected:** Configure structlog with JSON renderer in non-local envs, console renderer locally. `RedactProcessor` blocks named fields per SECURITY.md. request_id middleware generates ULID, sets `X-Request-Id` header, binds to structlog context.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/test_observability_redaction.py -q`
- **Expected result:** /auth/login body never appears in logs.
- **Recovery:** If a field leaks, add it to the redacted list and retest.

### M2: Prometheus registry + named metrics
- **Files to read:** `OBSERVABILITY.md`
- **Files to change:** `apps/api/app/observability/metrics.py`, `apps/api/app/services/generation/service.py`, `apps/api/app/services/ingest/service.py`
- **Exact edits expected:** Define every named metric from OBSERVABILITY.md. GenerationService instruments `llm_generation_duration_seconds` and `question_grounding_failures_total`. IngestService instruments `ingest_duration_seconds` and `ingest_jobs_total`. Expose at `/metrics`.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/test_observability_metrics_shape.py -q`
- **Expected result:** Every named metric registered and visible at `/metrics` after a smoke.
- **Recovery:** If metric name typo, cross-check exact spelling against OBSERVABILITY.md.

### M3: /healthz + /readyz deep checks
- **Files to read:** `OPERATIONS.md`
- **Files to change:** `apps/api/app/api/routes/health.py`
- **Exact edits expected:** `/healthz` returns `{status: ok}` unconditionally. `/readyz` checks DB `SELECT 1` in 500ms + FAISS dir writable + LLM warm flag per provider. Returns 200 only if all green, else 503.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/test_healthz_readyz.py -q`
- **Expected result:** /healthz 200 always; /readyz 200 when green, 503 when a subsystem down (induced by fixture).
- **Recovery:** If LLM warm check too slow for `fake` provider, short-circuit to True for it.

### M4: Sentry init gated on SENTRY_DSN
- **Files to read:** `OBSERVABILITY.md`
- **Files to change:** `apps/api/app/observability/sentry.py`, `apps/api/app/main.py`
- **Exact edits expected:** Init Sentry SDK only when `SENTRY_DSN` set. Environment from `APP_ENV`. PII redacted.
- **Validation command:** `uv run --directory apps/api pytest tests/integration -q -k sentry`
- **Expected result:** Sentry is a no-op when DSN unset; mock-Sentry receives an event when DSN set.
- **Recovery:** If SDK version mismatch, pin `sentry-sdk` in pyproject.toml.

### M5: Synthetic fault test
- **Files to read:** `OBSERVABILITY.md`
- **Files to change:** `apps/api/tests/integration/test_alert_smoke.py`
- **Exact edits expected:** Test induces a 5xx burst at a test-only route; asserts the mocked alerting provider receives the `api_5xx_high` alert. In staging, this runs as a manual pre-launch smoke.
- **Validation command:** `uv run --directory apps/api pytest tests/integration/test_alert_smoke.py -q`
- **Expected result:** Mock alerting provider records the alert.
- **Recovery:** If mock plumbing flaky, write a record-only fake and assert call count.

### M6: Runbooks committed
- **Files to read:** `OBSERVABILITY.md`, `OPERATIONS.md`, `.agent/templates/runbook-template.md`
- **Files to change:** `.agent/runbooks/api_5xx_high.md`, `.agent/runbooks/api_latency_p95_high.md`, `.agent/runbooks/grounding_failure_high.md`, `.agent/runbooks/openai_cap_reached.md`, `.agent/runbooks/readyz_failing.md`
- **Exact edits expected:** One runbook per alert using the runbook template (Trigger / Detection / Severity / Owner / Pre-checks / Procedure / Verification / Rollback / Post-action / Postmortem).
- **Validation command:** `ls .agent/runbooks | wc -l`
- **Expected result:** Count ≥ 5.
- **Recovery:** If a runbook is missing template fields, fill them per `.agent/templates/runbook-template.md`.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] `scripts/smoke-test.sh` logs include all required fields
  - [ ] `/metrics` returns named metrics non-zero after smoke
  - [ ] One alert rule fires in staging during the synthetic fault test
  - [ ] Sentry shows the synthetic exception in the staging mock

## 11. Idempotence and Recovery
Tests use mocked Sentry and alerting; re-runs deterministic. /readyz checks are stateless. Re-running the plan reapplies files.

## 12. Progress
- [ ] M1: structlog + RedactProcessor + request_id middleware
- [ ] M2: Prometheus registry + named metrics
- [ ] M3: /healthz + /readyz deep checks
- [ ] M4: Sentry init gated on SENTRY_DSN
- [ ] M5: Synthetic fault test
- [ ] M6: Runbooks committed

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
