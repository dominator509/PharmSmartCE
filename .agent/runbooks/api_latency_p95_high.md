# Runbook — api_latency_p95_high

## Trigger
`api_latency_p95_high` alert fires or `/api/sessions/*/start` P95 exceeds 30 seconds for 10 minutes.

## Detection Signals
- Metric: `http_request_duration_seconds`
- Alert: `api_latency_p95_high`
- Log pattern: `duration_ms` spikes on `/api/sessions/*/start`

## Severity
Sev2

## Owner / Escalation
- Primary: on-call.
- Escalate to: backup on-call after 15 minutes; founding engineer after 60 minutes.

## Pre-checks
- Confirm whether latency is global or route-specific.
- Check CPU, memory, and DB pool saturation.

## Procedure
1. Inspect the affected route's p95/p99 dashboard.
2. Check DB readiness and ingest queue depth.
3. If a recent deploy correlates, roll back.

## Verification
- `/api/sessions/*/start` returns to within the SLO.
- `scripts/smoke-test.sh` completes.

## Rollback (if procedure fails)
- Roll back the latest release image and re-test.

## Post-action
- Document the primary bottleneck and any config change.

## Postmortem (Sev1 / Sev2)
- Record impact, contributing factors, and action items.
