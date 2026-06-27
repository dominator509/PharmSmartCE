# Checklist: Rollback

- [ ] Trigger evidence captured (metric / log / customer ticket)
- [ ] On-call owner identified
- [ ] Backup on-call acknowledged within 5 min (or proceed and document)
- [ ] Rollback type chosen (image / config / DB / feature flag)
- [ ] `flyctl releases rollback <prev>` executed
- [ ] DB: forward-fix preferred; downgrade only if migration was `# reversible: yes` AND no new dependent data AND human approved
- [ ] Config rollback via `flyctl secrets set/unset` + redeploy if applicable
- [ ] `/healthz` and `/readyz` back to 200
- [ ] `scripts/smoke-test.sh` passes against affected URL
- [ ] Error and grounding-failure dashboards back to baseline within 15 min
- [ ] Customer-impact tickets updated
- [ ] Communication template posted (status page + internal channel)
- [ ] Postmortem scheduled within 5 business days for Sev1/Sev2
