#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -f apps/api/pyproject.toml ]; then
  uv run --directory apps/api ruff format --check .
else
  echo "(format check: apps/api not yet bootstrapped — skipping ruff format)"
fi

if [ -f apps/web/package.json ]; then
  pnpm --filter web format:check
else
  echo "(format check: apps/web not yet bootstrapped — skipping prettier)"
fi

echo "format check: ok"
