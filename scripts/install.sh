#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# install: python deps via uv, node deps via pnpm, LLM model if configured

if [ -f apps/api/pyproject.toml ]; then
  uv sync --all-extras --frozen
else
  echo "(install: apps/api/pyproject.toml not present yet — skipping uv sync)"
fi

if [ -f pnpm-workspace.yaml ] || [ -f apps/web/package.json ]; then
  pnpm install --frozen-lockfile
else
  echo "(install: no pnpm workspace yet — skipping pnpm install)"
fi

# Optional GGUF model download (driven by env in .env, not enforced here)
if [ -n "${LLM_MODEL_PATH:-}" ] && [ ! -f "$LLM_MODEL_PATH" ]; then
  echo "(install: LLM_MODEL_PATH set but file missing; download GGUF per EP-001 / DECISIONS.md ADR-004)"
fi

echo "install: ok"
