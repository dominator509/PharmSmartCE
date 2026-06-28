# Runbook — openai_cap_reached

## Trigger
`openai_cap_reached` alert fires or monthly OpenAI spend hits the configured cap.

## Detection Signals
- Metric: `openai_cost_usd_monthly`
- Alert: `openai_cap_reached`
- Log pattern: `cap_reached`

## Severity
Sev2

## Owner / Escalation
- Primary: on-call.
- Escalate to: backup on-call after 30 minutes; founding engineer after 60 minutes.

## Pre-checks
- Confirm the fallback to local LLM is active.
- Check whether spend is expected from a test or smoke.

## Procedure
1. Verify the current spend and cap values.
2. Confirm generation falls back to the local provider.
3. Pause any nonessential OpenAI usage.

## Verification
- `openai_cost_usd_monthly` stays at or below cap.
- Generation continues via the local provider.

## Rollback (if procedure fails)
- Keep the cap unchanged; do not raise it.

## Post-action
- Record the spend snapshot and follow-up action.

## Postmortem (Sev1 / Sev2)
- Note whether the cap should have fired sooner.
