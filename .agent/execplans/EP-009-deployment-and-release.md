# EP-009 — Deployment & Release

**Phase:** P8

## 1. Purpose / Big Picture
Build Docker images, deploy to Fly.io staging, smoke, document and execute a rollback drill. Production deploy itself is a STOP S6 for autonomous agents.

## 2. Scope
- apps/api/Dockerfile multi-stage
- apps/web/Dockerfile multi-stage
- infra/fly.{api,web,worker}.toml with `release_command` for migrations + models volume on api
- `.github/workflows/release.yml` triggered on tag `vX.Y.Z`
- `scripts/smoke-test.sh` wired against staging URL
- Rollback drill executed in staging

## 3. Non-goals
- Production launch decision (human STOP S6)
- GPU inference
- Multi-region failover

## 4. Context and Orientation
Builds on EP-006 (security) and EP-008 (observability). Production deploy is a STOP S6 for agents.

## 5. Files to Read First
- `AGENTS.md`
- `DEPLOYMENT.md`
- `ROLLBACK.md`
- `OPERATIONS.md`

## 6. Files to Change
- `apps/api/Dockerfile`
- `apps/web/Dockerfile`
- `infra/fly.api.toml`
- `infra/fly.web.toml`
- `infra/fly.worker.toml`
- `.github/workflows/release.yml`
- `scripts/smoke-test.sh`
- `apps/api/app/cli/smoke.py`
- `CHANGELOG.md`

## 7. Interfaces and Contracts
Tag `vX.Y.Z` drives the build. `release_command` runs `alembic upgrade head` before traffic switch. Fly volume `models` persists `*.gguf` across deploys. `flyctl releases rollback` restores the previous image.

## 8. Milestones

### M1: apps/api Dockerfile multi-stage
- **Files to read:** `ARCHITECTURE.md`, `DEPLOYMENT.md`
- **Files to change:** `apps/api/Dockerfile`
- **Exact edits expected:** Stage 1: build with `uv sync --frozen`. Stage 2: `python:3.11-slim` final with copied venv + `app/`. `CMD uvicorn app.main:app --host 0.0.0.0 --port 8080`.
- **Validation command:** `docker build -f apps/api/Dockerfile -t pharmsmartce-api:dev .`
- **Expected result:** Build succeeds; image < 800 MB.
- **Recovery:** If build slow, add `.dockerignore` for `tests/` and `var/`.

### M2: apps/web Dockerfile multi-stage
- **Files to read:** `DEPLOYMENT.md`
- **Files to change:** `apps/web/Dockerfile`
- **Exact edits expected:** Stage 1: `node:20-alpine` + `pnpm install` + `pnpm build`. Stage 2: `node:20-alpine` with `.next/standalone` + production node_modules. `CMD node server.js`.
- **Validation command:** `docker build -f apps/web/Dockerfile -t pharmsmartce-web:dev .`
- **Expected result:** Build succeeds; image < 200 MB.
- **Recovery:** If next build needs standalone output, set `output: 'standalone'` in `next.config.mjs`.

### M3: fly.toml configs
- **Files to read:** `DEPLOYMENT.md`, `OPERATIONS.md`
- **Files to change:** `infra/fly.api.toml`, `infra/fly.web.toml`, `infra/fly.worker.toml`
- **Exact edits expected:** api app 4 vCPU / 8 GB with `mounts.[models]` at `/app/models`; web app shared CPU; worker same image with `process group=worker`. `release_command = "alembic upgrade head"`. `http_checks /healthz`.
- **Validation command:** `flyctl config validate -c infra/fly.api.toml`
- **Expected result:** Validate passes.
- **Recovery:** If validate fails, consult Fly schema docs and fix.

### M4: .github/workflows/release.yml
- **Files to read:** `DEPLOYMENT.md`, `RELEASE.md`
- **Files to change:** `.github/workflows/release.yml`
- **Exact edits expected:** Trigger on tag `v*.*.*`. Build + push images to registry. `flyctl deploy` staging. Run `scripts/smoke-test.sh` against staging URL. Await GitHub Environments `production` approval. `flyctl deploy` prod with bluegreen. Run smoke against prod URL.
- **Validation command:** `cat .github/workflows/release.yml`
- **Expected result:** Workflow file valid YAML with required steps in correct order.
- **Recovery:** If flyctl auth fails, ensure `FLY_API_TOKEN` secret set in repo settings.

### M5: scripts/smoke-test.sh wired against staging
- **Files to read:** `OPERATIONS.md`
- **Files to change:** `scripts/smoke-test.sh`, `apps/api/app/cli/smoke.py`
- **Exact edits expected:** smoke-test.sh accepts a BASE_URL arg defaulting to local. smoke.py CLI hits `/healthz`, `/readyz`, registers a throwaway user, uploads a fixture, polls ingest, starts a session, asserts ≥ 6 questions with a citation hyperlink that 200s.
- **Validation command:** `scripts/smoke-test.sh http://localhost:8000`
- **Expected result:** `smoke test: ok` after the full flow.
- **Recovery:** If PDF fixture too large, swap to a 5-page fixture.

### M6: Rollback drill in staging
- **Files to read:** `ROLLBACK.md`
- **Files to change:** `CHANGELOG.md`
- **Exact edits expected:** Document the executed drill in CHANGELOG and active ExecPlan Outcomes. Drill steps: cut a staging release tag with a benign deviation; `flyctl releases rollback <prev>` --app pharmsmartce-api-staging; verify `/healthz`, `/readyz`, and smoke pass after rollback.
- **Validation command:** `flyctl releases --app pharmsmartce-api-staging | head`
- **Expected result:** ≥ 2 release versions visible AND rollback to previous succeeded.
- **Recovery:** If rollback fails, check flyctl version and Fly Postgres compatibility per ROLLBACK.md.

### M7: Production deploy gate
- **Files to read:** `AGENTS.md`, `DEPLOYMENT.md`
- **Files to change:** (none)
- **Exact edits expected:** NOT APPLICABLE — this milestone is a STOP S6 by design. The agent records the staging smoke result in Outcomes and halts awaiting explicit human approval for prod deploy.
- **Validation command:** `echo 'STOP S6: production deploy awaits explicit human approval per AGENTS.md §4'`
- **Expected result:** Message printed; agent halts.
- **Recovery:** N/A — STOP condition.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] Staging smoke green
  - [ ] Rollback drill outcome recorded in Outcomes & Retrospective
  - [ ] Production deploy halted per STOP S6

## 11. Idempotence and Recovery
Image build deterministic from pinned lockfiles. `release_command` idempotent at head. Re-running the workflow on the same tag produces the same artifact.

## 12. Progress
- [x] M1: apps/api Dockerfile multi-stage
- [x] M2: apps/web Dockerfile multi-stage
- [x] M3: fly.toml configs
- [x] M4: .github/workflows/release.yml
- [x] M5: scripts/smoke-test.sh wired against staging
- [ ] M6: Rollback drill in staging
- [ ] M7: Production deploy gate

## 13. Surprises & Discoveries
- 2026-06-28 - The local smoke harness passes end-to-end on Windows once `UV_CACHE_DIR`, `TMP`, `TEMP`, and `TMPDIR` point at repo-local scratch space; the repo's Docker compose stack for db/redis/minio is healthy.
- 2026-06-27 - Docker build context needed a root `.dockerignore`; excluding caches, build outputs, `tests/`, `var/`, models, and local state kept the API image lean without hiding source files.
- 2026-06-27 - The API image needs Linux-friendly PDF magic support; `python-magic` resolves in the container, while Windows keeps `python-magic-bin` via environment markers.
- 2026-06-27 - The web image had no `public/` directory yet, so the standalone runner should not copy one.
- 2026-06-27 - Fly bluegreen is incompatible with the API's mounted model volume, so API/worker deploys use rolling while the web deploy remains bluegreen-capable.
- 2026-06-27 - The local smoke harness currently proves health/readiness plus course upload; the full session-start smoke path still awaits the missing session/generation routes.
- 2026-06-27 - The smoke harness now drives register/login/refresh, admin course upload, session start, citation URL checks, answer submission, CE record download, and logout; `/api/sessions/{id}` now returns `record_id` so the remote smoke can fetch the PDF artifact without DB access.
- 2026-06-27 - Added minimal `/login`, `/courses`, and `/sessions/[id]` web routes so the release smoke has a concrete session deep-link target.

## 14. Decision Log
- 2026-06-27 - Added `output: "standalone"` to Next config so the Docker runner can start with `node server.js` and avoid shipping the full dev toolchain.
- 2026-06-27 - API Dockerfile now stages `uv sync --frozen --no-dev`, copies the virtualenv, app, and Alembic assets, and installs `libmagic1` in the final image for PDF type checks.
- 2026-06-27 - Added Fly config templates for api/web/worker and a release workflow scaffold. API and worker use rolling deploys because the API mounts persistent model storage; web remains bluegreen-capable.
- 2026-06-27 - Fixed course creation/upload persistence by committing the course and source rows before the next request boundary so smoke and integration tests can see previously created records.
- 2026-06-27 - OpenAPI snapshot regenerated after adding course routes.
- 2026-06-27 - Added cookie-based auth, Argon2id password hashing, JWT bearer auth, refresh-token rotation, and browser-session smoke support to align the release gate with the actual user flow.

## 15. Outcomes & Retrospective
Release and deployment now have working Docker images, Fly config templates, a tag-driven workflow, and a smoke harness that exercises the real auth/course/session/CE-record path. The remaining work in this plan is the staging rollback drill and the final production gate, which are intentionally still separate from the codepath fixes.
