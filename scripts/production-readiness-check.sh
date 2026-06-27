#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Production-readiness gate.
# 1. Run full verify chain.
# 2. Check pack file presence.
# 3. Check for unresolved TODO/FIXME in core docs.
# 4. Optional Alembic head check.

scripts/verify.sh

err=0
warn=0

# Required pack files (Pack 1 contents)
for f in PROJECT_BRIEF.md AGENTS.md COMMANDS.md ARCHITECTURE.md ROADMAP.md \
         DECISIONS.md TESTING.md SECURITY.md ENVIRONMENT.md DEPLOYMENT.md \
         OPERATIONS.md OBSERVABILITY.md PRODUCTION_READINESS.md RELEASE.md \
         ROLLBACK.md CONTRIBUTING.md ASSUMPTIONS.md \
         .agent/PLANS.md .agent/EXECUTION_RULES.md; do
  if [ ! -f "$f" ]; then
    echo "ERROR: required file missing: $f" >&2
    err=1
  fi
done

# Required specs
for n in 000-product-scope 001-core-domain 002-data-model 003-api-contracts \
         004-ui-ux-behavior 005-auth-and-permissions 006-error-handling \
         007-observability 008-production-readiness; do
  if [ ! -f ".agent/specs/SPEC-$n.md" ]; then
    echo "ERROR: spec missing: .agent/specs/SPEC-$n.md" >&2
    err=1
  fi
done

# Required ExecPlans (these arrive in Pack 2)
for n in 000-repository-discovery 001-foundation 002-core-domain \
         003-data-and-persistence 004-api-or-service-layer \
         005-user-interface-or-client 006-auth-security-and-permissions \
         007-testing-hardening 008-observability-and-operations \
         009-deployment-and-release 010-production-readiness; do
  if [ ! -f ".agent/execplans/EP-$n.md" ]; then
    echo "WARNING: ExecPlan missing: .agent/execplans/EP-$n.md (expected after Pack 2 applied)" >&2
    warn=1
  fi
done

# Required checklists (Pack 2)
for f in agent-readiness preflight implementation validation final-review \
         production-readiness release rollback incident-response; do
  if [ ! -f ".agent/checklists/$f.md" ]; then
    echo "WARNING: checklist missing: .agent/checklists/$f.md (expected after Pack 2 applied)" >&2
    warn=1
  fi
done

# No unresolved TODO/FIXME in core docs
for f in PROJECT_BRIEF.md AGENTS.md COMMANDS.md ARCHITECTURE.md ROADMAP.md \
         DECISIONS.md PRODUCTION_READINESS.md; do
  if [ -f "$f" ] && grep -nE "TODO|FIXME" "$f" >/dev/null 2>&1; then
    echo "WARNING: unresolved TODO/FIXME in $f" >&2
    warn=1
  fi
done

# Optional Alembic head check
if [ -d apps/api/alembic ]; then
  if command -v alembic >/dev/null 2>&1 || [ -f apps/api/pyproject.toml ]; then
    echo "(prod readiness: Alembic present — verify head matches deployed env manually per OPERATIONS.md)"
  fi
fi

if [ "$err" -ne 0 ]; then
  echo "production readiness: FAILED" >&2
  exit 1
fi

if [ "$warn" -ne 0 ]; then
  echo "production readiness: ok (with warnings — see above)"
else
  echo "production readiness: ok"
fi
