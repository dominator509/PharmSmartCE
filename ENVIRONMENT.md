# ENVIRONMENT.md

## Required Tools
| Tool | Min Version | Notes |
|---|---|---|
| Python | 3.11.x | `apps/api/.python-version` |
| Node.js | 20.x LTS | `apps/web/.nvmrc` |
| Docker | 24.x | Local Postgres + Redis + MinIO |
| docker compose | v2 | Bundled with Docker Desktop |
| uv | 0.5+ | Python pkg mgr |
| pnpm | 9.x | Node pkg mgr |
| git | 2.40+ | |

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
corepack enable && corepack prepare pnpm@9 --activate
```

## Package Managers
- Python: `uv` (lockfile `uv.lock`, manifest `apps/api/pyproject.toml`).
- Node: `pnpm` (lockfile `pnpm-lock.yaml`, workspace `pnpm-workspace.yaml`).

## Environment Variables

| Name | Required | Env | Example | Secret | Description | Validation |
|---|---|---|---|---|---|---|
| `APP_ENV` | yes | all | `local` | no | Runtime env | enum: `local`,`test`,`staging`,`prod` |
| `LOG_LEVEL` | no | all | `info` | no | Log verbosity | enum |
| `DATABASE_URL` | yes | all | `postgresql+asyncpg://app:app@db:5432/pharm` | YES | Postgres async DSN | URI w/ `+asyncpg` |
| `REDIS_URL` | yes (workers) | all | `redis://redis:6379/0` | no | Redis | URI |
| `JWT_SECRET` | yes | all | `<32+ random bytes b64>` | YES | JWT HS256 signing | `len(decoded)>=32` |
| `REFRESH_SECRET` | yes | all | `<32+ random bytes b64>` | YES | Refresh pepper | `len(decoded)>=32` |
| `LLM_PROVIDER` | yes | all | `llama_cpp` | no | Adapter | enum: `llama_cpp`,`openai`,`fake` |
| `LLM_MODEL_PATH` | if `llama_cpp` | all | `models/llama-3.1-8b-instruct.Q4_K_M.gguf` | no | GGUF path | file exists; ends `.gguf` |
| `LLM_CONTEXT_SIZE` | no | all | `4096` | no | Context window | int 512..32768 |
| `LLM_N_THREADS` | no | all | `4` | no | CPU threads | int >= 1 |
| `LLM_MAX_OUTPUT_TOKENS` | no | all | `512` | no | Per-call output | int 64..2048 |
| `OPENAI_API_KEY` | if `openai` | all | `sk-...` | YES | OpenAI key | starts `sk-` |
| `OPENAI_MODEL` | no | all | `gpt-4o-mini` | no | Model | non-empty |
| `OPENAI_MONTHLY_USD_CAP` | if `openai` | all | `50.00` | no | Hard cap | decimal > 0 |
| `EMBEDDING_MODEL` | no | all | `sentence-transformers/all-MiniLM-L6-v2` | no | HF model id | non-empty |
| `FAISS_INDEX_DIR` | no | all | `var/faiss` | no | Index dir | path |
| `RAG_CHUNK_TOKENS` | no | all | `512` | no | Chunk size | int 128..2048 |
| `RAG_CHUNK_OVERLAP` | no | all | `64` | no | Overlap | int 0..512 |
| `RAG_MAX_CONTEXT_TOKENS` | no | all | `3000` | no | Max LLM ctx | int 512..16000 |
| `CITATION_MIN_OVERLAP_RATIO` | no | all | `0.4` | no | Min overlap | float 0..1 |
| `GENERATION_RETRY_BUDGET` | no | all | `3` | no | Per-Q retry cap | int >= 1 |
| `UPLOAD_MAX_BYTES` | no | all | `52428800` | no | Upload cap | int > 0 |
| `S3_ENDPOINT` | yes (non-local) | staging,prod | `https://<acct>.r2.cloudflarestorage.com` | no | Endpoint | URI |
| `S3_BUCKET` | yes (non-local) | staging,prod | `pharm-sources-prod` | no | Bucket | non-empty |
| `S3_REGION` | yes (non-local) | staging,prod | `auto` | no | Region | non-empty |
| `S3_ACCESS_KEY_ID` | yes (non-local) | staging,prod | `...` | YES | Access key | non-empty |
| `S3_SECRET_ACCESS_KEY` | yes (non-local) | staging,prod | `...` | YES | Secret key | non-empty |
| `SENTRY_DSN` | no | staging,prod | `https://...@sentry.io/123` | YES | Sentry DSN | URI |
| `CORS_ALLOWED_ORIGINS` | yes | all | `https://app.pharmsmartce.com` | no | CSV origins | CSV URIs |
| `RATE_LIMIT_DEFAULT` | no | all | `30/minute` | no | slowapi default | `n/unit` |
| `WEB_PUBLIC_API_URL` | yes | all (web) | `http://localhost:8000` | no | Browser API base | URI |

Validation lives in `apps/api/app/config.py` (`pydantic-settings` +
`@field_validator`). Failed validation crashes the app at startup.

## Local Dev Setup
```sh
git clone <repo> && cd PharmSmartCE
cp .env.example .env
scripts/install.sh
docker compose -f infra/docker-compose.yml up -d db redis minio
uv run --directory apps/api alembic upgrade head
uv run --directory apps/api python -m app.cli.seed_dev
uv run --directory apps/api uvicorn app.main:app --reload --port 8000
pnpm --filter web dev
```

## Test Env
Tests start Postgres via `testcontainers`. LLM is FakeLLM by default.
`llm_smoke` marker requires `LLM_MODEL_PATH` and is excluded from CI.

## Staging
Fly.io app `pharmsmartce-staging`; managed Postgres; R2 bucket
`pharm-sources-staging`. Secrets via `flyctl secrets set ...`. Sentry env
`staging`.

## Production
Fly.io app `pharmsmartce-prod`; managed Postgres with daily backup; R2
bucket `pharm-sources-prod`. Secrets via `flyctl secrets set ...`. Sentry
env `prod`.

## Config Validation
`app/config.py::Settings(BaseSettings)` with typed fields + `@field_validator`.
Unit-tested in `tests/unit/test_config.py`.

## Environment Parity Rules
- Same Docker image runs in staging and prod.
- Same model file in staging and prod (Fly volume).
- Same Alembic head in staging and prod.
- No env var named `*_DEBUG*` is `true` in staging/prod.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `Settings` validation error at startup | Missing/invalid env var | Set per table |
| `OSError: cannot load model` | `LLM_MODEL_PATH` wrong / not downloaded | `scripts/install.sh` |
| FAISS `IndexError` | Stale index after schema change | Delete `var/faiss/` and re-ingest |
| `429 Too Many Requests` locally | Hit local rate limit | Raise `RATE_LIMIT_DEFAULT` |
| Postgres conn refused | `docker compose` not up | `docker compose ... up -d db` |
