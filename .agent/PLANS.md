# .agent/PLANS.md — The ExecPlan Standard

An ExecPlan is a self-contained implementation document for one feature or
system change. **A new agent with no prior conversation must be able to
continue from the ExecPlan alone.**

If a section in the active ExecPlan is empty, the agent fills it in (with
evidence from the repo) before continuing. ExecPlans are living documents
during execution and finalized at completion.

## Required Sections (every ExecPlan)
1. **Purpose / Big Picture** — One-paragraph statement of why this plan
   exists and what user-visible outcome it produces.
2. **Scope** — Bullet list of things this plan WILL do.
3. **Non-goals** — Bullet list of things this plan WILL NOT do.
4. **Context and Orientation** — Where in the system this plan lands.
5. **Files to Read First** — Concrete repository paths.
6. **Files to Change** — Concrete repository paths expected.
7. **Interfaces and Contracts** — APIs, schemas, types, adapter Protocols.
8. **Milestones** — Ordered list. Each has goal, files to read, files to
   change, exact edits expected, validation command, expected result,
   recovery instruction.
9. **Concrete Steps** — Short prose of overall strategy.
10. **Validation and Acceptance** — All milestone validations + `verify.sh`
    + explicit acceptance criteria block.
11. **Idempotence and Recovery** — How to re-run safely.
12. **Progress** — Checkbox list, one per milestone.
13. **Surprises & Discoveries** — Free-form notes.
14. **Decision Log** — Inline; promote non-trivial to ADR.
15. **Outcomes & Retrospective** — Filled at completion.

## Execution Rules
- Exactly **one** active ExecPlan at a time.
- Milestones **in order**. No skipping.
- Validate after each milestone with the documented command.
- Tick `Progress`. Add notes. Continue.
- Update `Decision Log` for every non-trivial choice.
- Stop ONLY for STOP conditions in `AGENTS.md` §4.
- Never implement directly from `ROADMAP.md`.

## Milestone Rules
A milestone is small enough that:
- One agent session can complete it.
- One command can validate it.
- One paragraph can describe what changed.

If a milestone is larger, split it before starting.

## Validation Rules
Every milestone has a runnable validation command from `COMMANDS.md`. If
missing, update `COMMANDS.md` first (per AGENTS §6).

## Acceptance Rules
ExecPlan-level acceptance = ALL of:
- Every milestone validation passes.
- `scripts/verify.sh` exits 0.
- Every explicit acceptance criterion satisfied with evidence.

## Idempotence Rules
- Every step re-runnable. Re-running a completed milestone is a no-op.
- Migrations identified by Alembic revision id; re-running\
  `alembic upgrade head` is a no-op when at head.
- Background jobs accept `idempotency_key`; re-runs after success are
  no-ops (Architectural Invariant I9).

## Recovery Rules
Bounded retry per AGENTS §7:
- 1st failure → smallest targeted fix.
- 2nd same-root failure → narrower diagnostic; no broad rewrites.
- 3rd same-root failure → simpler implementation path; record failed
  hypotheses.
- Still blocked + no simpler path → STOP S5.

## Progress Update Rules
After each milestone, append to `Progress`:
```
- [x] M3: Implement RAGRetriever — 2026-01-23T14:02Z — tests/unit/test_rag.py 12/12 pass.
```

## Decision Log Rules
Capture inline. Format:
```
- 2026-01-23 — Context: FAISS index path collision under parallel ingest.
  Decision: Per-course subdirectory. Alternative: shared dir with locks
  (more fragile). Consequence: small disk overhead.
```
Promote to ADR if architectural.

## Completion Rules
See `AGENTS.md` §14 (Definition of Done) and §15 (Final Response
Requirements). At completion, run the `final-review.md` prompt procedure.
