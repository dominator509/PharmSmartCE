# DEPLOYMENT.md

## Environments
| Env | Purpose | DB | Storage | LLM | Domain |
|---|---|---|---|---|---|
| `local` | Dev | Postgres in Docker | MinIO | Local GGUF / FakeLLM | http://localhost:3000 |
| `staging` | Pre-prod | Managed Postgres (small) | R2 `pharm-sources-staging` | Local GGUF on Fly | https://staging.pharmsmartce.com |
| `prod` | Live | Managed Postgres + daily backup | R2 `pharm-sources-prod` | Local GGUF on Fly | https://app.pharmsmartce.com |

## Deployment Architecture (Reference: Fly.io)
- **API app** `pharmsmartce-api-<env>`: 1 min / 2 max machines, 4 vCPU / 8 GB
  RAM. Volume `models` mounted at `/app/models` (≥ 8 GB) holding the GGUF
  across deploys.
- **Web app** `pharmsmartce-web-<env>`: 1 min / 2 max, shared CPU.
- **Worker app** `pharmsmartce-worker-<env>`: same image as API, different
  command, consumes Redis queue.
- **Managed Postgres** (Fly Postgres or Neon): single primary + read replica
  in prod; daily logical backup to R2.
- **R2 bucket**: source PDFs + nightly DB backups.
- **Redis**: Upstash or Fly Redis; queue + rate limit.

## Build Artifact
- API image: `apps/api/Dockerfile` (multi-stage; ~600 MB final).
- Web image: `apps/web/Dockerfile` (multi-stage; ~150 MB final).
- Tagged `pharmsmartce-api:{git_sha}` / `pharmsmartce-web:{git_sha}`.
- Built and pushed by `.github/workflows/release.yml` on tag `vX.Y.Z`.

## Release Flow
1. PR → `main`. CI runs `scripts/verify.sh`.
2. Merge to `main`. CI re-runs `verify.sh`.
3. Maintainer creates tag `vX.Y.Z`.
4. `release.yml`:
   - Build + push images.
   - Deploy to staging (`flyctl deploy --image ...`).
   - Run `scripts/smoke-test.sh https://staging.pharmsmartce.com`.
   - Pause for manual `production` environment approval.
5. Maintainer approves prod deploy (explicit human approval — agents STOP S6).
6. Actions deploys to prod:
   - Pre-traffic release task runs `alembic upgrade head`.
   - `flyctl deploy --strategy bluegreen --image ...`.
   - Post-deploy smoke against `https://app.pharmsmartce.com`.

## Manual Fallback
```sh
flyctl auth login
flyctl deploy --config infra/fly.api.toml \
              --app pharmsmartce-api-staging \
              --image pharmsmartce-api:vX.Y.Z
flyctl ssh console --app pharmsmartce-api-staging \
   --command "alembic upgrade head"
flyctl deploy --config infra/fly.web.toml \
              --app pharmsmartce-web-staging \
              --image pharmsmartce-web:vX.Y.Z
scripts/smoke-test.sh https://staging.pharmsmartce.com
```

## Migration Steps
- Migrations in `apps/api/alembic/versions/`. Each has a
  `# reversible: yes|no` annotation in the docstring.
- Non-reversible migrations require S6 approval for staging/prod.
- Migrations run in a `release_command` BEFORE traffic switch. Failure →
  traffic stays on old image.

## Rollback Steps
See `ROLLBACK.md`. Quick:
```sh
flyctl releases --app pharmsmartce-api-prod
flyctl releases rollback <version> --app pharmsmartce-api-prod
```

## Post-Deploy Smoke
`scripts/smoke-test.sh <base_url>` hits `/healthz`, `/readyz`, registers a
throwaway user, uploads a fixture, polls ingest, starts a session, asserts
≥ 6 questions with valid citation fields and a hyperlink that 200s.

## Required Approvals
- **Staging:** automatic on tag.
- **Prod:** explicit human approval via GitHub Environments `production`.
  For autonomous agents this is always STOP S6.

## Deployment STOP Conditions
- **S6.** Any prod deploy without human approval.
- **S6.** Any non-reversible migration applied to prod.
- **S2.** Secret rotation without documented procedure.
- **S1.** Missing `flyctl` token, `OPENAI_API_KEY` (if applicable), S3 keys,
  or Sentry DSN at deploy time.

## Production Verification
- [ ] `/healthz` and `/readyz` 200.
- [ ] Synthetic user completes a session end-to-end.
- [ ] Sentry shows no new error spikes within 15 min.
- [ ] `openai_cost_usd_total` increases only as expected.
- [ ] `question_grounding_failures_total` is 0 over the smoke window.
- [ ] Logs show `app_started` with the new image SHA.
