# Runbook — grounding_failure_high

## Trigger
`grounding_failure_high` alert fires or grounded question failures exceed the allowed rate.

## Detection Signals
- Metric: `question_grounding_failures_total`
- Alert: `grounding_failure_high`
- Log pattern: `reason=injection_flagged|overlap_low|refused`

## Severity
Sev1

## Owner / Escalation
- Primary: on-call.
- Escalate to: backup on-call after 15 minutes; founding engineer after 30 minutes.

## Pre-checks
- Confirm whether failures come from one course or all courses.
- Check recent source uploads for injection patterns.

## Procedure
1. Inspect the failing source and its chunks.
2. Verify the injection detector and citation validator thresholds.
3. Quarantine or re-ingest the source if needed.

## Verification
- Grounding failures return to baseline.
- Newly ingested content passes citation checks.

## Rollback (if procedure fails)
- Disable the suspect source and revert to the last known good release.

## Post-action
- Notify content owners and log the affected source IDs.

## Postmortem (Sev1 / Sev2)
- Record root cause, evidence, and corrective actions.
