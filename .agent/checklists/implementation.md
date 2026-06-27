# Checklist: Implementation (per milestone)

- [ ] Read `AGENTS.md`
- [ ] Read `COMMANDS.md`
- [ ] Read `.agent/PLANS.md`
- [ ] Read active ExecPlan in full
- [ ] Inspect existing patterns before editing (don't invent APIs)
- [ ] Implement one milestone at a time
- [ ] Do not broaden scope
- [ ] Update ExecPlan `Progress` after each milestone with timestamp + one-line note
- [ ] Validate the milestone with the documented command
- [ ] Apply bounded retry on failure (AGENTS §7)
- [ ] Continue autonomously unless a STOP condition applies
