# Contributing to Project Walkthrough Skill

## Development Setup

```bash
git clone https://github.com/zwyin/ruyi-skills.git
cd ruyi-skills
pip install pytest jsonschema pyyaml
```

## Project Structure

- `skills/ruyi-project-walkthrough/SKILL.md` — Canonical skill definition (single source of truth)
- `docs/` — Reference docs (chapter templates, exploration protocol, HTML spec)
- `scripts/` — Helper tools (`convert.sh`, `verify_sources.py`, `import_graph.py`)
- `tests/` — Test suite (pytest)
- Platform files are auto-generated — do not edit directly

## Making Changes

### 1. Edit canonical source

Only modify these files directly:

- `skills/ruyi-project-walkthrough/SKILL.md` — Skill logic, parameters, process
- `docs/chapter-templates.md` — Project type templates
- `docs/exploration-protocol.md` — Project type detection
- `docs/html-reference.md` — HTML output spec
- `docs/documentation-standards.md` — Writing conventions
- `scripts/verify_sources.py` / `scripts/import_graph.py` — Validation tools

### 2. Regenerate platform files

After changing SKILL.md:

```bash
make generate                  # Regenerate Cursor, Windsurf, OpenCode files
make check                     # Verify all platforms in sync
```

### 3. Run tests

```bash
make ci                        # All CI checks (test + sync check)
make test                      # Full test suite with verbose output
make test-quick                # Quick test run
```

### 4. Commit and PR

- Work on `develop` branch
- Create PR to `master`
- CI runs automatically (pytest + convert.sh --check)

### 5. Release

Use the automated release script:

```bash
make release VERSION=1.3.0              # Full release (bump + PR + merge + tag)
./scripts/release.sh 1.3.0 --bump-only  # Only bump version files, no PR/tag
```

The script validates semver format, requires clean tree on `develop`, runs `make ci`, then handles the full workflow: bump → commit → push → PR → wait CI → merge → tag → sync develop.

## Adding a New Project Template

1. Add template to `docs/chapter-templates.md` (Brief/Medium/Deep levels)
2. Add project type to `docs/exploration-protocol.md` classification table
3. Add tests in `tests/test_adaptive_scope.py` (template existence + protocol detection)
4. Run `pytest tests/` to verify

## Adding a New Platform

1. Add generation logic to `scripts/convert.sh` (Python section)
2. Add output path to `--check` mode
3. Add tests in `tests/test_convert.py`
4. Update README.md installation table and project structure
5. Run `./scripts/convert.sh` to regenerate all files

## Code Style

- Python: PEP 8, type hints optional
- Bash: `set -euo pipefail`, quote variables
- Markdown: hard wrap at 100 chars
- No emojis in code or docs unless explicitly requested

## Testing Conventions

- Every code block in example walkthroughs must have `// Simplified from:` citation
- Manifest tests are auto-discovered from `examples/` directory
- Platform file tests verify frontmatter + body sync with canonical SKILL.md
- 295 tests must all pass before merge
