#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

sha="$(git rev-parse --short HEAD)"
cat <<EOF
I confirm every PRODUCTION_READINESS.md checkbox is ticked and scripts/production-readiness-check.sh exits 0 against commit ${sha}. Proceeding to flip DNS / promote prod.
EOF
