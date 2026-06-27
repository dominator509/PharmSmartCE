# Prompt: Continue ExecPlan

Paste this prompt into a coding agent to continue a partially completed
ExecPlan.

---

You are a coding agent in the PharmSmartCE repository. A previous agent left
the ExecPlan at **[EXECPLAN_PATH]** partially complete. Your task is to
continue it to completion.

Procedure:

1. Read `AGENTS.md`.
2. Read `COMMANDS.md`.
3. Read `.agent/PLANS.md` to recall the standard.
4. Read **[EXECPLAN_PATH]** end-to-start: skim `Outcomes & Retrospective`
   first (if started), then `Decision Log`, then `Surprises & Discoveries`,
   then `Progress`, then the rest. This absorbs prior context fast.
5. Identify the first unchecked `Progress` checkbox. That is your resume
   point.
6. Validate prior assumptions still hold:
   - Run `scripts/preflight.sh`.
   - Run `scripts/verify.sh` and note any regressions (record them in
     `Surprises & Discoveries`).
7. Resume at the first incomplete milestone. Follow the milestone procedure
   from `execute-active-execplan.md`.
8. Continue autonomously through remaining milestones.
9. Stop only under a STOP condition in `AGENTS.md` §4.
10. At completion: `scripts/verify.sh`, diff review, fill\
    `Outcomes & Retrospective`, final report per `AGENTS.md` §15.

Notes:
- Trust the prior agent's `Decision Log`. Do not undo decisions without
  recording a counter-decision with rationale.
- If `Progress` is empty, treat as a fresh execution and use
  `execute-active-execplan.md` procedure.
