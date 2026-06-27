# Prompt: Execute Active ExecPlan

Paste this prompt into a coding agent to execute an ExecPlan to completion.

---

You are a coding agent operating in the PharmSmartCE repository. Your task
is to execute the ExecPlan at **[EXECPLAN_PATH]** to completion.

Optional additional context from the user: **[OPTIONAL_USER_REQUEST]**.

Procedure (follow exactly):

1. Read `AGENTS.md`. Treat its STOP conditions, anti-drift, anti-hallucination,
   and bounded-retry rules as binding.
2. Read `COMMANDS.md`. Use ONLY commands from this file. If a needed command
   is missing, update `COMMANDS.md` first with evidence from the repo.
3. Read `.agent/PLANS.md`.
4. Read **[EXECPLAN_PATH]** start-to-finish, including `Files to Read First`,
   `Scope`, `Non-goals`, `Milestones`, and `Validation and Acceptance`.
5. Run `scripts/preflight.sh`. If it fails, fix the cause before editing
   feature code.
6. Implement milestones in order. For each milestone:
   - Read the milestone's listed files.
   - Make the documented edits to the listed `Files to change`.
   - Run the milestone's `Validation command`.
   - Verify the `Expected result`.
   - Tick the corresponding `Progress` checkbox with a timestamp and a
     one-line note.
   - If validation fails, apply the bounded-retry ladder (`AGENTS.md` §7).
7. Continue autonomously to the next milestone. **Do not ask the user for
   next steps.**
8. Do not implement from `ROADMAP.md` directly. Do not broaden scope.
9. Stop only under a STOP condition in `AGENTS.md` §4.
10. At completion:
    - Run `scripts/verify.sh` and confirm exit 0.
    - Run `git diff --name-only` and compare with `Files to Change`.
      Justify or revert extras.
    - Fill `Outcomes & Retrospective`.
    - Produce the final report per `AGENTS.md` §15.

Forbidden in this run:
- Inventing commands, APIs, env vars, table names, routes, or migration ids.
- Disabling `CitationValidator`, `InjectionDetector`, or the OpenAI cost cap.
- Touching production data or running `alembic downgrade base` against any
  non-local DB.
- Broad refactors outside `Files to Change`.
