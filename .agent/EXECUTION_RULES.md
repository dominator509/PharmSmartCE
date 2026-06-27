# .agent/EXECUTION_RULES.md

Consolidated execution rules for any coding agent. These restate and
reinforce `AGENTS.md`. On conflict, `AGENTS.md` wins.

## 1. One Active ExecPlan
At any time, the agent is executing exactly one ExecPlan. Jumping between
unrelated plans is forbidden. If a second concern surfaces, record it in
`Surprises & Discoveries`, finish the current plan, then start a new one.

## 2. No Hidden Context
Every fact required to continue must be inside the ExecPlan, or inside
files it explicitly references. The plan must be sufficient for a new
agent with no prior conversation.

## 3. No Roadmap-Only Implementation
`ROADMAP.md` is strategic and forbidden as an implementation source. If
the roadmap describes work with no ExecPlan, the agent creates an ExecPlan
from `.agent/templates/execplan-template.md` before any code edit.

## 4. Continue by Default
After validating a milestone, proceed to the next without asking the user.
The user is consulted only on STOP conditions.

## 5. STOP-Only Stopping
Stop only for an explicit STOP condition (S1–S6) in `AGENTS.md` §4. The
report follows `AGENTS.md` §15 plus the STOP code, evidence, smallest
decision needed, and recommended default.

## 6. Anti-Drift
Implement only `Scope`. No unrelated refactors, format sweeps, dep
upgrades, or renames outside `Files to Change`. At the end,
`git diff --name-only` MUST match `Files to Change`.

## 7. Anti-Hallucination
Never invent package APIs, env vars, table names, route paths, or CLI
flags. Verify by reading repo files or installed package source. Commands
come exclusively from `COMMANDS.md`; if missing, update first with
evidence.

## 8. Anti-Fixation (Bounded Retry)
Apply the AGENTS §7 ladder: smallest fix → narrow diagnostic → simpler
path. No more than 3 same-root attempts before pivot or STOP S5.

## 9. Test Before Completion
A milestone is "done" only when its validation passes with the expected
result. An ExecPlan is "done" only when `scripts/verify.sh` exits 0.

## 10. Diff Review
Before declaring an ExecPlan complete, run `git diff --name-only` and
compare to `Files to Change`. Any extra file must be justified in
`Decision Log` or reverted.

## 11. Final Response
Follow `AGENTS.md` §15 exactly: ExecPlan, changed files, commands +
exit codes, acceptance criteria status with evidence, decisions,
assumptions confirmed/changed, remaining risks, prod-readiness impact.
