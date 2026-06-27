# PRODUCTION_READINESS.md

## Definition
Production-ready when ALL category checkboxes below are ticked AND
`scripts/production-readiness-check.sh` exits 0 AND the human launch gate
is approved.

This is the only document that defines launch readiness. `EP-010` walks
through these items.

## Functional Readiness
- [ ] User can register, log in, log out.
- [ ] Course author can upload PDF/DOCX source.
- [ ] Ingest completes successfully for 3 reference fixture PDFs.
- [ ] Test taker can start a session and receive ≥ 6 questions.
- [ ] Every question displays a clickable citation hyperlink to the source
      page/span.
- [ ] Submitting an answer is recorded; score is shown at session end.
- [ ] CE completion record is generated and downloadable as PDF.

## Test Readiness
- [ ] `scripts/verify.sh` exits 0 on a clean clone.
- [ ] Backend line ≥ 80%, branch ≥ 70%.
- [ ] Frontend statements ≥ 70%.
- [ ] Golden-set: citation accuracy ≥ 99%, uniqueness ≥ 95%.
- [ ] Playwright happy path green against staging.
- [ ] P95 session-start latency ≤ 30 s on target host.

## Security Readiness
- [ ] `scripts/security-check.sh` exits 0.
- [ ] `scripts/dependency-audit.sh` exits 0 (or allowlisted with reason).
- [ ] Refresh cookie is `HttpOnly; Secure; SameSite=Lax`.
- [ ] CSP headers verified.
- [ ] Authz matrix green.
- [ ] Injection detector + citation validator wired and tested.
- [ ] No secrets in repo (`gitleaks` clean).

## Privacy Readiness
- [ ] No PHI fields collected.
- [ ] Uploaded docs SSE-S3 encrypted at rest.
- [ ] Account deletion documented and tested.
- [ ] CE record export documented.

## Performance Readiness
- [ ] P95 session-start ≤ 30 s on 4 vCPU / 8 GB Fly machine.
- [ ] 30-page ingest ≤ 5 min.
- [ ] No N+1 queries on hot routes (`test_no_n_plus_one.py`).

## Accessibility Readiness
- [ ] axe-core no `serious` violations on `/login`, `/courses`,
      `/sessions/:id`.
- [ ] Interactive controls keyboard-reachable.
- [ ] Color contrast ≥ WCAG AA on text.

## Observability Readiness
- [ ] Structured logs with required fields.
- [ ] `/metrics` exposes all named metrics.
- [ ] Sentry receiving events from staging and prod.
- [ ] All alerts wired in alerting provider.
- [ ] Runbooks linked from each alert.

## Deployment Readiness
- [ ] `.github/workflows/release.yml` builds, pushes, deploys without manual
      edits.
- [ ] Same image tag in staging and prod.
- [ ] Bluegreen verified in staging.
- [ ] `release_command` runs migrations before traffic switch.

## Rollback Readiness
- [ ] Rollback drill executed in staging in the last 30 days.
- [ ] DB rollback policy documented in `ROLLBACK.md` and accepted by ops.

## Data Readiness
- [ ] Daily DB backup verified by test-restore in last 7 days.
- [ ] R2 retention set (sources: 365 d; backups: 30 d).
- [ ] FAISS indices rebuildable (`python -m app.cli.rebuild_index --all` in
      staging).

## Documentation Readiness
- [ ] All sections of this pack reviewed in the last quarter.
- [ ] `ASSUMPTIONS.md` reconciled — no `Yes (blocks)` rows unresolved.
- [ ] All ExecPlans `Outcomes & Retrospective` filled.

## Support Readiness
- [ ] Incident-response checklist exercised (tabletop within 30 days).
- [ ] On-call rota documented (even if one engineer initially).
- [ ] Customer-facing contact channel published.

## Final Launch Gate
Production launch requires a single explicit human decision recorded as an
issue or PR comment:

> "I confirm every PRODUCTION_READINESS.md checkbox is ticked and
> `scripts/production-readiness-check.sh` exits 0 against commit <SHA>.
> Proceeding to flip DNS / promote prod."

For autonomous coding agents, this gate is STOP S6.
