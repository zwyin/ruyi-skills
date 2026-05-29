#!/usr/bin/env bash
# release.sh — Automate version release workflow
#
# Usage:
#   ./scripts/release.sh 0.5.0              # Full release (bump + commit + tag)
#   ./scripts/release.sh 0.5.0 --bump-only  # Only bump version files, no tag
#   ./scripts/release.sh 0.5.0 --dry-run    # Validate only, no side effects
#
# Version source: skills/ruyi-github-safe-publish/SKILL.md frontmatter (唯一版本源)

set -euo pipefail

VERSION="${1:?Usage: $0 <version> [--bump-only | --dry-run]}"
MODE="${2:-}"

DRY_RUN=false
BUMP_ONLY=false
if [ "$MODE" = "--dry-run" ]; then DRY_RUN=true; fi
if [ "$MODE" = "--bump-only" ]; then BUMP_ONLY=true; fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SKILL_MD="skills/ruyi-github-safe-publish/SKILL.md"
PLUGIN_JSON=".claude-plugin/plugin.json"
MARKETPLACE_JSON=".claude-plugin/marketplace.json"

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: Version must be semver (e.g. 0.5.0), got: $VERSION" >&2
    exit 1
fi

# Read current version from SKILL.md frontmatter (single source of truth)
CURRENT_VERSION=$(grep '^version:' "$SKILL_MD" | head -1 | perl -pe 's/version: *//;s/"//g;s/ //g')
if [ -z "$CURRENT_VERSION" ]; then
    echo "ERROR: Cannot read version from $SKILL_MD frontmatter" >&2
    exit 1
fi

echo "==> Version: $CURRENT_VERSION → $VERSION"

if $DRY_RUN; then
    echo "==> Dry run: validation passed. Exiting."
    exit 0
fi

# Check clean tree
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working tree not clean. Commit or stash changes first." >&2
    git status -s
    exit 1
fi

echo "==> Running tests..."
bash scripts/validate_skill.sh

echo "==> Bumping version to $VERSION..."

# 1. Update SKILL.md frontmatter
perl -pi -e "s/^version: \"\Q$CURRENT_VERSION\E\"/version: \"$VERSION\"/" "$SKILL_MD"

# 2. Update plugin.json
perl -pi -e "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$PLUGIN_JSON"

# 3. Update marketplace.json
perl -pi -e "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$MARKETPLACE_JSON"

# 4. Update README version badge (if exists)
if [ -f README.md ]; then
    perl -pi -e "s/badge\/version-[^-]*-/badge\/version-${VERSION}-/" README.md
fi

# 5. Update CHANGELOG [Unreleased] → [VERSION]
TODAY=$(date +%Y-%m-%d)
if grep -q "## \[Unreleased\]" CHANGELOG.md; then
    perl -pi -e "s/## \\[Unreleased\\]/## [$VERSION] - $TODAY/" CHANGELOG.md
else
    perl -pi -e "if (/The format is based on/) { \$_ .= qq(\n## [$VERSION] - $TODAY\n\n### Added\n\n### Changed\n\n### Fixed\n) }" CHANGELOG.md
fi

echo "==> Committing version bump..."
git add "$SKILL_MD" "$PLUGIN_JSON" "$MARKETPLACE_JSON" CHANGELOG.md
[ -f README.md ] && git add README.md
git commit -m "chore: bump version to $VERSION"

if $BUMP_ONLY; then
    echo "Bump-only mode. Files updated, commit created."
    exit 0
fi

echo "==> Tagging v$VERSION..."
git tag -a "v$VERSION" -m "v$VERSION"

echo ""
echo "✓ Released v$VERSION!"
echo "  Tag: v$VERSION"
BRANCH=$(git branch --show-current)
echo "  Push with: git push origin $BRANCH --tags"
