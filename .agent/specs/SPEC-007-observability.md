# SPEC-007 — Observability

**Status:** Accepted
**Owner:** founding-eng
**Date:** 2026-01
**Linked Roadmap Phase:** P7
**Linked ExecPlans:** EP-008

## User-Visible Goal
Operators can diagnose, alert on, and prove the health of the system.

## Required Behaviors
- Structured JSON logs with required fields (see `OBSERVABILITY.md`).
- Redaction of secrets per `SECURITY.md`.
- Prometheus `/metrics` exposes the metrics listed in `OBSERVABILITY.md`.
- `/healthz` (liveness) and `/readyz` (readiness) behave per
  `OPERATIONS.md`.
- Sentry receives unhandled exceptions in non-local envs.
- Optional OTel traces gated on `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Required Tests
- `test_observability_redaction.py` — `/auth/login` body never appears in
  logs.
- `test_observability_metrics_shape.py` — every named metric is registered.
- `test_healthz_readyz.py` — endpoints differentiate liveness vs readiness.
- `test_alert_smoke.py` (EP-008) — synthetic 5xx burst triggers a staging
  alert.

## Acceptance Criteria
- [ ] All required fields present in a smoke run's logs.
- [ ] Every named metric scrapes non-empty after a smoke run.
- [ ] `/healthz` and `/readyz` behave correctly under induced fault.
- [ ] Sentry shows the synthetic exception in staging.
