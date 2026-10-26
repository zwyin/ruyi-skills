# Changelog

All notable changes to ruyi-version-check are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.2] - 2026-10-26

### Changed

- Cross-agent portability: description now leads with an English one-liner containing `Use when` trigger scenarios (existing Chinese detail line kept verbatim below); frontmatter adds a `license: MIT` field. Both satisfy the collection's `scripts/check_portability.py` lint gate.

## [0.1.1] - 2026-10-26

### Changed
- Exit-code semantics (CI no longer blocked by WARNs): default mode now exits
  `0` on warnings-only (FAIL still exits `2`); new `--strict` flag restores
  `WARN-only -> 1` for pre-release checks. `main()`, `render_json`, and the
  `render_text` Summary line all derive the exit code from one
  `Report.exit_code(strict)` computation — report display and process exit
  code can no longer disagree.

### Added
- `SKILL_BODY_PATTERNS` now covers the `Project Walkthrough vX.Y.Z` startup
  print (e.g. `Print Project Walkthrough v1.6.5`), which has no `--version`
  prefix and is not the `**Version X**` banner form — previously missed.

## [0.1.0] - 2026-07-27

### Added
- Initial pilot: `validate_versions.py` deterministic version-consistency checker.
  - Collection layer: marketplace.json version vs CHANGELOG latest entry.
  - Per skill: frontmatter (canonical), plugin.json, marketplace.json, skill
    CHANGELOG, skill README badge, collection README badge membership, Phase 0
    banner, `--version` doc strings.
  - dist copies (opencode/cursor/windsurf) frontmatter + banner drift (WARN).
  - Hardcoded version literals in tests (WARN).
  - PASS/WARN/FAIL report with file:line, expected/actual, remediation hint.
  - Exit codes: 0 consistent / 1 warnings / 2 failures. `--format json` supported.
- evals framework (simplified from khazix neat-freak): `trigger-eval.json`,
  `evals.json` (5 behavior evals), `validate.py` (structural regression),
  5 minimal fixtures.
- pytest suite covering all fixtures.
