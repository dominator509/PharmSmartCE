#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -f apps/api/Dockerfile ]; then
  docker build -f apps/api/Dockerfile -t pharmsmartce-api:dev .
else
  echo "(build: apps/api/Dockerfile not present yet — skipping API image build)"
fi

if [ -f apps/web/package.json ]; then
  pnpm --filter web build
else
  echo "(build: apps/web not present yet — skipping web build)"
fi

echo "build: ok"
