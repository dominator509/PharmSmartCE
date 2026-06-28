#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
export TMPDIR="${TMPDIR:-$PWD/.tools/tmp}"
PYTEST_BASETEMP="$PWD/.tools/pytest"
mkdir -p "$UV_CACHE_DIR" "$TMP" "$TMPDIR" "$PYTEST_BASETEMP"

if [ -d apps/api/tests/unit ]; then
  uv run --directory apps/api pytest --basetemp="$PYTEST_BASETEMP" tests/unit -q
else
  echo "(unit tests: apps/api/tests/unit not present yet - skipping)"
fi

if [ -f apps/web/package.json ] && grep -q '"test:unit"' apps/web/package.json 2>/dev/null; then
  pnpm --filter web test:unit
else
  echo "(unit tests: apps/web test:unit not present yet - skipping)"
fi

echo "unit tests: ok"
