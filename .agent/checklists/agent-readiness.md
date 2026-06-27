# Checklist: Agent Readiness

Use before starting work on an ExecPlan.

- [ ] Exactly one active ExecPlan identified
- [ ] ExecPlan is self-contained (no hidden context)
- [ ] Exact `Files to Read First` listed
- [ ] Exact `Files to Change` listed
- [ ] Exact commands listed (and all come from `COMMANDS.md`)
- [ ] Expected outputs documented per milestone
- [ ] Observable acceptance criteria present
- [ ] Explicit non-goals listed
- [ ] STOP conditions (S1–S6) referenced
- [ ] Recovery rules per milestone
- [ ] Bounded-retry rule (AGENTS §7) acknowledged
- [ ] Diff-review rule (compare `git diff --name-only` to `Files to Change`) acknowledged
- [ ] No hidden context required to proceed
- [ ] No vague requirements remaining
