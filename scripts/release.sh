#!/usr/bin/env bash
# release.sh — Bump collection version and sync to all brand remotes
#
# Usage:
#   ./scripts/release.sh patch    # 0.1.0 → 0.1.1
#   ./scripts/release.sh minor    # 0.1.0 → 0.2.0
#   ./scripts/release.sh major    # 0.1.0 → 1.0.0

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MARKETPLACE=".claude-plugin/marketplace.json"
CHANGELOG="CHANGELOG.md"

# Current version
CURRENT=$(python3 -c "import json; print(json.load(open('$MARKETPLACE'))['version'])")

# Calculate next version
BUMP="${1:-patch}"
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP" in
    patch) PATCH=$((PATCH + 1)) ;;
    minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
    major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
    *) echo "Usage: $0 [patch|minor|major]"; exit 1 ;;
esac

NEXT="${MAJOR}.${MINOR}.${PATCH}"

echo "Bumping $CURRENT → $NEXT"

# Update marketplace.json version
perl -pi -e "s/\"version\": \"$CURRENT\"/\"version\": \"$NEXT\"/" "$MARKETPLACE"

# Update CHANGELOG.md
if [ -f "$CHANGELOG" ]; then
    perl -pi -e "s/## \\[$CURRENT\\]/## [$NEXT] - $(date +%Y-%m-%d)/" "$CHANGELOG"
fi

# Update README badges
perl -pi -e "s/version-$CURRENT/version-$NEXT/g" README.md README.en.md 2>/dev/null || true

git add -A
git commit -m "release: v$NEXT"

# Tag
git tag "v$NEXT" -m "v$NEXT"

# Push to all remotes
bash scripts/sync-all.sh

echo "Released v$NEXT"
