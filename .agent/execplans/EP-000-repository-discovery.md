# EP-000 — Repository Discovery

**Phase:** P0

## 1. Purpose / Big Picture
Inventory the greenfield PharmSmartCE repository, confirm tool versions, and reconcile assumptions before any feature work. This ExecPlan is mandatory for any unfamiliar repository state.

## 2. Scope
- Inventory root contents and git state
- Verify tool versions (Python 3.11, Node 20, Docker 24+, uv 0.5+, pnpm 9)
- Reconcile `ASSUMPTIONS.md` and `COMMANDS.md` with reality
- Establish baseline `.gitignore`

## 3. Non-goals
- Implement application code
- Create the FastAPI or Next.js skeletons (deferred to EP-001)
- Run any non-local command

## 4. Context and Orientation
This is the first plan. There is no prior code. Read `AGENTS.md` and `ROADMAP.md` Phase 0 for the strategic context. The output is a verified `COMMANDS.md`, a reconciled `ASSUMPTIONS.md`, and a baseline `.gitignore`.

## 5. Files to Read First
- `AGENTS.md`
- `ROADMAP.md`
- `COMMANDS.md`
- `ASSUMPTIONS.md`
- `ENVIRONMENT.md`

## 6. Files to Change
- `COMMANDS.md (if needed)`
- `ASSUMPTIONS.md (if needed)`
- `.gitignore (new)`

## 7. Interfaces and Contracts
No external interfaces. This plan only records reality and writes docs.

## 8. Milestones

### M1: Inventory root contents and git state
- **Files to read:** `.`
- **Files to change:** (none)
- **Exact edits expected:** No file edits. Output of `ls -la` and `git status` captured in Surprises & Discoveries.
- **Validation command:** `git status && ls -la`
- **Expected result:** Clean git status; only blueprint pack files in root.
- **Recovery:** If unexpected files present, list them in Surprises & Discoveries; do not delete.

### M2: Verify tool versions
- **Files to read:** `ENVIRONMENT.md`
- **Files to change:** (none)
- **Exact edits expected:** Record version output for each tool in Surprises & Discoveries.
- **Validation command:** `python --version && node --version && docker --version && uv --version && pnpm --version`
- **Expected result:** All commands print versions matching `ENVIRONMENT.md` minimums.
- **Recovery:** If a tool is missing/too old, follow `ENVIRONMENT.md` install commands. If still missing → STOP S1.

### M3: Reconcile assumptions with reality
- **Files to read:** `ASSUMPTIONS.md`
- **Files to change:** `ASSUMPTIONS.md (if needed)`
- **Exact edits expected:** For each row in `ASSUMPTIONS.md`, confirm or update. Add a note to Decision Log for changes.
- **Validation command:** `grep -c '^|' ASSUMPTIONS.md`
- **Expected result:** Row count matches before and after (no rows lost).
- **Recovery:** If row count drops, restore from git and redo edits.

### M4: Reconcile commands with reality
- **Files to read:** `COMMANDS.md`
- **Files to change:** `COMMANDS.md (if needed)`
- **Exact edits expected:** Confirm every command in `COMMANDS.md` is the one that will be used after EP-001. Update only with evidence.
- **Validation command:** `ls scripts/`
- **Expected result:** All scripts referenced in COMMANDS.md exist.
- **Recovery:** If a script is missing, leave a TODO in COMMANDS.md and add a note; EP-001 will create the script.

### M5: Create baseline .gitignore
- **Files to read:** `ARCHITECTURE.md`
- **Files to change:** `.gitignore`
- **Exact edits expected:** Add: `__pycache__/`, `.venv/`, `node_modules/`, `.next/`, `dist/`, `build/`, `models/`, `var/`, `*.gguf`, `*.faiss`, `.env`, `.env.local`, `.coverage`, `htmlcov/`, `playwright-report/`, `test-results/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`.
- **Validation command:** `test -f .gitignore && grep -qE '\.env$' .gitignore && grep -q 'models/' .gitignore`
- **Expected result:** Both greps succeed (exit 0).
- **Recovery:** If grep fails, re-add missing lines.

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry (AGENTS §7) on
any failure. Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [x] `scripts/preflight.sh` exits 0 — `preflight: ok`
  - [x] `ASSUMPTIONS.md` reflects current reality
  - [x] `COMMANDS.md` has no broken commands
  - [x] Baseline `.gitignore` covers secrets and generated artifacts

## 11. Idempotence and Recovery
Re-running this plan is a no-op: it only reads state and updates docs. If a doc was updated, git tracks the diff; re-running yields no further change.

## 12. Progress
- [x] M1: Inventory root contents and git state - 2026-06-27 - `git status && ls -la` exited 0; root includes prior GitHub/Serena/Obsidian setup plus ignored `.tools/`.
- [x] M2: Verify tool versions - 2026-06-27 - Python 3.11.15, Node v20.20.2, Docker 29.5.3, uv 0.11.25, pnpm 9.15.0.
- [x] M3: Reconcile assumptions with reality - 2026-06-27 - `grep -c '^|' ASSUMPTIONS.md` returned 20 after adding EP-000 review notes.
- [x] M4: Reconcile commands with reality - 2026-06-27 - `ls scripts/` listed all 14 scripts referenced by `COMMANDS.md`.
- [x] M5: Create baseline .gitignore - 2026-06-27 - `.gitignore` covers env files, caches, builds, models, `*.gguf`, `*.faiss`, `var/`, and local `.tools/`; validation exited 0.

## 13. Surprises & Discoveries
- 2026-06-27 - M1: Repository is no longer a pristine blueprint-only folder. It has been initialized as Git repo `main` tracking `origin/main`, and prior setup added `.serena/`, `.obsidian/`, `.gitattributes`, `REPO_BRIEF.md`, and a local ignored `.tools/` toolchain directory.
- 2026-06-27 - M1: `git status` reports `.gitignore` modified because `.tools/` was added to keep the repo-local Node 20 toolchain out of commits.
- 2026-06-27 - M1/M2: Git and Docker commands warn that `C:\Users\domin/.config/git/ignore` and `C:\Users\domin\.docker\config.json` are permission-denied in this managed Codex environment; version checks still complete.
- 2026-06-27 - M2: Required tools are available through the coding PATH after setup: Python 3.11.15 via uv-managed CPython, Node v20.20.2 via repo-local `.tools`, uv 0.11.25, pnpm 9.15.0, Git sh at `C:\Program Files\Git\usr\bin`, Docker 29.5.3, Docker Compose v5.1.4.
- 2026-06-27 - M3: `ASSUMPTIONS.md` table row count stayed 20; A11 is confirmed locally and remaining assumptions are still deferred to their named ExecPlans.
- 2026-06-27 - M4: `COMMANDS.md` script references match the current `scripts/` directory; no command table edits needed.
- 2026-06-27 - M5: `.gitignore` already existed from repository publishing; added `.tools/` for local toolchain and `*.faiss` to match EP-000 expected generated artifacts.
(empty — append entries here as they occur)

## 14. Decision Log
- 2026-06-27 - Context: Machine PATH had Python 3.14, Node 24, no `uv`, no `sh`, and PowerShell-blocked global pnpm. Decision: Install/wire repo-safe local tooling: uv via user Python, Python 3.11 via uv, portable Node v20.20.2 + pnpm 9.15.0 under ignored `.tools/`, Git `usr\bin` for `sh`, and HKCU `TEMP`/`TMP` to `C:\tmp`. Alternative: replace system Node/Python globally (higher blast radius). Consequence: repo commands can run with the required versions while avoiding global downgrades.
- 2026-06-27 - Context: `ASSUMPTIONS.md` is mostly forward-looking for EP-001 through EP-010. Decision: Add compact EP-000 review notes instead of rewriting architectural assumptions before their owning ExecPlans. Alternative: mark each future assumption as unverified in-table (noisy). Consequence: table row count remains stable and current reality is recorded.
- 2026-06-27 - Context: `git diff --name-only` includes `.agent/execplans/EP-000-repository-discovery.md`, which is not listed in Files to Change. Decision: Keep the ExecPlan diff because AGENTS/PLANS require progress, discoveries, decisions, and outcomes to be recorded in the active ExecPlan. Alternative: leave completion evidence only in chat (not durable). Consequence: the extra file is justified.
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
- Landed: EP-000 repository discovery is complete. The repo has verified local toolchain commands, reconciled assumptions notes, confirmed command/script inventory, and a baseline `.gitignore` that covers secrets, caches, builds, local runtime state, model/index artifacts, and repo-local `.tools/`.
- Deferred: Application skeletons, dependency manifests, CI workflow, and real app tests remain for EP-001 and later ExecPlans.
- Went well: Repo-local Node 20 and uv-managed Python 3.11 avoided replacing newer system runtimes while satisfying project requirements.
- Improve later: Add a Windows/Codex shell bootstrap script or docs note once EP-001 creates real manifests, so future agents do not need to rediscover PATH/TEMP quirks.
- Remaining risks: Docker and Git still warn about permission-denied user-home config files in this managed environment; commands used by EP-000 still passed. Current `verify.sh` is green with intentional skips because apps are not bootstrapped yet.
