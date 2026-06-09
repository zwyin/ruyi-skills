---
content_type: software-project
project_name: project-walkthrough-skill
scope: full
depth: detailed
chapter_count: 13
audience: general
lang: en
manifest_strictness: required
---

# Content Analysis

## Type
Software project — Claude Code skill plugin for generating structured project walkthroughs.

## Scope
- ~40 files across source, tests, docs, platform adapters
- ~8,356 lines of source code
- 5 Python scripts, 3 shell scripts, 1 Makefile, 8 test files
- Multi-platform output (Cursor, Windsurf, OpenCode)

## Content Structure
- Python source: `md_to_html.py` (643L), `verify_sources.py` (315L), `import_graph.py` (239L)
- Shell scripts: `convert.sh` (272L), `release.sh` (166L)
- Skill definition: `SKILL.md` (890L)
- Tests: 8 files, ~2,778 lines total
- Documentation: 8 docs files
- Platform adapters: Cursor (.mdc), Windsurf (.md), OpenCode (SKILL.md)

## Technical Density
High — core logic in Python, multi-phase pipeline, JSON Schema validation, automated release workflow.

## User Selections
- Scope: Full walkthrough
- Depth: Detailed
- Format: HTML + Markdown
- Language: English
- Review outline: Yes (approved)
