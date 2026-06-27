# Prompt: Final Review of an ExecPlan

Paste this prompt to perform final review before declaring an ExecPlan done.

---

You are a coding agent performing final review of the ExecPlan at
**[EXECPLAN_PATH]**.

Procedure:

1. Read `AGENTS.md` §14 (Definition of Done) and §15 (Final Response
   Requirements).
2. Run `scripts/verify.sh`. If non-zero, switch to the
   `debug-validation-failure.md` procedure, fix, then return here.
3. If the ExecPlan touches production-readiness items, run
   `scripts/production-readiness-check.sh`. If non-zero, identify the
   failed check, log it in `Surprises & Discoveries`, fix or escalate.
4. Run `git diff --name-only`. Compare with `Files to Change`:
   - Any file in the diff but NOT in `Files to Change` must be justified
     in `Decision Log` (with a one-line rationale) or reverted.
   - Any file in `Files to Change` but NOT in the diff is acceptable only
     if the milestone explicitly says "no change required".
5. Verify each explicit acceptance criterion. For each, record evidence
   (test name, command output, log line) inline next to the criterion.
6. Fill `Outcomes & Retrospective`:
   - What landed.
   - What deferred (with reason).
   - What went well.
   - What to change in future ExecPlans.
7. Produce the final report per `AGENTS.md` §15.

If any acceptance criterion is ❌, the ExecPlan is NOT done. Either continue
work (return to milestone execution) or STOP with the right S code.
