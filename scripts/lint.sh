#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
export TMPDIR="${TMPDIR:-$PWD/.tools/tmp}"
mkdir -p "$UV_CACHE_DIR" "$TMP" "$TMPDIR"

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
