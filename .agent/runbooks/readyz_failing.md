# Runbook — readyz_failing

## Trigger
`readyz_failing` alert fires or `/readyz` returns 503 for 2 minutes.

## Detection Signals
- Metric: `background_queue_depth`
- Alert: `readyz_failing`
- Log pattern: `readyz` checks fail on DB, FAISS, or LLM warm state

## Severity
Sev1

## Owner / Escalation
- Primary: on-call.
- Escalate to: backup on-call after 15 minutes; founding engineer after 30 minutes.

## Pre-checks
- Check `/healthz` to confirm the process is still alive.
- Inspect which readiness subcheck is failing.

## Procedure
1. Restore the missing subsystem.
2. Re-run `/readyz`.
3. If the failure is deployment-related, roll back.

## Verification
- `/readyz` returns 200.
- Smoke test passes.

## Rollback (if procedure fails)
- Roll back the latest release and re-check readiness.

## Post-action
- Record the failed subsystem and the recovery step.

## Postmortem (Sev1 / Sev2)
- Document timeline, duration, and preventive fix.
