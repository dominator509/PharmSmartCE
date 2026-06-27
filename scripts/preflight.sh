#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# preflight: validate repo state and required tooling

err=0

if [ ! -f AGENTS.md ]; then
  echo "ERROR: AGENTS.md missing at repo root." >&2
  err=1
fi
if [ ! -f COMMANDS.md ]; then
  echo "ERROR: COMMANDS.md missing at repo root." >&2
  err=1
fi

for cmd in uv pnpm docker git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: required command '$cmd' not found. Install per ENVIRONMENT.md." >&2
    err=1
  fi
done

if [ "$err" -ne 0 ]; then
  echo "preflight: FAILED" >&2
  exit 1
fi

echo "preflight: ok"
