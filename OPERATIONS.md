# OPERATIONS.md

## Local Operations
- Start: `docker compose -f infra/docker-compose.yml up -d`
- Stop: `docker compose -f infra/docker-compose.yml down`
- Reset DB: see `ENVIRONMENT.md`.
- Tail logs: `uv run --directory apps/api python -m app.cli.tail_logs`

## Staging Operations
- SSH: `flyctl ssh console --app pharmsmartce-api-staging`
- Logs: `flyctl logs --app pharmsmartce-api-staging`
- Migrate: `flyctl ssh console ... --command "alembic upgrade head"`
- Re-ingest: `... --command "python -m app.cli.reingest <source_id>"`

## Production Operations
Identical commands with `--app pharmsmartce-api-prod`. **Every write action
must satisfy `AGENTS.md` §13.**

## Health Checks
- `GET /healthz` — liveness: 200 if process is up.
- `GET /readyz` — readiness: 200 only if:
  - DB pool can `SELECT 1` in 500 ms.
  - FAISS index dir is writable; configured index loads.
  - LLM is warm (model loaded for `llama_cpp`; 1-token ping 2 s timeout for
    `openai`, rate-limited 1/30s; always true for `fake`).
- `GET /metrics` — Prometheus scrape (restricted to internal scrapers).

## Common Failure Modes
| Mode | Detection | Remediation |
|---|---|---|
| LLM OOM | restart loop; `dmesg` oom-killer | Reduce `LLM_CONTEXT_SIZE` or smaller GGUF; bigger RAM |
| FAISS index missing | `/readyz` 503; `FileNotFoundError` | `python -m app.cli.reingest <id>` |
| DB pool exhausted | `QueuePool limit overflow` | Find slow queries; raise pool only after fix |
| OpenAI cap hit | alert; `ExternalServiceError(cap_reached)` | Service auto-falls back. Do not raise cap (S3) |
| Ingest worker stuck | `background_queue_depth` rising | `flyctl machines restart` worker; inspect `source.last_error` |
| Refresh table bloat | nightly job row-count | Hourly cleanup removes `expires_at < now()` rows |
| Citation overlap regression | `question_grounding_failures_total` spike | Roll back; inspect retrieval on golden set |

## Troubleshooting
| Symptom | First Check | Second |
|---|---|---|
| 502 from web | `flyctl status --app pharmsmartce-web-*` | API `/healthz` reachable from web |
| Slow session start | `llm_generation_duration_seconds` P95 | CPU saturation |
| Cannot login | Sentry tag `route=/auth/login` | Rate-limit counter; lockout row |
| New questions repeat | `question_uniqueness_ratio` | Reseed retrieval; check chunk diversity |

## DB Backup / Restore
- **Backup:** managed Postgres daily snapshots (7-day retention) + nightly
  `pg_dump --format=custom` to `r2://pharm-backups-prod/db/YYYY-MM-DD.dump`.
  Lifecycle: delete after 30 days.
- **PITR:** managed provider's PITR feature.
- **Logical restore:** `pg_restore --clean --if-exists --no-owner -d
  <new_db_url> <dump_file>`.
- **Verification:** monthly test-restore into
  `pharmsmartce-api-staging-restore`; smoke must pass; recorded in
  `.agent/checklists/production-readiness.md` ledger.

## Scheduled Jobs
| Job | Schedule | Action |
|---|---|---|
| Golden-set eval | nightly 03:00 UTC | `app.cli.run_golden_eval`; alert if accuracy drops > 1 pp |
| Refresh token cleanup | hourly | Delete rows where `expires_at < now()` |
| OpenAI monthly cost report | 1st of month 00:30 UTC | Aggregate `openai_cost_usd_total`; email ops |
| DB logical backup | nightly 04:00 UTC | `pg_dump`-to-R2 + checksum verify |

## Incident Triage
- **Sev1**: customer-facing outage OR grounding failure rate > 0.5% OR data
  integrity event. Page on-call.
- **Sev2**: degraded perf OR elevated 5xx OR LLM quality regression. Notify
  on-call business hours.
- **Sev3**: cost / capacity warning. Email.
- **Sev4**: cosmetic. Backlog.

See `.agent/checklists/incident-response.md`.

## Escalation
On-call → backup on-call (after 15 min unacked Sev1, 60 min Sev2) →
founding engineer.

## Maintenance Windows
Default: Sunday 04:00–06:00 UTC; announce 24 h in advance. Long-lock
migrations only in the window.

## Operational Safety Rules
- `AGENTS.md` §13 applies.
- Two-person rule for any prod data deletion.
- Default DB access is read-only; write requires a documented ticket.
