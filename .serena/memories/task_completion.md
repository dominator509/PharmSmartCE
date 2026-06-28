# task_completion
- A coding milestone is done only after the relevant validation command passes with the expected result, then ExecPlan Progress and notes are updated.
- Repo-level done criteria: acceptance criteria met, `scripts/verify.sh` exits 0, ExecPlan Progress is fully checked, Outcomes & Retrospective is written, impacted docs are updated, and remaining risks are listed.
- Final proof should stay compact: list changed files, note any repo-local config found, and separate environment blockers from repo defects.
- For backend persistence work, confirm `docker compose -f infra/docker-compose.yml ps` is healthy and `uv run --directory apps/api alembic upgrade head` reaches head revision when those flows are part of the task.
- For setup tasks, safe validation is Serena project activation plus lightweight YAML/JSON/Markdown checks; avoid installs or destructive commands.
- Final responses should include the ExecPlan path, changed files, commands with exit codes, acceptance status, decisions, assumptions, remaining risks, and whether production-readiness status changed.
- If a STOP condition applies, include the S code, evidence path/output/line numbers, the smallest decision needed, and the recommended default.
- After onboarding, the user can run `serena memories check` from the project root to sanity-check the memory graph.