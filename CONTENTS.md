# PharmSmartCE Blueprint Pack — Contents

This blueprint pack ships in **two ZIPs**. Unzip BOTH into the same
`PharmSmartCE/` repository root. There is no file overlap between them.

## Pack 1 — Strategic & Reference (this zip)
- Root markdown control docs (PROJECT_BRIEF, AGENTS, COMMANDS, ARCHITECTURE,
  ROADMAP, DECISIONS, TESTING, SECURITY, ENVIRONMENT, DEPLOYMENT, OPERATIONS,
  OBSERVABILITY, PRODUCTION_READINESS, RELEASE, ROLLBACK, CONTRIBUTING,
  ASSUMPTIONS, README)
- `.agent/PLANS.md`, `.agent/EXECUTION_RULES.md`
- `.agent/prompts/` (4 paste-ready agent prompts)
- `.agent/specs/` (9 behavior specs SPEC-000..008)
- `.agent/templates/` (5 reusable templates)
- `scripts/` (14 executable shell scripts)

## Pack 2 — Implementation (next zip)
- `.agent/execplans/` (11 ordered ExecPlans EP-000..010)
- `.agent/checklists/` (9 operational checklists)

## How to use
1. Unzip Pack 1, then unzip Pack 2 over the same directory.
2. Read `README.md`, then `PROJECT_BRIEF.md`, then `AGENTS.md`.
3. Open the first ExecPlan (`.agent/execplans/EP-000-repository-discovery.md`)
   and follow it. Do not implement from `ROADMAP.md`.
