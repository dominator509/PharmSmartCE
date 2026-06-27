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
  - [ ] `scripts/preflight.sh` exits 0 — `preflight: ok`
  - [ ] `ASSUMPTIONS.md` reflects current reality
  - [ ] `COMMANDS.md` has no broken commands
  - [ ] Baseline `.gitignore` covers secrets and generated artifacts

## 11. Idempotence and Recovery
Re-running this plan is a no-op: it only reads state and updates docs. If a doc was updated, git tracks the diff; re-running yields no further change.

## 12. Progress
- [ ] M1: Inventory root contents and git state
- [ ] M2: Verify tool versions
- [ ] M3: Reconcile assumptions with reality
- [ ] M4: Reconcile commands with reality
- [ ] M5: Create baseline .gitignore

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
