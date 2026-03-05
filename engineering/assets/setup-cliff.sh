#!/usr/bin/env bash
# setup-cliff.sh — install git-cliff config into a project
# Usage: bash skills/engineering/assets/setup-cliff.sh [project-dir]
#   project-dir defaults to current working directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/cliff.toml.template"
TARGET_DIR="${1:-$(pwd)}"
TARGET="$TARGET_DIR/cliff.toml"

if [ ! -f "$TEMPLATE" ]; then
  echo "✗ Template not found: $TEMPLATE" >&2; exit 1
fi

cp "$TEMPLATE" "$TARGET"
echo "✓ cliff.toml written to $TARGET"

# Optionally patch package.json if it exists
PKG="$TARGET_DIR/package.json"
if [ -f "$PKG" ]; then
  if command -v jq &>/dev/null; then
    if ! jq -e '.scripts.changelog' "$PKG" &>/dev/null; then
      tmp=$(mktemp)
      jq '.scripts.changelog = "git cliff -o CHANGELOG.md"' "$PKG" > "$tmp" && mv "$tmp" "$PKG"
      echo "✓ Added 'changelog' script to package.json"
    else
      echo "  (package.json already has a 'changelog' script — skipped)"
    fi
  else
    echo "  (jq not found — add manually to package.json scripts: \"changelog\": \"git cliff -o CHANGELOG.md\")"
  fi
fi

echo ""
echo "Next: git cliff -o CHANGELOG.md"
