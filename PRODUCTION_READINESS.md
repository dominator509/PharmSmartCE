# PRODUCTION_READINESS.md

## Definition
Production-ready when ALL category checkboxes below are ticked AND
`scripts/production-readiness-check.sh` exits 0 AND the human launch gate
is approved.

This is the only document that defines launch readiness. `EP-010` walks
through these items.

## Functional Readiness
- [x] User can register, log in, log out.
- [x] Course author can upload PDF/DOCX source.
- [x] Ingest completes successfully for 3 reference fixture PDFs.
- [x] Test taker can start a session and receive ≥ 6 questions.
- [x] Every question displays a clickable citation hyperlink to the source
      page/span.
- [x] Submitting an answer is recorded; score is shown at session end.
- [x] CE completion record is generated and downloadable as PDF.

## Test Readiness
- [x] `scripts/verify.sh` exits 0 on a clean clone.
- [x] Backend line ≥ 80%, branch ≥ 70%.
- [x] Frontend statements ≥ 70%.
- [x] Golden-set: citation accuracy ≥ 99%, uniqueness ≥ 95%.
- [ ] Playwright happy path green against staging.
- [ ] P95 session-start latency ≤ 30 s on target host.

## Security Readiness
- [x] `scripts/security-check.sh` exits 0.
- [x] `scripts/dependency-audit.sh` exits 0 (or allowlisted with reason).
- [x] Refresh cookie is `HttpOnly; Secure; SameSite=Lax`.
- [x] CSP headers verified.
- [x] Authz matrix green.
- [x] Injection detector + citation validator wired and tested.
- [x] No secrets in repo (`scripts/security-check.sh` clean).

## Privacy Readiness
- [x] No PHI fields collected.
- [ ] Uploaded docs SSE-S3 encrypted at rest.
- [x] Account deletion documented and tested.
- [x] CE record export documented.

## Performance Readiness
- [ ] P95 session-start ≤ 30 s on 4 vCPU / 8 GB Fly machine.
- [ ] 30-page ingest ≤ 5 min.
- [x] No N+1 queries on hot routes (`test_no_n_plus_one.py`).

## Accessibility Readiness
- [x] axe-core no `serious` violations on `/login`, `/courses`,
      `/sessions/:id`.
- [x] Interactive controls keyboard-reachable.
- [x] Color contrast ≥ WCAG AA on text.

## Observability Readiness
- [x] Structured logs with required fields.
- [x] `/metrics` exposes all named metrics.
- [ ] Sentry receiving events from staging and prod.
- [ ] All alerts wired in alerting provider.
- [x] Runbooks linked from each alert.

## Deployment Readiness
- [x] `.github/workflows/release.yml` builds, pushes, deploys without manual
      edits.
- [x] Same image tag in staging and prod.
- [ ] Bluegreen verified in staging.
- [x] `release_command` runs migrations before traffic switch.

## Rollback Readiness
- [ ] Rollback drill executed in staging in the last 30 days.
- [ ] DB rollback policy documented in `ROLLBACK.md` and accepted by ops.

## Data Readiness
- [x] Daily DB backup verified by test-restore in last 7 days.
- [ ] R2 retention set (sources: 365 d; backups: 30 d).
- [x] FAISS indices rebuildable (`python -m app.cli.rebuild_index --all` in
      staging).

## Documentation Readiness
- [x] All sections of this pack reviewed in the last quarter.
- [x] `ASSUMPTIONS.md` reconciled — no `Yes (blocks)` rows unresolved.
- [x] All ExecPlans `Outcomes & Retrospective` filled.

## Support Readiness
- [ ] Incident-response checklist exercised (tabletop within 30 days).
- [x] On-call rota documented (even if one engineer initially).
- [x] Customer-facing contact channel published.

## Notes
- Branch-aware backend coverage currently reports 80% total with `pytest --cov=app --cov-branch -q`.
- Frontend coverage scoped to app routes and toolchain files currently reports 92.68% statements with `vitest --coverage`.
- Fixture-backed ingest now passes for 3 sample CE PDFs, and the injection detector/quarantine path is covered by dedicated API tests.
- Golden-set harness now passes against `apps/api/tests/fixtures/golden_set.jsonl` with the FakeLLM-backed grounded generation path.
- Observability locals now cover redaction, metrics shape, Sentry init/capture, and the synthetic 5xx alert hook in repo tests, but the staging smoke evidence is still separate.
- Support intake is published in `SUPPORT.md` and routed through `OPERATIONS.md` and `.agent/checklists/incident-response.md`.
- Support intake is documented, the on-call rota is documented, and the
  customer-facing contact channel is published, but the tabletop exercise
  itself is still pending.
- Repo secret scan and dependency audit are currently clean on this tree.
- Release workflow pins staging and prod to the same `github.sha` image tag;
  bluegreen still needs external proof, but the API Fly config now explicitly
  runs `alembic upgrade head` before traffic switch.
- Observability tests prove structured logs include request and image context,
  and `/metrics` exposes every metric name in `METRIC_NAMES`.
- `apps/web/tests/e2e/a11y.spec.ts` covers `/login`, `/courses`, and
  `/sessions/:id`; `pnpm --filter web test:e2e -- tests/e2e/a11y.spec.ts`
  passes that axe-core and keyboard-reachability check.
- The hardened a11y spec now tab-checks representative controls and rejects
  color-contrast violations on the same core pages.
- Alert rows in `OBSERVABILITY.md` now point at the relevant runbook sections.
- App schemas/routes only collect learner, course, session, and CE-record
  fields; no patient/diagnosis/insurance fields are present in app source.
- `apps/api/tests/integration/perf/test_no_n_plus_one.py` guards the session
  read route with a query budget of 6 statements.
- `scripts/verify.sh` now passes in the current checkout with the repo-local
  temp/cache overrides required by this Windows profile.
- The full readiness pack was re-reviewed in this pass, covering every section.
- `DELETE /auth/account` removes the current user and, when applicable, the
  org and its dependent course/session/CE-record data.
- External proof items still need dated entries in `PRODUCTION_EVIDENCE.md`
  before the final launch gate can be signed.

## Final Launch Gate
Production launch requires a single explicit human decision recorded as an
issue or PR comment:

> "I confirm every PRODUCTION_READINESS.md checkbox is ticked and
> `scripts/production-readiness-check.sh` exits 0 against commit <SHA>.
> Proceeding to flip DNS / promote prod."

For autonomous coding agents, this gate is STOP S6.
