#!/usr/bin/env bash
# convert.sh — Convert all skill SKILL.md to platform-specific formats
#
# Usage:
#   ./scripts/convert.sh --cursor     # Generate .cursor/rules/*.mdc per skill
#   ./scripts/convert.sh --windsurf   # Generate .windsurfrules per skill
#   ./scripts/convert.sh --opencode   # Generate AGENTS.md per skill
#   ./scripts/convert.sh --all        # Generate all formats
#   ./scripts/convert.sh --check      # Verify all skills are convertible (CI)

set -euo pipefail
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT/dist"
SKILLS_DIR="$ROOT/skills"

# Find SKILL.md — may be at skill_dir/SKILL.md or nested (subtree import)
_find_skill_md() {
    find "$1" -name "SKILL.md" -not -path "*/dist/*" -not -path "*/.opencode/*" 2>/dev/null | head -n 1 || true
}

# Extract SKILL.md body (everything after YAML frontmatter)
_skill_body() {
    awk '/^---/{n++; next} n>=2' "$1"
}

# Extract version from frontmatter
_skill_version() {
    grep '^version:' "$1" | head -n 1 | sed 's/version: *//;s/"//g' || true
}

# Extract name from frontmatter
_skill_name() {
    grep '^name:' "$1" | head -n 1 | sed 's/name: *//;s/"//g' || true
}

# --- Cursor ---
_convert_cursor() {
    local skill_dir="$1"
    local skill_md
    skill_md=$(_find_skill_md "$skill_dir") || { echo "  No SKILL.md in $skill_dir"; return; }
    local name
    name=$(_skill_name "$skill_md")

    local cursor_dir="$OUT_DIR/cursor/.cursor/rules"
    mkdir -p "$cursor_dir"

    local body
    body=$(_skill_body "$skill_md")

    # Split by ## Step headers into separate .mdc files
    local prefix="$name"
    local file_count=0

    # Overview file (everything before first ## Step)
    local overview
    overview=$(echo "$body" | awk '/^## Step/{exit} {print}') || true

    if [ -n "$overview" ]; then
        cat > "$cursor_dir/${prefix}-overview.mdc" <<META
---
name: ${prefix}-overview
description: Overview for ${name} skill
globs:
alwaysApply: false
---

${overview}
META
        file_count=$((file_count + 1))
    fi

    # Each ## Step becomes a separate file
    echo "$body" | awk -v prefix="$prefix" '
        /^## Step/ {
            if (out) close(out)
            n++
            gsub(/[^a-zA-Z0-9]/, "-", $0)
            file = "'"${cursor_dir}"'" "/" prefix "-" tolower($0) ".mdc"
            out = file
            print "---" > out
            print "name: " prefix "-" tolower($0) >> out
            print "description: " $0 >> out
            print "globs:" >> out
            print "alwaysApply: false" >> out
            print "---" >> out
            print "" >> out
            next
        }
        out { print > out }
    ' || true

    wc -l "$cursor_dir"/${prefix}*.mdc 2>/dev/null | tail -n 1 || true
}

# --- Windsurf ---
_convert_windsurf() {
    local skill_dir="$1"
    local skill_md
    skill_md=$(_find_skill_md "$skill_dir") || { echo "  No SKILL.md in $skill_dir"; return; }
    local name
    name=$(_skill_name "$skill_md")

    local ws_dir="$OUT_DIR/windsurf/.windsurfrules"
    mkdir -p "$ws_dir"

    {
        _skill_body "$skill_md"
    } > "$ws_dir/${name}.md"

    wc -l "$ws_dir/${name}.md"
}

# --- OpenCode ---
_convert_opencode() {
    local skill_dir="$1"
    local skill_md
    skill_md=$(_find_skill_md "$skill_dir") || { echo "  No SKILL.md in $skill_dir"; return; }
    local name
    name=$(_skill_name "$skill_md")

    local oc_dir="$OUT_DIR/opencode/.opencode/skills/${name}"
    mkdir -p "$oc_dir"

    cp "$skill_md" "$oc_dir/SKILL.md"

    wc -l "$oc_dir/SKILL.md"
}

# --- Check ---
_do_check() {
    local errors=0
    for skill_dir in "$SKILLS_DIR"/*/; do
        local skill_md
        skill_md=$(_find_skill_md "$skill_dir")
        [ -n "$skill_md" ] || { echo "✗ Missing SKILL.md in $skill_dir"; errors=$((errors + 1)); continue; }
        # Verify frontmatter has required fields
        for field in name version; do
            grep -q "^${field}:" "$skill_md" || { echo "✗ Missing '$field' in $skill_md"; errors=$((errors + 1)); }
        done
        echo "✓ $(basename "$skill_dir")"
    done
    [ "$errors" -eq 0 ] || exit 1
}

# --- Main ---
ACTION="${1:---all}"

case "$ACTION" in
    --cursor)
        for skill_dir in "$SKILLS_DIR"/*/; do
            echo "Cursor: $(basename "$skill_dir")"
            _convert_cursor "$skill_dir"
        done
        ;;
    --windsurf)
        for skill_dir in "$SKILLS_DIR"/*/; do
            echo "Windsurf: $(basename "$skill_dir")"
            _convert_windsurf "$skill_dir"
        done
        ;;
    --opencode)
        for skill_dir in "$SKILLS_DIR"/*/; do
            echo "OpenCode: $(basename "$skill_dir")"
            _convert_opencode "$skill_dir"
        done
        ;;
    --all)
        for skill_dir in "$SKILLS_DIR"/*/; do
            echo "=== $(basename "$skill_dir") ==="
            _convert_cursor "$skill_dir"
            _convert_windsurf "$skill_dir"
            _convert_opencode "$skill_dir"
        done
        ;;
    --check)
        _do_check
        ;;
    *)
        echo "Usage: $0 [--cursor|--windsurf|--opencode|--all|--check]"
        exit 1
        ;;
esac
