#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
export TMPDIR="${TMPDIR:-$PWD/.tools/tmp}"
mkdir -p "$PWD/.tools"
PYTEST_BASETEMP="${PYTEST_BASETEMP:-$(mktemp -d "$PWD/.tools/pytest.XXXXXX")}"
mkdir -p "$UV_CACHE_DIR" "$TMP" "$TMPDIR"

if [ -d apps/api/tests/integration ]; then
  uv run --directory apps/api pytest --basetemp="$PYTEST_BASETEMP" tests/integration -q
else
  echo "(integration tests: apps/api/tests/integration not present yet - skipping)"
fi

echo "integration tests: ok"
