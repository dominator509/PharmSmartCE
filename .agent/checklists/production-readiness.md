# Checklist: Production Readiness

Cross-reference with `PRODUCTION_READINESS.md` — this is the operational ledger.

- [ ] Functional category audited (E2E happy path green vs staging)
- [x] Test category audited (`verify.sh` + coverage gate + golden-set)
- [x] Security category audited (`security-check.sh` + `dependency-audit.sh` + authz matrix)
- [ ] Privacy + data category audited (SSE-S3 verified, backup test-restore < 7 days)
- [ ] Performance audited (P95 session-start ≤ 30 s; 30-page ingest ≤ 5 min)
- [x] Accessibility audited (axe-core no `serious` violations on listed pages)
- [ ] Observability audited (logs, metrics, Sentry, alerts wired, runbooks linked)
- [ ] Deployment audited (release.yml works, same image staging/prod, bluegreen verified)
- [ ] Rollback drill completed in last 30 days
- [ ] Data audited (R2 retention set; backup test-restore < 7 days; FAISS rebuildable)
- [x] Documentation reviewed in last quarter
- [ ] Support audited (incident tabletop < 30 days; on-call rota; customer contact)
- [x] `scripts/production-readiness-check.sh` exit 0
- [ ] Final human launch gate comment recorded on release PR with SHA
