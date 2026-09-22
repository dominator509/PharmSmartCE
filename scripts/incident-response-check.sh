#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

for f in SUPPORT.md OPERATIONS.md ROLLBACK.md .agent/checklists/incident-response.md PRODUCTION_EVIDENCE.md; do
  if [ ! -f "$f" ]; then
    echo "ERROR: required file missing: $f" >&2
    exit 1
  fi
done

for needle in \
  "Use \`.agent/checklists/incident-response.md\` as the tabletop checklist." \
  "Use \`OPERATIONS.md\` for severity, escalation, and rollback paths." \
  "Use \`ROLLBACK.md\` when a release needs to be reversed or forward-fixed." \
  "Capture tabletop exercises and follow-up notes in \`PRODUCTION_EVIDENCE.md\`."; do
  if ! grep -Fq "$needle" SUPPORT.md; then
    echo "ERROR: SUPPORT.md missing support routing text: $needle" >&2
    exit 1
  fi
done

for needle in \
  "Detect" \
  "Triage" \
  "Page" \
  "Notify" \
  "Mitigate" \
  "Communicate" \
  "Resolve" \
  "Verify" \
  "Document" \
  "Follow up" \
  "Archive evidence"; do
  if ! grep -Fq "$needle" .agent/checklists/incident-response.md; then
    echo "ERROR: incident-response checklist missing step: $needle" >&2
    exit 1
  fi
done

if ! grep -q "^## Support / Ops$" PRODUCTION_EVIDENCE.md; then
  echo "ERROR: PRODUCTION_EVIDENCE.md missing Support / Ops section" >&2
  exit 1
fi

echo "incident response docs: ok"
