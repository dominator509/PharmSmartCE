# SUPPORT.md

Compact support intake and incident routing for PharmSmartCE.

## Customer Support
- Customer-facing contact channel: open a GitHub issue in this repository.
- Include the environment, URL, request id, timestamp, exact user action, and any screenshots or console logs that do not expose secrets.
- Use the issue for bugs, access problems, grounding regressions, and release follow-up after customer impact.

## Incident Routing
- Use `.agent/checklists/incident-response.md` as the tabletop checklist.
- Use `OPERATIONS.md` for severity, escalation, and rollback paths.
- Use `ROLLBACK.md` when a release needs to be reversed or forward-fixed.

## On-Call Rota
- Primary: the currently assigned on-call engineer for the release window.
- Backup: the founding engineer.
- Sev1 escalation target: page immediately and expect acknowledgement within 5 minutes.
- Sev2 escalation target: notify during business hours and expect acknowledgement within 60 minutes.

## Operator Notes
- Keep incidents and customer reports linked to the issue or postmortem trail.
- Do not store secrets, tokens, or full `/auth/*` payloads in support notes.
