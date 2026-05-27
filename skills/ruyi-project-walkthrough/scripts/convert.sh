#!/usr/bin/env bash
# convert.sh — Generate platform-specific skill files from canonical SKILL.md
#
# Usage:
#   ./scripts/convert.sh              # Generate all platforms
#   ./scripts/convert.sh cursor       # Generate Cursor only
#   ./scripts/convert.sh windsurf     # Generate Windsurf only
#   ./scripts/convert.sh opencode     # Generate OpenCode only
#   ./scripts/convert.sh --check      # Check if files are in sync
#
# Reads:  skills/project-walkthrough/SKILL.md (canonical source)
# Writes: cursor/project-walkthrough.mdc
#         .windsurf/rules/project-walkthrough.md
#         .opencode/skills/project-walkthrough/SKILL.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL="$ROOT/skills/project-walkthrough/SKILL.md"
MAX_WINDSURF_CHARS=12000

TRIGGER_DESC="Use when the user wants to study, document, understand, or share analysis of a software project/codebase. Triggers on requests like 'walk through this project', 'explain this codebase', 'generate documentation for this project', 'help me understand this code'."

if [ ! -f "$SKILL" ]; then
    echo "ERROR: $SKILL not found" >&2
    exit 1
fi

# Use Python for reliable cross-platform text processing
CONVERT_PY=$(cat <<'PYEOF'
import sys, re

def read_skill(path):
    with open(path) as f:
        text = f.read()
    # Split on --- delimiters: frontmatter ... ---
    parts = re.split(r'^---\s*$', text.strip(), maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        frontmatter = parts[1].strip()
        body = parts[2].strip() + "\n"
    else:
        frontmatter = ""
        body = text
    # Parse frontmatter into dict
    fm = {}
    for line in frontmatter.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body

def gen_cursor(body, trigger_desc):
    return f'---\ndescription: "{trigger_desc}"\nglobs:\nalwaysApply: false\n---\n{body}'

def gen_opencode(body, fm):
    name = fm.get("name", "project-walkthrough")
    desc = fm.get("description", "")
    arg_hint = fm.get("argument-hint", "")
    return f'---\nname: {name}\ndescription: {desc}\nlicense: MIT\ncompatibility: opencode\nargument-hint: {arg_hint}\n---\n{body}'

def gen_windsurf(body, trigger_desc, max_chars):
    """Condense body to fit Windsurf's char limit by removing verbose sections."""
    lines = body.split("\n")
    result = []
    skip_sections = {
        "## Checklist", "## Documentation Standards",
    }
    skip_subsections = {
        "#### Phase 3A: Verify",
        "#### Phase 3B: Write",
        "#### Phase 3C: Validate",
        "#### If `all` depth",
        "#### Accuracy Rules",
    }

    def section_level(line):
        m = re.match(r'^(#{1,4}) ', line)
        return len(m.group(1)) if m else 0

    skip_until_level = 0
    in_skip = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if in_skip:
            lvl = section_level(line)
            if lvl > 0 and lvl <= skip_until_level:
                in_skip = False
                # Don't skip this line, fall through
            else:
                i += 1
                continue

        # Check skip sections
        stripped = line.strip()
        for s in skip_sections:
            if stripped.startswith(s):
                skip_until_level = section_level(line)
                in_skip = True
                break

        if in_skip:
            i += 1
            continue

        # Check skip subsections
        for s in skip_subsections:
            if stripped.startswith(s):
                skip_until_level = section_level(line)
                in_skip = True
                break

        if in_skip:
            i += 1
            continue

        result.append(line)
        i += 1

    condensed = "\n".join(result).strip() + "\n"

    # Check if still over limit
    if len(condensed) > max_chars:
        # Further trim: remove examples section
        lines2 = condensed.split("\n")
        result2 = []
        in_skip = False
        for line in lines2:
            if line.strip().startswith("## Key Rules"):
                in_skip = False  # keep from here
            if in_skip:
                continue
            if line.strip().startswith("**Examples:**"):
                in_skip = True
                continue
            result2.append(line)
        condensed = "\n".join(result2).strip() + "\n"

    return f'---\ntrigger: model_decision\ndescription: "{trigger_desc}"\n---\n{condensed}'

if __name__ == "__main__":
    cmd = sys.argv[1]
    skill_path = sys.argv[2]

    fm, body = read_skill(skill_path)
    trigger = "Use when the user wants to study, document, understand, or share analysis of a software project/codebase. Triggers on requests like 'walk through this project', 'explain this codebase', 'generate documentation for this project', 'help me understand this code'."

    if cmd == "body":
        sys.stdout.write(body)
    elif cmd == "cursor":
        sys.stdout.write(gen_cursor(body, trigger))
    elif cmd == "opencode":
        sys.stdout.write(gen_opencode(body, fm))
    elif cmd == "windsurf":
        max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 12000
        sys.stdout.write(gen_windsurf(body, trigger, max_chars))
    elif cmd == "check":
        # Read target and compare body
        target = sys.argv[3]
        _, target_body = read_skill(target)
        if target_body == body:
            print("SYNC")
        else:
            print("OUT_OF_SYNC")
PYEOF
)

run_python() {
    python3 -c "$CONVERT_PY" "$@"
}

# ─── Cursor ──────────────────────────────────────────────────

generate_cursor() {
    local target="$ROOT/cursor/project-walkthrough.mdc"
    run_python cursor "$SKILL" > "$target"
    echo "✓ Cursor: $target"
}

# ─── Windsurf (condensed <12K) ───────────────────────────────

generate_windsurf() {
    local target="$ROOT/.windsurf/rules/project-walkthrough.md"
    mkdir -p "$(dirname "$target")"
    run_python windsurf "$SKILL" "$MAX_WINDSURF_CHARS" > "$target"

    local chars
    chars=$(wc -c < "$target" | tr -d ' ')
    if [ "$chars" -gt "$MAX_WINDSURF_CHARS" ]; then
        echo "⚠ Windsurf: ${chars} chars exceeds ${MAX_WINDSURF_CHARS} limit" >&2
    else
        echo "✓ Windsurf: $target (${chars} chars)"
    fi
}

# ─── OpenCode ─────────────────────────────────────────────────

generate_opencode() {
    local target="$ROOT/.opencode/skills/project-walkthrough/SKILL.md"
    mkdir -p "$(dirname "$target")"
    run_python opencode "$SKILL" > "$target"
    echo "✓ OpenCode: $target"
}

# ─── Check mode ──────────────────────────────────────────────

check_sync() {
    local ok=true
    local body
    body=$(run_python body "$SKILL")

    # Cursor
    local cursor_check
    cursor_check=$(run_python check "$SKILL" "$ROOT/cursor/project-walkthrough.mdc")
    if [ "$cursor_check" = "SYNC" ]; then
        echo "✓ Cursor: in sync"
    else
        echo "✗ Cursor: OUT OF SYNC"
        ok=false
    fi

    # OpenCode
    local opencode_check
    opencode_check=$(run_python check "$SKILL" "$ROOT/.opencode/skills/project-walkthrough/SKILL.md")
    if [ "$opencode_check" = "SYNC" ]; then
        echo "✓ OpenCode: in sync"
    else
        echo "✗ OpenCode: OUT OF SYNC"
        ok=false
    fi

    # Windsurf: char limit only (content is condensed, can't compare directly)
    local windsurf_chars
    windsurf_chars=$(wc -c < "$ROOT/.windsurf/rules/project-walkthrough.md" | tr -d ' ')
    if [ "$windsurf_chars" -gt "$MAX_WINDSURF_CHARS" ]; then
        echo "✗ Windsurf: ${windsurf_chars} chars exceeds ${MAX_WINDSURF_CHARS} limit"
        ok=false
    else
        echo "✓ Windsurf: ${windsurf_chars} chars (within limit)"
    fi

    if [ "$ok" = true ]; then
        echo "All platforms in sync."
        return 0
    else
        echo "Run ./scripts/convert.sh to regenerate."
        return 1
    fi
}

# ─── Main ────────────────────────────────────────────────────

case "${1:-all}" in
    cursor)    generate_cursor ;;
    windsurf)  generate_windsurf ;;
    opencode)  generate_opencode ;;
    --check)   check_sync ;;
    all)
        generate_cursor
        generate_windsurf
        generate_opencode
        echo ""
        echo "All platforms generated from $SKILL"
        ;;
    *)
        echo "Usage: $0 [cursor|windsurf|opencode|--check|all]" >&2
        exit 1
        ;;
esac
