# core

- Repo is a real monorepo checkout now: `apps/api` backend, `apps/web` frontend, `infra/`, `.agent/`, `scripts/`, `REPO_BRIEF.md`, `.serena/`, `.obsidian/`.
- Authority chain stays: current user instruction -> `AGENTS.md` -> active `.agent/execplans/*` -> disk code/tests -> `ARCHITECTURE.md` -> `.agent/specs/*` -> `ROADMAP.md`.
- `ROADMAP.md` is strategy only; implementation runs through an active ExecPlan.
- Control-plane docs to read first: `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`, active ExecPlan, then `REPO_BRIEF.md` for compact navigation context.
- Project invariant set: pharmacist CE questions must stay source-grounded, every persisted question keeps citation fields, CPU-only local LLM is default, OpenAI remains optional and capped.
- For module detail, read `mem:backend/core` for `apps/api` and `mem:frontend/core` for `apps/web`.
- For working habits, read `mem:tech_stack`, `mem:suggested_commands`, `mem:conventions`, and `mem:task_completion`.