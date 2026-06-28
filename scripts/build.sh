#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
export DOCKER_CONFIG="${DOCKER_CONFIG:-$PWD/.tools/docker-config}"
mkdir -p "$TMP" "$DOCKER_CONFIG"

DOCKER_BIN="${DOCKER_BIN:-docker}"
if command -v docker.exe >/dev/null 2>&1; then
  DOCKER_BIN=docker.exe
fi

if [ -f apps/api/Dockerfile ]; then
  "$DOCKER_BIN" build -f apps/api/Dockerfile -t pharmsmartce-api:dev .
else
  echo "(build: apps/api/Dockerfile not present yet - skipping API image build)"
fi

if [ -f apps/web/package.json ]; then
  if command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c pnpm --filter web build
  else
    pnpm --filter web build
  fi
else
  echo "(build: apps/web not present yet - skipping web build)"
fi

echo "build: ok"
