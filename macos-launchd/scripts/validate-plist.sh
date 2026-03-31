#!/usr/bin/env bash
set -euo pipefail

PLIST="${1:-}"
if [[ -z "$PLIST" ]]; then
  echo "Usage: scripts/validate-plist.sh <path/to/file.plist>" >&2
  exit 1
fi

plutil -lint "$PLIST"
echo "Validation OK: $PLIST"
