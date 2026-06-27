# Checklist: Final Review

Run before declaring an ExecPlan done.

- [ ] All acceptance criteria met with evidence (test name / command / log line)
- [ ] `scripts/verify.sh` exit 0
- [ ] `git diff --name-only` matches the ExecPlan's `Files to Change` (extras justified or reverted)
- [ ] Docs updated where impacted (specs, COMMANDS, ARCHITECTURE, CHANGELOG)
- [ ] No secrets in the diff
- [ ] No production data changes
- [ ] Remaining risks documented in `Surprises & Discoveries`
- [ ] `Outcomes & Retrospective` filled in the ExecPlan
- [ ] Final response per `AGENTS.md` §15 produced
