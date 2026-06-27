#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
mkdir -p "$UV_CACHE_DIR" "$TMP"

if [ -d apps/api/tests/unit ]; then
  uv run --directory apps/api pytest tests/unit -q
else
  echo "(unit tests: apps/api/tests/unit not present yet — skipping)"
fi

if [ -f apps/web/package.json ] && grep -q '"test:unit"' apps/web/package.json 2>/dev/null; then
  pnpm --filter web test:unit
else
  echo "(unit tests: apps/web test:unit not present yet — skipping)"
fi

echo "unit tests: ok"
