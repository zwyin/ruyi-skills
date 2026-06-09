# Multi-Platform Distribution

The project generates platform-specific skill files from a single canonical source using `scripts/convert.sh` (272 lines). This ensures all AI coding platforms get identical content without manual duplication.

## The Problem

Different AI coding tools use different file formats and locations for their skill/rule definitions:

| Platform | File Location | Format |
|----------|--------------|--------|
| Claude Code | `skills/project-walkthrough/SKILL.md` | Frontmatter + Markdown |
| Cursor | `cursor/project-walkthrough.mdc` | Description header + body |
| Windsurf | `.windsurf/rules/project-walkthrough.md` | Trigger + description + condensed body |
| OpenCode | `.opencode/skills/project-walkthrough/SKILL.md` | Extended frontmatter + body |
| Gemini CLI | `gemini skills install` format | Compatible with SKILL.md |

Without automation, each platform file would need separate maintenance — a recipe for drift and inconsistency.

## convert.sh Architecture

The script reads the canonical SKILL.md and generates platform-specific files using embedded Python:

```bash
// Simplified from: scripts/convert.sh:16-20
SKILL="$ROOT/skills/ruyi-project-walkthrough/SKILL.md"
MAX_WINDSURF_CHARS=12000

if [ ! -f "$SKILL" ]; then
    echo "ERROR: $SKILL not found" >&2
    exit 1
fi
```

The embedded Python handles frontmatter parsing and format-specific generation:

```python
// Simplified from: scripts/convert.sh:31-46
def read_skill(path):
    with open(path) as f:
        text = f.read()
    parts = re.split(r'^---\s*$', text.strip(), maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        frontmatter = parts[1].strip()
        body = parts[2].strip() + "\n"
    ...
    return fm, body
```

## Platform Adapters

### Cursor (.mdc)

```python
// Simplified from: scripts/convert.sh:53-54
def gen_cursor(body, trigger_desc):
    return f'---\ndescription: "{trigger_desc}"\nglobs:\nalwaysApply: false\n---\n{body}'
```

Cursor uses `.mdc` files with a YAML header containing `description`, `globs`, and `alwaysApply`. The body is the full SKILL.md content unchanged.

### OpenCode

```python
// Simplified from: scripts/convert.sh:56-61
def gen_opencode(body, fm):
    name = fm.get("name", "project-walkthrough")
    desc = fm.get("description", "")
    arg_hint = fm.get("argument-hint", "")
    return f'---\nname: {name}\ndescription: {desc}\nlicense: MIT\ncompatibility: opencode\nargument-hint: {arg_hint}\n---\n{body}'
```

OpenCode uses the same SKILL.md format but with extended frontmatter including `license` and `compatibility` fields.

### Windsurf (Condensed)

Windsurf has a 12,000 character limit. The generator condenses the SKILL.md by removing verbose sections:

```python
// Simplified from: scripts/convert.sh:62-89
def gen_windsurf(body, trigger_desc, max_chars):
    skip_sections = {
        "## Checklist", "## Documentation Standards",
    }
    skip_subsections = {
        "#### Phase 3A: Verify",
        "#### Phase 3B: Write",
        "#### Phase 3C: Validate",
        ...
    }
    ...
    if len(condensed) > max_chars:
        # Further trim: remove examples section
        ...
```

The condensation removes checklist, documentation standards, and detailed Phase 3 sub-phases — keeping the essential usage instructions and rules.

## Sync Checking

The `--check` mode verifies all platform files are in sync with the canonical SKILL.md:

```bash
// Simplified from: scripts/convert.sh:211-252
check_sync() {
    local ok=true
    # Cursor: compare body content
    cursor_check=$(run_python check "$SKILL" "$ROOT/cursor/ruyi-project-walkthrough.mdc")
    # OpenCode: compare body content
    opencode_check=$(run_python check "$SKILL" "$ROOT/.opencode/skills/ruyi-project-walkthrough/SKILL.md")
    # Windsurf: check char limit only (content is condensed)
    windsurf_chars=$(wc -c < "$ROOT/.windsurf/rules/ruyi-project-walkthrough.md")
}
```

Cursor and OpenCode are compared for exact body match. Windsurf is checked for character limit only (since its content is intentionally condensed).

## CI Integration

The `make ci` target runs both tests and sync checking:

```makefile
// Simplified from: Makefile:18-19
ci: test check
	@echo "CI checks passed."
```

This ensures platform files never drift out of sync — CI fails if any platform file doesn't match the canonical source.

[Previous: Dependency Graph](06-dependency-graph.md) | [Next: Version Management](08-version-release.md)
