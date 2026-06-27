#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -d apps/api/tests/integration ]; then
  uv run --directory apps/api pytest tests/integration -q
else
  echo "(integration tests: apps/api/tests/integration not present yet — skipping)"
fi

echo "integration tests: ok"
