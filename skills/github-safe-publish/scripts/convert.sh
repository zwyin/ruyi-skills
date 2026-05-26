#!/usr/bin/env bash
# convert.sh — Convert SKILL.md to platform-specific formats
#
# Usage:
#   ./scripts/convert.sh --cursor     # Generate .cursor/rules/*.mdc
#   ./scripts/convert.sh --windsurf   # Generate .windsurfrules
#   ./scripts/convert.sh --opencode   # Generate AGENTS.md
#   ./scripts/convert.sh --all        # Generate all formats
#   ./scripts/convert.sh --list       # List supported platforms

set -euo pipefail
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_MD="$ROOT/skills/github-safe-publish/SKILL.md"
OUT_DIR="$ROOT/dist"

# Extract SKILL.md body (everything after YAML frontmatter)
_skill_body() {
    # Find the end of frontmatter (second ---) and print everything after
    awk '/^---/{n++; next} n>=2' "$SKILL_MD"
}

# Extract version from frontmatter
_skill_version() {
    grep '^version:' "$SKILL_MD" | head -1 | sed 's/version: *//;s/"//g'
}

# Extract description from frontmatter (first line only)
_skill_description() {
    awk '/^description:/{found=1; next} found && /^\s+\|/{gsub(/^[ \t]+/, ""); print; exit} found && !/^\s+\|/{exit}' "$SKILL_MD"
}

# --- Cursor ---
_convert_cursor() {
    local cursor_dir="$OUT_DIR/cursor/.cursor/rules"
    mkdir -p "$cursor_dir"
    rm -f "$cursor_dir"/*.mdc

    local version
    version=$(_skill_version)

    local body
    body=$(_skill_body)
    local total_lines
    total_lines=$(echo "$body" | wc -l | tr -d ' ')

    # 1. Overview file: 参数 + 前提 (everything before Step 1)
    local step1_line
    step1_line=$(echo "$body" | grep -n '^## Step 1' | head -1 | cut -d: -f1 || true)
    if [ -n "$step1_line" ] && [ "$step1_line" -gt 1 ]; then
        cat > "$cursor_dir/github-safe-publish-overview.mdc" <<HEREDOC
---
description: GitHub Safe Publish overview, parameters, and prerequisites (v${version})
globs:
alwaysApply: false
---

$(echo "$body" | head -n $((step1_line - 1)))
HEREDOC
    fi

    # 2. Per-step files (Steps 1-6)
    local prev_line=$step1_line
    for step in 1 2 3 4 5 6; do
        local next_step=$((step + 1))
        local next_line
        next_line=$(echo "$body" | grep -n "^## Step ${next_step}" | head -1 | cut -d: -f1 || true)
        if [ -z "$next_line" ]; then
            next_line=$(echo "$body" | grep -n '^## 可选模块' | head -1 | cut -d: -f1 || true)
        fi
        if [ -z "$next_line" ]; then
            next_line=$((total_lines + 1))
        fi

        local step_title
        step_title=$(echo "$body" | sed -n "${prev_line}p" | sed 's/^## //')

        cat > "$cursor_dir/github-safe-publish-step${step}.mdc" <<HEREDOC
---
description: ${step_title} (v${version})
globs:
alwaysApply: false
---

$(echo "$body" | sed -n "${prev_line},$((next_line - 1))p")
HEREDOC

        prev_line=$next_line
    done

    # 3. Optional modules file
    local modules_line
    modules_line=$(echo "$body" | grep -n '^## 可选模块' | head -1 | cut -d: -f1 || true)
    if [ -n "$modules_line" ]; then
        cat > "$cursor_dir/github-safe-publish-modules.mdc" <<HEREDOC
---
description: Optional --seo and --ci modules (v${version})
globs:
alwaysApply: false
---

$(echo "$body" | tail -n +"$modules_line")
HEREDOC
    fi

    echo "Cursor: $cursor_dir/"
    wc -l "$cursor_dir"/*.mdc
}

# --- Windsurf ---
_convert_windsurf() {
    mkdir -p "$OUT_DIR/windsurf"

    cat > "$OUT_DIR/windsurf/.windsurfrules" <<HEREDOC
# GitHub Safe Publish ($(date +%Y-%m-%d))
# Generated from skills/github-safe-publish/SKILL.md v$(_skill_version)
# Manual invokation: ask the AI to "publish to github" or "github safe publish"

$(_skill_body)
HEREDOC

    echo "Windsurf: $OUT_DIR/windsurf/.windsurfrules"
}

# --- OpenCode ---
_convert_opencode() {
    mkdir -p "$OUT_DIR/opencode"

    cat > "$OUT_DIR/opencode/AGENTS.md" <<HEREDOC
# GitHub Safe Publish ($(date +%Y-%m-%d))
# Generated from skills/github-safe-publish/SKILL.md v$(_skill_version)

$(_skill_body)
HEREDOC

    echo "OpenCode: $OUT_DIR/opencode/AGENTS.md"
}

# --- Main ---
case "${1:-}" in
    --cursor)
        _convert_cursor
        ;;
    --windsurf)
        _convert_windsurf
        ;;
    --opencode)
        _convert_opencode
        ;;
    --all)
        _convert_cursor
        _convert_windsurf
        _convert_opencode
        ;;
    --list)
        echo "Supported platforms:"
        echo "  --cursor    .cursor/rules/*.mdc (YAML frontmatter + markdown)"
        echo "  --windsurf  .windsurfrules (markdown)"
        echo "  --opencode  AGENTS.md (markdown)"
        echo "  --all       Generate all formats"
        ;;
    *)
        echo "Usage: $0 --cursor|--windsurf|--opencode|--all|--list"
        exit 1
        ;;
esac
