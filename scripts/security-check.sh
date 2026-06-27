#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# secret scan and basic hygiene

if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-banner --redact
else
  echo "(security check: gitleaks not installed — recommended; install per SECURITY.md)"
fi

# No committed .env file
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERROR: .env is tracked in git. Remove and add to .gitignore." >&2
  exit 1
fi

# Naive OpenAI key pattern check against tracked files
if git ls-files | xargs -I{} grep -l "sk-[A-Za-z0-9]\{20,\}" {} 2>/dev/null | head -1 | grep -q .; then
  echo "ERROR: tracked file appears to contain an OpenAI-style secret." >&2
  exit 1
fi

echo "security check: ok"
