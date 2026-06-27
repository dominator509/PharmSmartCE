#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -f apps/web/package.json ] && grep -q '"test:e2e"' apps/web/package.json 2>/dev/null; then
  pnpm --filter web test:e2e
else
  echo "(e2e tests: apps/web test:e2e not present yet — skipping)"
fi

echo "e2e tests: ok"
