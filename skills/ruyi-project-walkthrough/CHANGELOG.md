# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.6.3] - 2026-06-22

### Added

- **SessionStart auto update-check hook**: new `hooks/hooks.json` + `hooks/session-start` at the collection root run `scripts/check_update.sh` on every session start (and after clear/compact). When a newer version is published, the upgrade reminder is injected as SessionStart `additionalContext` so Claude surfaces it in its first reply. `check_update.sh` already has a 24h cache + network fallback, so this adds no per-session latency. Works across ruyi/paoding/davinci/doraemon with no per-brand edits (the hook has no brand strings; `check_update.sh`'s REPO/PLUGIN_KEY is brand-replaced by brand-sync as before). Previously `check_update.sh` only ran when a skill agent manually invoked it mid-walkthrough, so installed users never saw update prompts.

## [1.6.2] - 2026-06-22

### Fixed

- **Quiz correct-answer index always collapsed to 0 (option A)**: `parse_quiz_md` extracted the answer letter with `re.search(r'([A-D])', '**Answer: B**')`, which matched the `A` inside the literal word "Answer" instead of the real answer letter. Every quiz question's correct index became `0` regardless of the actual answer, so picking A was always judged correct and picking the real answer was judged wrong. The search regex is now anchored to "after the colon, before the closing `**`" (`r'[：:]\s*([A-D])\s*\*\*'`), so the correct option is honored. Affected every report generated with `--quiz-chapter` since 2026-05-27 (commit ca1f371); existing reports need regenerating.
- **Quiz explanation no longer trailing with `---`**: the inter-question `---` separator was being appended to the preceding question's explanation text. The parser now stops collecting explanation at a standalone `---` line.

## [1.6.1] - 2026-05-22

### Added

- **verify-result.json**: converter auto-generates structured verification evidence alongside HTML, containing passed status, section count, size ratio, nav count, errors, and UTC timestamp
- Phase 5 delivery gate now requires `verify-result.json` to exist and contain `"passed": true` — cannot claim PASSED without the file
- Delivery report template reads actual metrics from verify-result.json instead of allowing model to fabricate values

### Changed

- README: "交付质量门禁" rephrased as "自动质量门禁" — quality gates are automatic, not a user parameter
- `verify_html()` returns structured result dict (exit code + metrics) instead of exit code only

## [1.6.0] - 2026-05-22

### Added

- **Converter-first HTML generation**: `md_to_html.py` is now the canonical HTML generator for all depth levels, replacing manual JS DOM construction. Eliminates silent empty-section failures caused by innerHTML restrictions.
- **i18n in converter**: `--lang zh|zh-pure|en|bilingual` flag generates HTML with matching language for sidebar, navigation, quiz, and theme toggle labels.
- **Interactive quiz support**: `--quiz-chapter N` extracts quiz questions from markdown and generates a JavaScript-based interactive quiz section with scoring.
- **Per-section content verification**: `--verify` checks each section individually for empty content, not just aggregate metrics.
- **XSS protection**: `sanitize_url()` blocks `javascript:` and `data:` URLs; HTML entity escaping; `<details>` body sanitization.
- **Delivery quality gates**: Phase 5 now has a 3-retry error recovery loop that reads specific `--verify` error output and takes targeted corrective actions before delivery.
- **Safety net for .md links**: 3-stage removal of broken internal `.md` cross-references (dual nav, single nav, inline href).

### Changed

- Phase 4 workflow: all depths now use converter (no manual fallback). Brief/medium get curated output, deep gets full-content conversion.
- Phase 5 rewritten: delivery gate with automated + model-verified checks, quality metrics report template.
- HTML reference (`docs/html-reference.md`): added Generation Strategy section, updated DOM rules to "converter developers only", made content density gate a hard requirement.
- Quiz format canonically defined in Phase 3B (`**Q<N>:**` questions, `- A.` options, `**Answer: X**`, `**Explanation:**`).

### Fixed

- Empty HTML sections: root cause was innerHTML restriction making rich content generation impractical. Solved by Python pre-rendered static HTML.
- Quiz option parsing: regex now handles `- A. Option` markdown list format (`r'^(?:[-*]\s+)?([A-D])[.)]\s+(.*)'`).
- Navigation counting: verify now counts only sidebar nav links (excludes prev/next buttons).
- Broken `.md` links: inline cross-references like `[text](01-overview.md)` now stripped by catch-all regex.

## [1.5.0] - 2026-05-20

### Changed

- Deep mode HTML generation upgraded to full-content conversion: Phase 3 does content, Phase 4 does styling only — no trimming, no summarization, no omission
- Phase 4 now distinguishes brief/medium (curated HTML) from deep (complete markdown-to-HTML conversion)
- Added 5-step deep-mode Phase 4 protocol: read .md → convert every element → add interactive features → content parity check → file size gate
- Deep HTML file size must be ≥80% of total markdown size (e.g., 160K markdown → 150K+ HTML)
- Checklist adds 2 deep-only items: content parity verification, file size ratio check

## [1.4.0] - 2026-05-20

### Added

- `--lang` expanded from 2 to 4 modes: `zh` (中文+英文术语，默认), `zh-pure` (纯中文), `en` (纯英文), `bilingual` (中英对照)
- `--version` standalone flag: prints version and exits
- Language selection (Q5) added to Phase 0.3 confirmation gate
- `--lang` flag pre-selects matching option in confirmation gate
- Updated JSON schema (`sources-manifest.schema.json`) with 4-value lang enum
- Documentation standards updated with conventions for each language mode
- 9 new tests for language modes and version flag (295 total)

### Changed

- README: updated parameter table, usage examples, and EXTEND.md sample with 4 lang values
- SKILL.md frontmatter: argument-hint and version line updated
- Platform files regenerated via `convert.sh`

## [1.3.0] - 2026-05-20

### Added

- `scripts/release.sh`: automated release workflow (bump → PR → CI → merge → tag)
- `make release` target in Makefile
- Release workflow documentation in CONTRIBUTING.md

### Changed

- `verify_sources.py`: missing source directories now silently skip instead of warning

### Docs

- Simplified TODO.md: removed 60 lines of completed items
- CONTRIBUTING.md: added release workflow section

## [1.2.1] - 2026-05-20

### Fixed

- CI timeout: node JS validation 5s → 10s (zod HTML fixture too large for ubuntu-latest)

### Added

- MIT LICENSE file
- GitHub issue templates (bug report, feature request)
- PR template with test/checklist reminders

## [1.2.0] - 2026-05-20

### Added

- **AGENTS.md**: Cross-platform auto-discovery file at project root (Cursor/Windsurf/OpenCode scan this automatically)
- **GitHub Actions CI**: Automated test workflow on push to master/develop and PRs (pytest + convert.sh --check)
- **convert.sh tests**: 20 new tests for platform file generation (281 total)
- marketplace.json version synced to 1.1.0

## [1.1.0] - 2026-05-20

### Added

- **Multi-language support** (`--lang zh|en`): Chinese body + English terms (default), or pure English output
- **Adaptive scope system**: Phase 0 analyzes input, recommends scope/depth, interactive confirmation gate
- **Document/Report walkthrough**: Full support for non-code projects with 1:1 chapter preservation
- **EXTEND.md preferences**: Per-project and per-user preference files with YAML schema
- **Platform compatibility files**:
  - Cursor IDE: `cursor/project-walkthrough.mdc`
  - Windsurf: `.windsurf/rules/project-walkthrough.md` (condensed <12K chars)
  - OpenCode: `.opencode/skills/project-walkthrough/SKILL.md`
  - Gemini CLI: compatible with `gemini skills install`
- **Project type templates**: Game Engine, Database/Storage Engine, Compiler/Interpreter
- **Cross-platform conversion script**: `scripts/convert.sh` generates all platform files from canonical SKILL.md
- **Self-demo examples**: `examples/self-demo-zh/` and `examples/self-demo-en/` walkthrough of the plugin itself
- **Quick-start section** in README for beginners and senior developers

### Changed

- SKILL.md parameter design migrated from positional args to `--flag` convention
- `--no-confirm` flag added to skip Phase 0 confirmation gate
- Exploration protocol updated with new project types (game engine, database, compiler)
- README updated with multi-platform installation instructions

### Fixed

- HTML string escaping: JS string escaping rules for quotes and special characters in interactive HTML
- Escaping test rewritten to use node-based validation
- Plugin packaging: `plugin.json` and `marketplace.json` format validation
- Test fixtures for `--lang` coverage

### Tests

- Dynamic MANIFEST_PROJECTS discovery: auto-scans examples/ directory (3 → 16 project coverage)
- Template and protocol tests for new project types
- Test count: 185 → 261 (all passing)

## [1.0.0] - 2026-05-09

### Added

- Manifest-first Phase 3 workflow (3A verify → 3B write → 3C validate)
- `sources-manifest.json` schema with `verify_sources.py` validation script
- `import_graph.py` dependency graph extraction (Python, TypeScript, Rust)
- `// Simplified from:` citation format (disallows `// Source:`)
- Chapter templates for AI Tool, Library, Web App, CLI Tool, Document/Report
- Exploration protocol with project type detection
- HTML reference spec: DOM-only API, dark/light toggle, sidebar, quiz
- Documentation standards with language-specific conventions
- 185 tests covering structure, manifest, citations, and source integrity
- 12 rounds of accuracy verification (Rounds 10-12 consecutive zero issues)
