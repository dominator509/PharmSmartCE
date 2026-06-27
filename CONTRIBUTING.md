# CONTRIBUTING.md

For human contributors and coding agents. Agents must ALSO follow `AGENTS.md`.

## Setup
```sh
git clone <repo>
cd PharmSmartCE
cp .env.example .env
scripts/install.sh
scripts/preflight.sh
docker compose -f infra/docker-compose.yml up -d db redis minio
uv run --directory apps/api alembic upgrade head
```

## Branch Naming
| Type | Pattern |
|---|---|
| Feature | `feat/<slug>` |
| Bug fix | `fix/<slug>` |
| Chore / refactor | `chore/<slug>` |
| Agent ExecPlan | `ep/EP-NNN-<slug>` |
| Hotfix off release tag | `hotfix/<slug>` |

## Coding Standards
- Python: `ruff` (lint + format) configured in `apps/api/pyproject.toml`;
  `mypy` strict-ish (`disallow_untyped_defs`).
- TypeScript: `eslint` + `prettier`; `tsc --noEmit` clean.
- No `print()` in non-CLI code (Architectural Invariant I5).
- No `os.environ` outside `apps/api/app/config.py` (I4).
- Public functions in services and adapters have docstrings.

## Test Requirements
- Every PR with new behavior MUST include a test that fails without the change.
- `scripts/verify.sh` green locally before opening PR.

## Documentation Requirements
- Update the relevant spec when behavior changes.
- Update `COMMANDS.md` when commands change.
- Update `ARCHITECTURE.md` when boundaries change.
- Add an ADR for non-trivial choices.

## Commit Guidance — Conventional Commits
```
feat(generation): add per-session deterministic seeding for retrieval
fix(auth): reject revoked refresh token reuse across the entire chain
chore(deps): bump fastapi to 0.115.5
docs(architecture): clarify ports/adapters boundary
```

## Pull Request Checklist
- [ ] Active ExecPlan referenced (`Implements EP-004 milestone 3`).
- [ ] Scope matches the ExecPlan's `Files to Change`.
- [ ] `scripts/verify.sh` green locally.
- [ ] Tests added/updated.
- [ ] Docs updated.
- [ ] ADR added if non-trivial.
- [ ] `CHANGELOG.md [Unreleased]` updated.

## Code Review Checklist
- [ ] Architectural invariants respected.
- [ ] No LLM calls outside `grounded_llm.py`.
- [ ] No env reads outside `config.py`.
- [ ] No raw SQL outside `repositories/`.
- [ ] No `print()` in service/adapter code.
- [ ] Citation invariant enforced where applicable.
- [ ] No secrets in code or fixtures.
- [ ] No new dependency without ADR.

## Agent-Specific Contribution Rules
- Read `AGENTS.md` and the active ExecPlan before editing any file.
- Do not implement from `ROADMAP.md`.
- Continue autonomously; stop only on STOP conditions.
- Update the ExecPlan after each milestone.
- Provide the final report described in `AGENTS.md` §15.
