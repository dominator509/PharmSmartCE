#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -f apps/api/pyproject.toml ]; then
  uv run --directory apps/api ruff check .
else
  echo "(lint: apps/api not yet bootstrapped — skipping ruff)"
fi

if [ -f apps/web/package.json ]; then
  pnpm --filter web lint
else
  echo "(lint: apps/web not yet bootstrapped — skipping eslint)"
fi

echo "lint: ok"
