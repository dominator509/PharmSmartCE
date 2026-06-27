#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Full local validation chain.

scripts/preflight.sh
scripts/lint.sh
scripts/format-check.sh
scripts/typecheck.sh
scripts/test-unit.sh
scripts/test-integration.sh
scripts/test-e2e.sh
scripts/build.sh
scripts/security-check.sh
scripts/dependency-audit.sh

echo "verify: ok"
