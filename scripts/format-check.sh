#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
mkdir -p "$UV_CACHE_DIR" "$TMP"

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
