# Runbook — api_5xx_high

## Trigger
`api_5xx_high` alert fires or 5xx rate exceeds 1% for 5 minutes.

## Detection Signals
- Metric: `http_requests_total{status=~"5.."}`
- Alert: `api_5xx_high`
- Log pattern: `status=5xx route=/api/*`

## Severity
Sev2

## Owner / Escalation
- Primary: on-call.
- Escalate to: backup on-call after 15 minutes; founding engineer after 60 minutes.

## Pre-checks
- Confirm whether the spike is isolated to one route.
- Verify `/healthz` and `/readyz`.

## Procedure
1. Inspect logs by `request_id` and route.
2. Check recent deploys and rollback if a new image is implicated.
3. Re-run the smoke test against the affected environment.

## Verification
- 5xx rate returns below 1%.
- Smoke test returns `ok`.

## Rollback (if procedure fails)
- Roll back to the previous release image.
- Re-check health and smoke.

## Post-action
- Update incident notes and link the root-cause ticket.

## Postmortem (Sev1 / Sev2)
- Record timeline, root cause, and follow-up actions.
