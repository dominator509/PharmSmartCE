#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Secret scan and basic hygiene.

scan_tracked_secret() {
  label="$1"
  pattern="$2"
  if git grep -I -n -E "$pattern" -- . >/dev/null 2>&1; then
    echo "ERROR: tracked file appears to contain ${label}." >&2
    git grep -I -n -E "$pattern" -- . >&2 || true
    exit 1
  fi
}

if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-banner --redact
else
  echo "(security check: gitleaks not installed - running repo-local fallback patterns)"
  scan_tracked_secret "an OpenAI-style secret" "sk-[A-Za-z0-9_-]{20,}"
  scan_tracked_secret "a GitHub-style token" "(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"
  scan_tracked_secret "an AWS access key" "AKIA[0-9A-Z]{16}"
  scan_tracked_secret "a Google API key" "AIza[0-9A-Za-z_-]{35}"
  scan_tracked_secret "a Slack token" "xox[baprs]-[A-Za-z0-9-]{10,}"
  scan_tracked_secret "a private key block" "-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"
fi

# No committed .env file
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERROR: .env is tracked in git. Remove and add to .gitignore." >&2
  exit 1
fi

echo "security check: ok"
