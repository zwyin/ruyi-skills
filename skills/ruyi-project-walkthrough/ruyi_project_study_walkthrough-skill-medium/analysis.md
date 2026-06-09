---
content_type: software-project
project_name: project-walkthrough
version: "1.6.1"
depth: medium
scope: focused
audience: general
lang: zh
chapters_planned: 12
total_files: 203
markdown_files: 114
python_files: 12
shell_files: 2
json_files: 15
technical_density: high
---

# Content Analysis: project-walkthrough

## Type Detection

- **Content type**: software-project
- **Signals**: source code files (.py, .sh), package manifests (plugin.json, marketplace.json), CI workflow, test suite, documentation

## Scope Measurement

- Total files: 203 (excluding .git)
- Markdown files: 114 (docs, examples, tests/fixtures)
- Python scripts: 12 (md_to_html.py, verify_sources.py, import_graph.py, __init__.py, tests)
- Shell scripts: 2 (convert.sh, release.sh)
- JSON files: 15 (manifests, schemas, plugin config)
- Key source: SKILL.md (890 lines) — canonical skill definition

## Content Structure

- Statistics: version history (6 releases), test counts (295 tests), file sizes
- Code blocks: Python, Bash, JSON, YAML throughout
- Architecture: 5-phase pipeline (Phase 0-5), manifest-first verification
- Documentation: exploration protocol, chapter templates, HTML reference, accuracy protocol

## Technical Density: High

- Multi-phase pipeline with formal verification protocol
- Python markdown-to-HTML converter with quiz parsing, i18n, XSS protection
- Manifest-first accuracy system with JSON Schema validation
- Multi-platform code generation (Cursor/Windsurf/OpenCode/Gemini)

## User Selections

- **Scope**: focused (12 key chapters)
- **Per-chapter depth**: detailed
- **Format**: HTML + Markdown
- **Outline review**: yes (approved)
- **Language**: zh (Chinese + English technical terms)

## Chapter Plan

| # | Title | Primary Sources |
|---|-------|----------------|
| 01 | Overview | README.md, SKILL.md frontmatter, plugin.json |
| 02 | 5-Phase Pipeline Architecture | SKILL.md Process section |
| 03 | Phase 0: Analysis & Confirmation Gate | SKILL.md Phase 0, EXTEND.md, analysis-framework.md |
| 04 | Phase 1-2: Exploration & Chapter Planning | exploration-protocol.md, chapter-templates.md |
| 05 | Phase 3: Manifest-First Accuracy | SKILL.md Phase 3, sources-manifest-schema.md |
| 06 | md_to_html.py: The HTML Converter | scripts/md_to_html.py |
| 07 | Supporting Scripts | verify_sources.py, import_graph.py, convert.sh |
| 08 | Release Automation & Version Sync | scripts/release.sh, 6 location sync |
| 09 | Multi-Platform Compatibility | convert.sh output, platform files |
| 10 | Testing & CI | tests/*.py, .github/workflows/test.yml |
| 11 | Design Philosophy | cross-cutting design decisions |
| 12 | Summary & Extension Guide | CONTRIBUTING.md, TODO.md |
