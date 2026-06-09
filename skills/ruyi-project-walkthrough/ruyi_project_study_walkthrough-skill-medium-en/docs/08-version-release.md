# Version Management & Release

The project maintains version consistency across six locations using an automated release script. This chapter explains the synchronization system and the release workflow.

## The Six-Location Problem

Every version bump must update six files:

```text
// Simplified from: CLAUDE.md:9-18
| # | File | Location | Purpose |
|---|------|----------|---------|
| 1 | skills/project-walkthrough/SKILL.md | frontmatter `version: "X.Y.Z"` | **Single source of truth** |
| 2 | skills/project-walkthrough/SKILL.md | `--version` text (2 occurrences) | User-visible version |
| 3 | .claude-plugin/plugin.json | `"version": "X.Y.Z"` | Plugin metadata |
| 4 | .claude-plugin/marketplace.json | `"version": "X.Y.Z"` | Marketplace registration |
| 5 | README.md | Badge URL | Visual version indicator |
| 6 | CHANGELOG.md | Version heading | Change history |
```

Manual editing of any location except #1 is forbidden. The `release.sh` script handles synchronization.

## release.sh

The 166-line script automates the full release workflow:

```text
// Simplified from: scripts/release.sh:1-13
#!/usr/bin/env bash
# release.sh — Automate version release workflow
#
# Usage:
#   ./scripts/release.sh 1.3.0              # Full release
#   ./scripts/release.sh 1.3.0 --bump-only  # Only bump version files
#   ./scripts/release.sh 1.3.0 --dry-run    # Validate only
```

### Version Bump (6 locations)

The script reads the current version from SKILL.md frontmatter and updates all six locations:

```bash
// Simplified from: scripts/release.sh:57-104
# Read current version from SKILL.md frontmatter
CURRENT_VERSION=$(grep '^version:' skills/project-walkthrough/SKILL.md | head -1 | sed 's/version: *"//;s/"//')

# 1. SKILL.md frontmatter
sed -i.bak "s/^version: \"${CURRENT_VERSION}\"/version: \"${VERSION}\"/" skills/project-walkthrough/SKILL.md

# 2. SKILL.md --version text (all occurrences)
sed -i.bak "s/project-walkthrough v${CURRENT_VERSION}/project-walkthrough v${VERSION}/g" skills/project-walkthrough/SKILL.md
sed -i.bak "s/Project Walkthrough v${CURRENT_VERSION}/Project Walkthrough v${VERSION}/g" skills/project-walkthrough/SKILL.md

# 3. plugin.json
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" .claude-plugin/plugin.json

# 4. marketplace.json
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" .claude-plugin/marketplace.json

# 5. README badge
sed -i.bak "s/badge\/version-[^-]*-/badge\/version-${VERSION}-/" README.md

# 6. CHANGELOG header
TODAY=$(date +%Y-%m-%d)
sed -i.bak "s/## \[Unreleased\]/## [$VERSION] - $TODAY/" CHANGELOG.md
```

### Validation Guards

The script validates several preconditions before proceeding:

```bash
// Simplified from: scripts/release.sh:28-50
# Version format validation
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: Version must be semver (e.g. 1.3.0), got: $VERSION" >&2
    exit 1
fi

# Branch check
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "develop" ]; then
    echo "ERROR: Must be on develop branch" >&2
    exit 1
fi

# Clean tree check
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working tree not clean" >&2
    exit 1
fi
```

### Full Release Flow

When run without `--bump-only`, the script executes the complete release:

1. Run CI checks (`make ci`)
2. Bump version in all 6 locations
3. Commit version bump
4. Push to develop
5. Create PR to master via `gh pr create`
6. Wait for CI to pass (up to 120 seconds)
7. Merge PR via `gh pr merge`
8. Fetch master, tag with version
9. Push tag
10. Sync develop with master

```bash
// Simplified from: scripts/release.sh:115-165
echo "==> Pushing to develop..."
git push origin develop

echo "==> Creating PR..."
PR_URL=$(gh pr create --base master --head develop --title "chore: release v$VERSION" ...)

echo "==> Waiting for CI..."
MAX_WAIT=120
while [ $ELAPSED -lt $MAX_WAIT ]; do
    CHECKS=$(gh pr checks "$PR_NUM" 2>&1 || true)
    if echo "$CHECKS" | grep -q "pass"; then break; fi
    sleep 10
done

echo "==> Merging PR..."
gh pr merge "$PR_NUM" --merge --delete-branch

echo "==> Tagging v$VERSION..."
git tag -a "v$VERSION" "$MASTER_SHA" -m "v$VERSION"
git push origin "v$VERSION"
```

## Makefile Targets

The Makefile provides convenient shortcuts:

```makefile
// Simplified from: Makefile:1-30
test:       python -m pytest tests/ -v --tb=short
test-quick: python -m pytest tests/ -q --tb=line
check:      ./scripts/convert.sh --check
generate:   ./scripts/convert.sh
verify:     python scripts/verify_sources.py --check-all examples/ --strict
ci:         test check
release:    ./scripts/release.sh $(VERSION)
clean:      find . -type d -name __pycache__ -exec rm -rf {} +
```

The `ci` target runs both pytest and convert.sh sync checking — ensuring tests pass AND platform files are current.

## Version Verification Checklist

After any version bump, the CLAUDE.md requires verifying all six locations:

```bash
grep '^version:' skills/project-walkthrough/SKILL.md
grep 'project-walkthrough v' skills/project-walkthrough/SKILL.md
grep '"version"' .claude-plugin/plugin.json
grep '"version"' .claude-plugin/marketplace.json
grep 'badge/version-' README.md
head -5 CHANGELOG.md
```

All six must output the same version number.

[Previous: Multi-Platform Distribution](07-multi-platform-distribution.md) | [Next: Test Suite](09-test-suite.md)
