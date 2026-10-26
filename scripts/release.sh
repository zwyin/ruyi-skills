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

# Guard: CHANGELOG must have an [Unreleased] section before we touch anything.
# Runs BEFORE the marketplace.json edit so a failed release leaves it untouched.
grep -q '^## \[Unreleased\]' "$CHANGELOG" || { echo "ERROR: CHANGELOG.md 缺 ## [Unreleased] 段；先写 Unreleased 再发版"; exit 1; }

# Update marketplace.json version
perl -pi -e "s/\"version\": \"$CURRENT\"/\"version\": \"$NEXT\"/" "$MARKETPLACE"

# Update CHANGELOG.md: rotate [Unreleased] → [$NEXT] and insert a fresh skeleton
python3 scripts/update_changelog.py "$CHANGELOG" "$NEXT"

# Update README badges
perl -pi -e "s/version-$CURRENT/version-$NEXT/g" README.md README.en.md 2>/dev/null || true

git add "$MARKETPLACE" "$CHANGELOG" README.md README.en.md
git commit -m "release: v$NEXT"

# Tag
git tag "v$NEXT" -m "v$NEXT"

# Push to main remote (bypass local HTTPS-intercepting proxy explicitly)
MAIN_REMOTE=$(git remote | grep -v github | head -1 || echo "origin")
git -c http.proxy="" -c https.proxy="" push "$MAIN_REMOTE" main --tags

echo "Released v$NEXT"
echo "To sync brand repos, run: cd brand-sync-tool && bash sync.sh"
