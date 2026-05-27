#!/usr/bin/env bash
set -euo pipefail

echo "=== github-safe-publish skill validation ==="
echo ""

SKILL="skills/github-safe-publish/SKILL.md"
version=$(grep '^version:' "$SKILL" | head -1 | awk '{print $2}' | tr -d '"')
echo "Version: $version"
echo ""
if python3 -m pytest tests/ -v --tb=short; then
    echo ""
    echo "2. Checking file structure..."
    RULES="docs/scanning-rules.md"

    for f in "$SKILL" "$RULES" "CLAUDE.md" "LICENSE" "README.md" ".claude-plugin/plugin.json" ".claude-plugin/marketplace.json" "CHANGELOG.md" ".github/workflows/test.yml" "scripts/release.sh" "scripts/convert.sh" "scripts/validate_skill.sh"; do
        if [ -f "$f" ]; then
            echo "   ✓ $f"
        else
            echo "   ✗ $f MISSING"
            exit 1
        fi
    done

    echo ""
    echo "3. Checking SKILL.md version..."
    version=$(grep '^version:' "$SKILL" | head -1 | awk '{print $2}' | tr -d '"')
    if echo "$version" | grep -qE '^\d+\.\d+\.\d+$'; then
        echo "   ✓ version: $version"
    else
        echo "   ✗ Invalid version: $version"
        exit 1
    fi

    echo ""
    echo "4. Checking version sync across files..."
    mismatches=0
    for f in ".claude-plugin/plugin.json" ".claude-plugin/marketplace.json"; do
        fv=$(grep '"version"' "$f" | head -1 | sed 's/.*: "//;s/".*//')
        if [ "$fv" != "$version" ]; then
            echo "   ✗ $f: $fv (expected $version)"
            mismatches=$((mismatches + 1))
        else
            echo "   ✓ $f: $fv"
        fi
    done
    badge_ver=$(grep -o 'version-[0-9.]*' README.md | head -1 | sed 's/version-//')
    if [ "$badge_ver" != "$version" ]; then
        echo "   ✗ README badge: $badge_ver (expected $version)"
        mismatches=$((mismatches + 1))
    else
        echo "   ✓ README badge: $badge_ver"
    fi
    if [ "$mismatches" -gt 0 ]; then
        echo "   ✗ Version mismatches found!"
        exit 1
    fi

    echo ""
    echo "5. Checking convert.sh..."
    bash scripts/convert.sh --cursor > /dev/null 2>&1 && echo "   ✓ --cursor" || { echo "   ✗ --cursor failed"; exit 1; }
    bash scripts/convert.sh --windsurf > /dev/null 2>&1 && echo "   ✓ --windsurf" || { echo "   ✗ --windsurf failed"; exit 1; }
    bash scripts/convert.sh --opencode > /dev/null 2>&1 && echo "   ✓ --opencode" || { echo "   ✗ --opencode failed"; exit 1; }

    echo ""
    echo "=== All validations passed ==="
else
    echo "Tests failed!"
    exit 1
fi
