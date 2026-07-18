# Task completion
- Normal coding task done path: run the repo validation sequence ending with `scripts/verify.sh`; for backend-heavy changes that usually includes preflight, lint, format-check, typecheck, unit tests, integration tests, then e2e.
- When the task touches Docker or release packaging, also run the documented image builds for API and web, plus `docker compose -f infra/docker-compose.yml config` / `ps` as needed.
- For Serena onboarding or memory updates, finish by confirming `serena memories check` from the project root and listing the updated memories.
- A task is only truly done when the relevant scripts pass, the affected docs are updated, and local-only state has stayed out of versioned files unless explicitly requested.