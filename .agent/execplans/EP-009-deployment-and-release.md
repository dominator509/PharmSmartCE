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
- [ ] M1: apps/api Dockerfile multi-stage
- [ ] M2: apps/web Dockerfile multi-stage
- [ ] M3: fly.toml configs
- [ ] M4: .github/workflows/release.yml
- [ ] M5: scripts/smoke-test.sh wired against staging
- [ ] M6: Rollback drill in staging
- [ ] M7: Production deploy gate

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
