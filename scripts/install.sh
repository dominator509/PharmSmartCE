#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$PWD/.tools/ms-playwright}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
mkdir -p "$UV_CACHE_DIR" "$PLAYWRIGHT_BROWSERS_PATH" "$TMP"

# install: python deps via uv, node deps via pnpm, LLM model if configured

if [ -f apps/api/pyproject.toml ]; then
  uv sync --directory apps/api --all-extras --frozen
else
  echo "(install: apps/api/pyproject.toml not present yet — skipping uv sync)"
fi

if [ -f pnpm-workspace.yaml ] || [ -f apps/web/package.json ]; then
  pnpm install --frozen-lockfile
  if [ -f apps/web/package.json ] && grep -q '"test:e2e"' apps/web/package.json 2>/dev/null; then
    pnpm --filter web exec playwright install chromium
  fi
else
  echo "(install: no pnpm workspace yet — skipping pnpm install)"
fi

# Optional GGUF model download (driven by env in .env, not enforced here)
if [ -n "${LLM_MODEL_PATH:-}" ] && [ ! -f "$LLM_MODEL_PATH" ]; then
  echo "(install: LLM_MODEL_PATH set but file missing; download GGUF per EP-001 / DECISIONS.md ADR-004)"
fi

echo "install: ok"
