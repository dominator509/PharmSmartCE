# Runbook — <Alert / Incident Name>

## Trigger
(What event/alert/customer report triggers this runbook.)

## Detection Signals
- Metric: `<name>` threshold `<value>` over `<window>`.
- Alert: `<alert_name>`.
- Log pattern: `<query>`.

## Severity
Sev1 | Sev2 | Sev3 | Sev4

## Owner / Escalation
- Primary: on-call.
- Escalate to: backup on-call after <N> minutes; founding engineer after
  <M> minutes.

## Pre-checks
- (Confirm impact scope.)
- (Verify auth / access available.)

## Procedure
1. (Safe step with exact command.)
2. (Safe step with exact command.)
3. (Safe step with exact command.)

## Verification
- (Command + expected output to confirm fix.)
- (Dashboard panel to watch.)

## Rollback (if procedure fails)
- (Concrete rollback steps.)

## Post-action
- Update Sentry incident.
- Update status page if customer-facing.
- File issue for follow-up.

## Postmortem (Sev1 / Sev2)
- Timeline.
- Root cause.
- What went well.
- What went poorly.
- Action items with owners and dates.
