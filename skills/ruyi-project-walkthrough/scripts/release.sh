#!/usr/bin/env bash
# release.sh — Automate version release workflow
#
# Usage:
#   ./scripts/release.sh 1.3.0              # Full release (bump + PR + merge + tag)
#   ./scripts/release.sh 1.3.0 --bump-only  # Only bump version files, no PR/tag
#   ./scripts/release.sh 1.3.0 --dry-run    # Validate only, no side effects
#
# Prerequisites:
#   - On develop branch, clean working tree
#   - gh CLI authenticated
#   - make ci passes

set -euo pipefail

VERSION="${1:?Usage: $0 <version> [--bump-only] [--dry-run]}"
MODE="${2:-}"

DRY_RUN=false
BUMP_ONLY=false
if [ "$MODE" = "--dry-run" ]; then DRY_RUN=true; fi
if [ "$MODE" = "--bump-only" ]; then BUMP_ONLY=true; fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: Version must be semver (e.g. 1.3.0), got: $VERSION" >&2
    exit 1
fi

if $DRY_RUN; then
    echo "==> Dry run: validation passed. Exiting."
    exit 0
fi

# Check we're on develop
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "develop" ]; then
    echo "ERROR: Must be on develop branch, currently on: $BRANCH" >&2
    exit 1
fi

# Check clean tree
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working tree not clean. Commit or stash changes first." >&2
    git status -s
    exit 1
fi

echo "==> Running CI checks..."
make ci

echo "==> Bumping version to $VERSION..."

# Read current version from SKILL.md frontmatter (single source of truth)
CURRENT_VERSION=$(grep '^version:' skills/project-walkthrough/SKILL.md | head -1 | sed 's/version: * "//;s/"//')
if [ -z "$CURRENT_VERSION" ]; then
    echo "ERROR: Cannot read version from skills/project-walkthrough/SKILL.md frontmatter" >&2
    exit 1
fi
echo "    Current version: $CURRENT_VERSION → $VERSION"

# 1. Update SKILL.md frontmatter
sed -i.bak "s/^version: \"${CURRENT_VERSION}\"/version: \"${VERSION}\"/" skills/project-walkthrough/SKILL.md
rm -f skills/project-walkthrough/SKILL.md.bak

# 2. Update SKILL.md --version output text (all version references)
sed -i.bak "s/project-walkthrough v${CURRENT_VERSION}/project-walkthrough v${VERSION}/g" skills/project-walkthrough/SKILL.md
sed -i.bak "s/Project Walkthrough v${CURRENT_VERSION}/Project Walkthrough v${VERSION}/g" skills/project-walkthrough/SKILL.md
rm -f skills/project-walkthrough/SKILL.md.bak

# 3. Update plugin.json
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" .claude-plugin/plugin.json
rm -f .claude-plugin/plugin.json.bak

# 4. Update marketplace.json
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" .claude-plugin/marketplace.json
rm -f .claude-plugin/marketplace.json.bak

# 5. Update README version badge
sed -i.bak "s/badge\/version-[^-]*-/badge\/version-${VERSION}-/" README.md
rm -f README.md.bak

# Update CHANGELOG [Unreleased] → [VERSION]
if grep -q "## \[Unreleased\]" CHANGELOG.md; then
    TODAY=$(date +%Y-%m-%d)
    sed -i.bak "s/## \[Unreleased\]/## [$VERSION] - $TODAY/" CHANGELOG.md
    rm -f CHANGELOG.md.bak
else
    # Prepend new version entry after header
    TODAY=$(date +%Y-%m-%d)
    sed -i.bak "/The format is based on/a\\
\\
## [$VERSION] - $TODAY\\
\\
### Added\\
\\
### Changed\\
\\
### Fixed" CHANGELOG.md
    rm -f CHANGELOG.md.bak
fi

echo "==> Committing version bump..."
git add skills/project-walkthrough/SKILL.md .claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md README.md
git commit -m "chore: bump version to $VERSION"

if $BUMP_ONLY; then
    echo "Bump-only mode. Files updated, commit created."
    echo "Push with: git push origin develop"
    exit 0
fi

echo "==> Pushing to develop..."
git push origin develop

echo "==> Creating PR..."
PR_URL=$(gh pr create --base master --head develop \
    --title "chore: release v$VERSION" \
    --body "Automated release v$VERSION" 2>&1)
PR_NUM=$(echo "$PR_URL" | grep -o '[0-9]*$')
echo "    PR #$PR_NUM: $PR_URL"

echo "==> Waiting for CI..."
MAX_WAIT=120
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep 10
    ELAPSED=$((ELAPSED + 10))
    CHECKS=$(gh pr checks "$PR_NUM" 2>&1 || true)
    if echo "$CHECKS" | grep -q "fail"; then
        echo "ERROR: CI failed!" >&2
        echo "$CHECKS" >&2
        exit 1
    fi
    if echo "$CHECKS" | grep -q "pass" && ! echo "$CHECKS" | grep -q "pending"; then
        echo "    CI passed!"
        break
    fi
    echo "    Waiting... ($ELAPSED/${MAX_WAIT}s)"
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "ERROR: CI timed out after ${MAX_WAIT}s" >&2
    exit 1
fi

echo "==> Merging PR..."
gh pr merge "$PR_NUM" --merge --delete-branch

echo "==> Tagging v$VERSION..."
git fetch origin master
MASTER_SHA=$(git rev-parse origin/master)
git tag -a "v$VERSION" "$MASTER_SHA" -m "v$VERSION"
git push origin "v$VERSION"

echo "==> Syncing develop..."
git checkout develop
git merge master --ff-only

echo ""
echo "✓ Released v$VERSION!"
echo "  Tag: v$VERSION"
echo "  PR:  #$PR_NUM"
