# Changelog

All notable changes to ruyi-version-check are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
