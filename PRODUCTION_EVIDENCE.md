# Production Evidence Ledger

Compact place to record the external proof that EP-010 still needs.
Use one dated line per item, with the exact command or link and a short
result note.

Refresh this ledger with `scripts/production-evidence-report.sh` when you
need a compact Obsidian-friendly summary of the open launch evidence.

## Staging / Release
- Happy path vs staging: TODO - needs Fly auth, staging deploy, and smoke against https://staging.pharmsmartce.com.
- Bluegreen verification: TODO - needs staging deploy history that proves bluegreen or documented rolling exception.
- Release smoke: TODO - run `scripts/smoke-test.sh https://staging.pharmsmartce.com` after deploy.

## Rollback
- Rollback drill: TODO - execute in staging and record the previous release/version.
- Rollback verification: TODO - confirm /healthz, /readyz, and smoke pass after rollback.
- DB rollback policy documented in ROLLBACK.md and accepted by ops: TODO - capture ops sign-off on the rollback policy in ROLLBACK.md.
- Customer-impact follow-up: TODO - link any customer issue or postmortem note.

## Data
- Local migration proof: verified 2026-06-28 with `cmd.exe /c` + `scripts/bin/uv.cmd run --directory apps/api alembic upgrade head` against the local Postgres container.
- Local integration proof: verified 2026-06-28 with `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/repositories -q`, `... test_faiss_store.py -q`, and `... test_citation_not_null.py -q`.
- FAISS rebuildable: verified in repo with `python -m app.cli.rebuild_index --all`.
- Backup test-restore: verified 2026-06-28 with `scripts/backup-restore-check.sh` against the local Postgres container.
- FAISS rebuildable refresh: verified 2026-06-30 with `uv run --directory apps/api python -m app.cli.rebuild_index --all`; current local dataset rebuilt course indexes successfully and cleared stale zero-chunk artifacts.
- Backup test-restore refresh: verified 2026-06-30 with `scripts/backup-restore-check.sh` against the local Postgres container (`12 public tables restored`).
- R2 retention evidence: TODO - capture bucket retention settings for sources and backups.
- S3 encryption evidence: TODO - capture bucket encryption settings for sources and backups.

## Security
- Local security proof: verified 2026-06-28 with `scripts/security-check.sh`, `scripts/dependency-audit.sh`, and `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/security -q`.
- Local security proof refresh: verified 2026-06-30 with `scripts/security-check.sh`, `scripts/dependency-audit.sh`, and `uv run --directory apps/api pytest tests/integration/security -q`.
- Repo-local secret-scan fallback: verified 2026-06-30 by hardening `scripts/security-check.sh` to scan tracked files for OpenAI, GitHub, AWS, Google, Slack, and private-key patterns when `gitleaks` is unavailable on the workstation.

## Privacy
- Uploaded docs SSE-S3 encrypted at rest: TODO - capture bucket encryption settings for source PDFs and backups.

## Performance
- Local perf proof: verified 2026-06-28 with `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/perf -q`.
- Local perf proof refresh: verified 2026-06-30 with `uv run --directory apps/api pytest tests/integration/perf -q`.
- Target-host P95 session-start: TODO - capture the Fly 4 vCPU / 8 GB timing and record <= 30 s.
- Target-host 30-page ingest: TODO - capture ingest timing on the target host and record <= 5 min.

## Observability
- Local observability proof: verified 2026-06-28 with `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/test_observability_metrics_shape.py tests/integration/test_observability_redaction.py tests/integration/test_sentry.py tests/integration/test_alert_smoke.py -q`.
- Local observability proof refresh: verified 2026-06-30 with `uv run --directory apps/api pytest tests/integration/test_observability_metrics_shape.py tests/integration/test_observability_redaction.py tests/integration/test_sentry.py tests/integration/test_alert_smoke.py -q`.

## Support / Ops
- Local incident-response doc check: verified 2026-06-28 with `scripts/incident-response-check.sh`.
- Local evidence-ledger check: verified 2026-06-28 with `scripts/evidence-ledger-check.sh`.
- Local readiness gate: verified 2026-06-28 with `scripts/production-readiness-check.sh`.
- Local readiness gate refresh: verified 2026-06-30 with `scripts/verify.sh`, `uv run --directory apps/api pytest --cov-fail-under=80 -q`, `uv run --directory apps/api pytest tests/integration/test_generation_golden.py -q`, and `scripts/production-readiness-check.sh`.
- Local accessibility proof: verified 2026-06-30 with `pnpm --filter web test:e2e -- tests/e2e/a11y.spec.ts`.
- Local incident-response doc check refresh: verified 2026-06-30 with `scripts/incident-response-check.sh`.
- Local evidence-ledger check refresh: verified 2026-06-30 with `scripts/evidence-ledger-check.sh`.
- Incident tabletop: TODO - run the checklist and record outcome within 30 days.
- Sentry staging/prod evidence: TODO - capture a staging and prod event or dashboard proof.
- Alerting provider wiring: TODO - record provider/rule IDs and a test-fire result.

## Launch Gate
- Release candidate: the current `codex/release-readiness` head `adfdbe8` is the draft release candidate; the launch comment template is generated from that head.
- Launch comment template refresh: verified 2026-06-30 with `scripts/launch-gate-comment.sh`, which currently renders `I confirm every PRODUCTION_READINESS.md checkbox is ticked and scripts/production-readiness-check.sh exits 0 against commit adfdbe8. Proceeding to flip DNS / promote prod.`
- Human approval comment request posted 2026-06-28 on [PR #1](https://github.com/dominator509/PharmSmartCE/pull/1#issuecomment-4827000647); explicit approval with commit SHA remains TODO and `scripts/launch-gate-comment.sh` generates the exact launch text from the current branch head.
