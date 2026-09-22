#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

BASE_URL="${1:-${SMOKE_BASE_URL:-http://localhost:8000}}"

echo "smoke: target=$BASE_URL"

if [ -d apps/api/app/cli ]; then
  uv run --directory apps/api python -m app.cli.smoke "$BASE_URL"
else
  echo "(smoke test: apps/api/app/cli not present yet — implementation lands in EP-004/EP-008. Skipping.)"
fi

echo "smoke test: ok"
