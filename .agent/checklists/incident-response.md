# Checklist: Incident Response

- [ ] **Detect** — alert fired / customer report / dashboard anomaly
- [ ] **Triage** — assign severity Sev1/Sev2/Sev3/Sev4 per `OPERATIONS.md`
- [ ] **Page** on-call for Sev1 within minutes
- [ ] **Notify** on-call during business hours for Sev2
- [ ] **Mitigate** — rollback per `ROLLBACK.md` if needed; apply runbook
- [ ] **Communicate** — status page if customer-facing; internal channel update
- [ ] **Resolve** — root cause addressed or remediation in flight
- [ ] **Verify** — dashboards back to baseline; smoke green
- [ ] **Document** — incident report (timeline + impact + actions)
- [ ] **Follow up** — postmortem within 5 business days for Sev1/Sev2; action items with owners and dates
- [ ] **Archive evidence** — capture the drill / incident notes in `PRODUCTION_EVIDENCE.md`
