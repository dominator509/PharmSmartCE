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
- Customer-impact follow-up: TODO - link any customer issue or postmortem note.

## Data
- Local migration proof: verified 2026-06-28 with `cmd.exe /c` + `scripts/bin/uv.cmd run --directory apps/api alembic upgrade head` against the local Postgres container.
- Local integration proof: verified 2026-06-28 with `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/repositories -q`, `... test_faiss_store.py -q`, and `... test_citation_not_null.py -q`.
- FAISS rebuildable: verified in repo with `python -m app.cli.rebuild_index --all`.
- Backup test-restore: verified 2026-06-28 with `scripts/backup-restore-check.sh` against the local Postgres container.
- R2 retention evidence: TODO - capture bucket retention settings for sources and backups.
- S3 encryption evidence: TODO - capture bucket encryption settings for sources and backups.

## Security
- Local security proof: verified 2026-06-28 with `scripts/security-check.sh`, `scripts/dependency-audit.sh`, and `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/security -q`.

## Performance
- Local perf proof: verified 2026-06-28 with `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/perf -q`.

## Observability
- Local observability proof: verified 2026-06-28 with `scripts/bin/uv.cmd run --directory apps/api pytest tests/integration/test_observability_metrics_shape.py tests/integration/test_observability_redaction.py tests/integration/test_sentry.py tests/integration/test_alert_smoke.py -q`.

## Support / Ops
- Local incident-response doc check: verified 2026-06-28 with `scripts/incident-response-check.sh`.
- Incident tabletop: TODO - run the checklist and record outcome within 30 days.
- Sentry staging/prod evidence: TODO - capture a staging and prod event or dashboard proof.
- Alerting provider wiring: TODO - record provider/rule IDs and a test-fire result.

## Launch Gate
- Human approval comment: TODO - add the explicit launch comment with the release commit SHA.
