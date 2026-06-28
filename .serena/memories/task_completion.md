# task_completion
- Milestone done: documented validation command passes with expected result, then update active ExecPlan Progress and notes.
- ExecPlan done per AGENTS.md: all acceptance criteria satisfied; scripts/verify.sh exits 0; all Progress boxes checked; Outcomes & Retrospective filled; impacted docs updated; remaining risks listed.
- Required final checks for code tasks: milestone validation(s), scripts/verify.sh, git diff --name-only, compare changed files to ExecPlan Files to Change.
- For backend persistence work, confirm docker compose -f infra/docker-compose.yml ps is healthy and python -m uv run --directory apps/api alembic upgrade head reaches the head revision.
- For repo setup tasks, keep the final proof compact: list changed files, note any repo-local config found, and call out environment blockers separately from repo defects.
- Final response must include: ExecPlan path, changed files, commands + exit codes, acceptance criteria with evidence, decisions, assumptions, remaining risks, production-readiness impact.
- If STOP condition applies, include S code, evidence path/output/line numbers, smallest decision needed, and recommended default.
- For Serena/Obsidian setup tasks, safe validation is config load via Serena activation plus lightweight YAML/JSON/Markdown checks; do not run installs or destructive commands.
- On Windows, the Serena wrapper serena.cmd may be needed to force UTF-8, and repo command shims now include scripts/bin/uv.cmd and scripts/bin/uvx.cmd.
