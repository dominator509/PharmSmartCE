@C:\Users\domin\.codex\RTK.md

# AGENTS.md — Control Plane for Coding Agents

This file is the highest-priority operational document for any coding agent
(human or LLM) working in this repository. Read this first.

For compact Serena/Obsidian navigation context, read `REPO_BRIEF.md` after
this file. `REPO_BRIEF.md` is an index only; it does not override these rules.

## 1. Mission
Implement PharmSmartCE — cloud SaaS generating dynamic per-user pharmacist
CE questions grounded ONLY in uploaded CE source material via a self-hosted
CPU-only LLM, with every question and rationale carrying a verifiable
source-citation hyperlink. You operate in bounded autonomy: continue by
default, stop only for explicit STOP conditions in §4.

## 2. Source-of-Truth Priority (higher wins on conflict)
1. Current explicit user instruction in this session.
2. `AGENTS.md` (this file).
3. Active ExecPlan in `.agent/execplans/`.
4. Existing repository code and tests on disk.
5. `ARCHITECTURE.md`.
6. Relevant spec in `.agent/specs/`.
7. `ROADMAP.md`.

If a user instruction conflicts with a STOP condition, the STOP condition
wins unless the user explicitly acknowledges the risk.

## 3. Required Workflow
1. Read `AGENTS.md`.
2. Read `COMMANDS.md`.
3. Read `.agent/PLANS.md`.
4. Read the active ExecPlan in `.agent/execplans/`.
5. Run `scripts/preflight.sh`. Fix the cause before editing feature code.
6. Complete milestones in order.
7. After each milestone: run its validation command, verify the expected
   result, tick `Progress`, append notes to `Surprises & Discoveries` or
   `Decision Log`.
8. Continue autonomously to the next milestone.
9. Stop only under a STOP condition (§4).

**Do not ask the user for next steps. Proceed autonomously through the
active ExecPlan unless a STOP condition applies.**

## 4. STOP Conditions
Stop and report ONLY for:
- **S1.** Missing required secret, credential, paid service account, or
  external account that cannot be substituted by a documented local mock.
- **S2.** Any action that may destroy user/production data or irreversible
  cloud resources (dropping prod table, deleting bucket, rotating prod
  secret, force-pushing protected branch).
- **S3.** Legal/security/financial judgment not already resolved by spec or
  ExecPlan (e.g., "enable OpenAI billing?", "collect SSN?").
- **S4.** User-visible behavior choice with materially different alternatives
  not resolved by the spec.
- **S5.** Required tests cannot run after bounded-retry recovery exhausted
  (§7).
- **S6.** Production deployment or irreversible migration without explicit
  user permission.

When stopping, the report MUST include: S code, evidence (file path, terminal
output, line numbers), smallest decision needed, recommended default.

## 5. Anti-Drift Rules
- Implement only what the active ExecPlan's `Scope` describes.
- No broad refactors, file moves, format sweeps, dep upgrades, or unrelated
  cleanup unless the ExecPlan explicitly requires it.
- Before opening unrelated files: "Does the ExecPlan require this?" If no,
  don't open them.
- After implementation, `git diff --name-only` MUST match the ExecPlan's
  `Files to Change`. Justify extras in Decision Log or revert.
- `ROADMAP.md` is strategic only. Never implement directly from it.

## 6. Anti-Hallucination Rules
- Do not invent package APIs, function names, decorators, CLI flags, env
  vars, config keys, route paths, table names, column names, migration ids.
- Confirm names by reading files (`grep -R`, viewing the file, reading
  installed package source).
- Use only commands in `COMMANDS.md`. If a needed command is missing, update
  `COMMANDS.md` first with evidence.
- For LLM/library specifics: open the library's source.
- Record any unverifiable assumption in the active ExecPlan's `Decision Log`
  with the smallest reversible default.

## 7. Anti-Fixation Rules (Bounded Retry)
- **1st failure:** read full error, identify smallest plausible cause,
  smallest targeted fix, re-run.
- **2nd same-root failure:** narrower diagnostic (single test `-x -vv`, tiny
  isolation script). Do NOT rewrite unrelated code.
- **3rd same-root failure:** stop the approach, record failed hypotheses in
  `Surprises & Discoveries`, choose a simpler implementation path. Continue
  if safe.

If still blocked after 3rd attempt AND no simpler path exists → S5.

## 8. Dependency Rules
Before adding ANY dependency:
1. Verify functionality not already available.
2. Verify it cannot be implemented in ≤ 50 lines.
3. Pin exact version. Add only to `pyproject.toml` or `package.json`.
4. Run `scripts/dependency-audit.sh`. Resolve findings.
5. Document in Decision Log; add ADR if non-trivial.

Forbidden: `*`, `latest`, floating versions in lockfiles.

## 9. File Creation Rules
- New files live within the repo map in `ARCHITECTURE.md`. Update map first
  if needed.
- `.gitignore` all generated artifacts (builds, coverage, `*.gguf`, FAISS
  indexes, uploaded PDFs).
- Never commit secrets. `.env.example` for schema; deploy platform store for
  values.
- LLM weights (`*.gguf`) never committed; downloaded by `scripts/install.sh`
  to `models/` (gitignored).
- Uploaded CE source docs never committed; object storage in non-local envs,
  `var/uploads/` (gitignored) locally.

## 10. Testing Rules
- Every new behavior REQUIRES a test that fails without the change.
- LLM tests use deterministic `FakeLLM` adapter unless marked
  `@pytest.mark.llm_smoke` (excluded from CI).
- A milestone is "done" only when its validation command passes with the
  expected result.

## 11. Documentation Update Rules
- Changed a command → update `COMMANDS.md` same change.
- Changed a route/contract → update `.agent/specs/SPEC-003-api-contracts.md`.
- Changed data model → update `.agent/specs/SPEC-002-data-model.md` AND add
  Alembic migration in same change.
- Non-trivial architectural choice → add ADR to `DECISIONS.md`.

## 12. Security Rules
- Never log secrets, JWTs, refresh tokens, passwords, API keys, or full
  bodies of `/auth/*` requests. Use redaction processor in
  `apps/api/app/observability/logging.py`.
- Parameterized SQL only.
- Pydantic models validate all HTTP inputs.
- All outbound LLM prompts MUST go through
  `apps/api/app/services/generation/grounded_llm.py`. No raw LLM calls
  elsewhere.
- Every persisted `Question` row MUST have non-null `source_doc_id`,
  `source_page`, `source_span`. Schema NOT NULL + service invariant.

## 13. Production Data Rules
- Never run destructive migration against env named `prod` or `production`
  without explicit user instruction matching exactly:
  `RUN-DESTRUCTIVE-MIGRATION-IN-PROD <migration_id>`. Otherwise S2/S6.
- Never run `DROP`, `TRUNCATE`, `DELETE FROM` without `WHERE`, or
  `alembic downgrade base` against a non-local database.
- Backups verified before any destructive change.

## 14. Definition of Done
ALL must be true:
- All acceptance criteria satisfied.
- `scripts/verify.sh` exits 0.
- ExecPlan `Progress` fully checked.
- `Outcomes & Retrospective` written.
- `git diff --name-only` matches `Files to Change` (extras justified or
  reverted).
- Impacted docs updated.
- Remaining risks listed.

## 15. Final Response Requirements
Every final agent response MUST include:
1. ExecPlan completed (path).
2. Changed files (`git diff --name-only`).
3. Commands run + exit codes.
4. Acceptance criteria status (each ✅/❌ with evidence).
5. Decisions made (or "none").
6. Assumptions confirmed/changed (or "none").
7. Remaining risks (or "none").
8. Whether production-readiness status changed.

If a STOP applied, also include: S code, evidence, smallest decision needed,
recommended default.
