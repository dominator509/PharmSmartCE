# core

- Repo is currently a blueprint/control-plane checkout, not an implemented app tree: root docs + `.agent/` + `scripts/`; intended `apps/`, `packages/shared/`, `infra/`, `models/`, `var/` are absent until an ExecPlan creates them.
- Authority chain: current user instruction -> `AGENTS.md` -> active `.agent/execplans/*` -> disk code/tests -> `ARCHITECTURE.md` -> `.agent/specs/*` -> `ROADMAP.md`.
- `ROADMAP.md` is strategy only; implementation must come from an active ExecPlan or a newly created ExecPlan template.
- Start any agent run by reading `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`, active ExecPlan, then `REPO_BRIEF.md` for compact navigation context.
- No active-marker file exists; README says pick active ExecPlan from `.agent/execplans/`; current pack guidance starts with `EP-000-repository-discovery.md`.
- Project invariants: source-grounded pharmacist CE generation, citations on every persisted question, CPU-only local LLM default, optional OpenAI only behind feature flag and cost cap.
- Read `mem:tech_stack` for planned stack/tools, `mem:suggested_commands` for allowed command surface, `mem:conventions` for guardrails, `mem:task_completion` for done checks.
- Read `mem:backend/core` when creating or reviewing `apps/api`; read `mem:frontend/core` when creating or reviewing `apps/web`.