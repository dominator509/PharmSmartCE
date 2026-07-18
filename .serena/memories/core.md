# PharmSmartCE core
- Monorepo control-plane repo for a planned pharmacist CE SaaS.
- Top-level authority surface: `AGENTS.md`, `COMMANDS.md`, `.agent/PLANS.md`, active ExecPlan in `.agent/execplans/`, then `ARCHITECTURE.md` and repo code/tests.
- Local-only state stays local unless explicitly requested: `.obsidian/`, `.serena/`, `.tmp/`, `var/`, model blobs, caches, build output.
- Product invariants: CE generation must stay grounded in uploaded source material; all persisted questions need citation fields; all outbound LLM calls route through `apps/api/app/services/generation/grounded_llm.py`.
- Read `mem:backend/core` and `mem:frontend/core` for module-specific notes; use `mem:tech_stack`, `mem:suggested_commands`, `mem:conventions`, and `mem:task_completion` for shared operational context.