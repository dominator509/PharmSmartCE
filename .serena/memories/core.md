# core
- Repo shape: `apps/api` backend, `apps/web` frontend, plus `infra/`, `.agent/`, `scripts/`, `REPO_BRIEF.md`, `.serena/`, and local-only `.obsidian/`.
- Authority chain: current user instruction -> `AGENTS.md` -> active `.agent/execplans/*` -> disk code/tests -> `ARCHITECTURE.md` -> `.agent/specs/*` -> `ROADMAP.md`.
- `ROADMAP.md` is strategy only; implementation work follows the active ExecPlan.
- Control-plane docs to read first are `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`, the active ExecPlan, and `REPO_BRIEF.md`.
- Product invariant: pharmacist CE content stays source-grounded; persisted questions keep citation fields; CPU-only local LLM remains the default path and OpenAI stays optional/guarded.
- For module detail, read `mem:backend/core` for `apps/api` and `mem:frontend/core` for `apps/web`.
- For workflow detail, read `mem:tech_stack`, `mem:suggested_commands`, `mem:conventions`, and `mem:task_completion`.
- Serena setup stays headless, LSP-backed, and additive.