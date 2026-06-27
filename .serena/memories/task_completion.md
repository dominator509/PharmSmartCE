# task_completion

- Milestone done: documented validation command passes with expected result, then update active ExecPlan `Progress` and notes.
- ExecPlan done per `AGENTS.md`: all acceptance criteria satisfied; `scripts/verify.sh` exits 0; all `Progress` boxes checked; `Outcomes & Retrospective` filled; impacted docs updated; remaining risks listed.
- Required final checks for code tasks: milestone validation(s), `scripts/verify.sh`, `git diff --name-only`, compare changed files to ExecPlan `Files to Change`.
- Final response must include: ExecPlan path, changed files, commands + exit codes, acceptance criteria with evidence, decisions, assumptions, remaining risks, production-readiness impact.
- If STOP condition applies, include S code, evidence path/output/line numbers, smallest decision needed, and recommended default.
- For this Serena/Obsidian setup class of task, safe validation is config load via Serena activation plus lightweight YAML/JSON/Markdown checks; do not run installs or destructive commands.