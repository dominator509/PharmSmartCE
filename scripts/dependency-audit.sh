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
  uv run --directory apps/api pip-audit || {
    echo "ERROR: pip-audit found vulnerabilities. Review per SECURITY.md." >&2
    exit 1
  }
else
  echo "(dependency audit: apps/api not yet bootstrapped — skipping pip-audit)"
fi

if [ -f pnpm-workspace.yaml ] || [ -f apps/web/package.json ]; then
  pnpm audit --prod || {
    echo "ERROR: pnpm audit found vulnerabilities. Review per SECURITY.md." >&2
    exit 1
  }
else
  echo "(dependency audit: no pnpm workspace yet — skipping pnpm audit)"
fi

echo "dependency audit: ok"
