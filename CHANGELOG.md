# Changelog

## [Unreleased]

### Added

### Fixed

## [0.9.5] - 2026-10-26

### Added

- **ruyi-version-check skill v0.1.0 入库** (`skills/ruyi-version-check/`, pilot promoted to an in-repo skill): deterministic version-consistency checker — `validate_versions.py` verifies skill frontmatter (canonical), plugin.json, marketplace.json, README badges, Phase 0 banner, per-skill CHANGELOG, dist copies, and hardcoded version literals in tests all agree before a release. PASS/WARN/FAIL report with file:line, expected/actual, remediation hint; exit codes 0 consistent / 1 warnings / 2 failures; `--format json` supported. Registered in the collection marketplace.json.
- **`make check-versions` target**: runs `validate_versions.py --root .` across the collection, so version drift is checkable with one command instead of a manual agent invocation.
- **`test-version-check` CI job**: rebuilds the eval fixtures to verify determinism, runs the pytest suite, then `evals/validate.py` structural regression.

### Changed

- **`make check-versions` is now CI-blocking** (`make ci` runs it; the `test.yml` workflow invokes `validate_versions.py --root .` directly) with new `--strict` semantics: default mode exits `0` on warnings-only so WARNs never block CI, FAIL still exits `2`; `--strict` (WARN-only → `1`) is for the pre-release consistency gate. Report display and process exit code derive from one `Report.exit_code(strict)` computation.
- **ruyi-version-check skill 0.1.0 → 0.1.1**: exit-code/`--strict` semantics above; `SKILL_BODY_PATTERNS` coverage extended to the `Project Walkthrough vX.Y.Z` startup print (no `--version` prefix, not the `**Version X**` banner form — previously missed).

### Fixed

- **`convert.sh` could resolve the wrong SKILL.md** (`find | head -n 1`): `skills/<name>/evals/fixtures/*/SKILL.md` demo files could shadow the real skill, writing `demo-skill` artifacts into `dist/` (opencode/windsurf/cursor) and skipping the real skill's platform copies. `_find_skill_md` now prefers the canonical nested `skills/<name>/skills/<name>/SKILL.md`, falls back to the outer `skills/<name>/SKILL.md`, and never descends into `evals/`, `tests/`, `dist/`. Regression-tested in `tests/test_convert.py`.
- **Root CHANGELOG backfilled 0.9.1–0.9.4**: `release.sh` had failed to write these version blocks (only 0.9.0 and 0.1.1 existed), leaving shipped fixes — quiz answer-index bug, update-check cache staleness, walkthrough manifest/verify pipeline hardening — unrecorded. Backfilled from commit history.
- **`test-version-check` CI job working-directory** fixed to the outer skill dir (`skills/ruyi-version-check`): the evals/pytest steps resolve relative to the skill root, not the nested inner skill dir.

## [0.9.4] - 2026-06-29

### Fixed

- **Hardened manifest/verify accuracy pipeline (4 bugs)** in ruyi-project-walkthrough (skill 1.6.4 → 1.6.5, PR#11):
  - `verify_html` now surfaces code-block citation coverage (`code_blocks` / `code_blocks_cited` / `code_blocks_uncited`) in `verify-result.json`, so Phase 3C uncited source-derived code blocks are no longer silently passed (Bug 1).
  - `verify_sources.py` no longer aborts with `IsADirectoryError` on `directory_structure` claims whose `source_file` is a real directory; directories now skip the line-count check (Bug 2).
  - `sources-manifest.schema.json` now accepts an optional `source_project.version` field (was rejected by `additionalProperties:false` as `'version' was unexpected`) (Bug 3).
  - `verify-result.json` adds an explicit `chapter_count` field to disambiguate `expected_sections` (`.md` count) from `section_count` (includes quiz + promo) (Bug 4).
  - Tests: +8 (2 dir-handling, 1 schema version, 5 code-block coverage); suite 300 passed, 23 skipped.

## [0.9.3] - 2026-06-22

### Fixed

- **`check_update.sh` false "new version" prompt after upgrade**: the 24h cache replayed the stored `remoteSha` whenever it differed from the local SHA, without noticing the local SHA had changed. Right after `claude plugin update`, users saw one bogus "🔄 有新版本可用" prompt pointing backwards (new local SHA → older cached remote SHA), self-healing only after 24h. The cache now also stores `localShaAtCheck`; if the current local SHA differs (user upgraded), the cache is treated as stale and the script re-checks the remote. Backward compatible (old caches are treated as stale → re-check).
- ruyi-project-walkthrough skill 1.6.3 → 1.6.4.

## [0.9.2] - 2026-06-22

### Added

- **SessionStart auto update-check hook**: new `hooks/hooks.json` + `hooks/session-start` at the collection root run `scripts/check_update.sh` on every session start (and after clear/compact). When a newer version is published, the upgrade reminder is injected as SessionStart `additionalContext` so Claude surfaces it in its first reply. Works across ruyi/paoding/davinci/doraemon with no per-brand edits. Previously `check_update.sh` only ran when a skill agent manually invoked it mid-walkthrough, so installed users never saw update prompts.
- ruyi-project-walkthrough skill 1.6.2 → 1.6.3.

## [0.9.1] - 2026-06-22

### Fixed

- **Quiz correct-answer index always collapsed to option A** in ruyi-project-walkthrough: `parse_quiz_md` extracted the answer letter with `re.search(r'([A-D])', '**Answer: B**')`, which matched the `A` inside the literal word "Answer" instead of the real answer letter. Every quiz question's correct index became `0`, so picking A was always judged correct and picking the real answer was judged wrong. The regex is now anchored to "after the colon, before the closing `**`" (`r'[：:]\s*([A-D])\s*\*\*'`). Also fixes the inter-question `---` separator being appended to the preceding explanation. Affected every report generated with `--quiz-chapter` since 2026-05-27 (commit ca1f371). Added `test_quiz_parsing.py` regression coverage.
- ruyi-project-walkthrough skill 1.6.1 → 1.6.2.

## [0.9.0] - 2026-06-16

### Added

- **brand-config.json `language` field** (zh|en): davinci/doraemon = en, ruyi/paoding = zh. Brand homepage language convention is now config-driven, single source of truth.
- **verify-sync.sh language purity check (5b)**: English-first brand homepages must have 0 Chinese (except the language toggle), Chinese-first must contain Chinese — fails sync on CN/EN mixing, preventing regression.
- **brand-sync coverage gaps closed**: Step 9d2 (skill install-docs incl. README_zh), 9d3 (skill `.github/*.md`), 9d4 (skill-level CLAUDE.md), 9d5 (skill `docs/` source docs), Step 10 (CLAUDE.md Remotes table + push remote `ruyi`→`origin`), Step 12b (exclude source dev planning artifacts from brand repos).
- **English-first homepages for davinci/doraemon**: Skills content (descriptions/usage/params/comparison table) now sourced from `README.en.md`; brand-unique intro/story preserved.
- **Competitor comparison table** in project homepage `README.md` and `README.en.md` for the ruyi-github-safe-publish skill section. Sourced from `github-safe-publish` upstream `docs/README_zh.md`. Covers GitHub Safe Publish vs Gitleaks / TruffleHog / git-secrets on 14 dimensions (price, detection method, rule count, auto-fix, publishing flow, backup, PII, internal infra, AI semantic, file blacklist, git history, platform, SEO, CI).
- **brand-sync Step 3b** in `brand-sync-tool/sync.sh`: auto-propagates `ruyi-skills/README.en.md` to all brand `README.en.md` on every sync. Previously required a manual `git commit && git push` from `output/<brand>/` after each sync.

### Changed

- Aligned both skills' user-facing docs to the collection command model: install is `/plugin install ruyi-skills@ruyi-skills`, commands are `/ruyi-<skill>` (PR#3-9). Fixes standalone-model leakage where `/plugin install project-walkthrough@ruyi-skills` would fail (no such plugin in the collection marketplace).
- De-branded source examples (`tests/test_watermark.py` comment, `SKILL.md` prefix example) that leaked bare `ruyi` into brand repos.
- 3 brand templates in `brand-sync-tool/brands/{paoding,davinci,doraemon}/README.md` updated to mirror the new comparison table; next sync carries the change to all 3 brand GitHub remotes.

## [0.1.1] - 2026-05-26 - 2026-05-26

### Added

- Multi-brand skill collection: ruyi-skills, paoding-skills, davinci-skills, doraemon-skills
- 2 skills: github-safe-publish (v0.7.0), project-walkthrough (v1.6.1)
- CI workflow with per-skill tests and structure validation
- Makefile with test/ci/release/sync/convert/clean targets
- sync-all.sh for pushing to 4 remotes with per-brand customization
- Hybrid version check (git SHA + time fallback) via scripts/check_update.sh
- check_self_contained.py to enforce skill self-containment
- GitHub community templates (bug report, feature request, PR)
- Architecture design document with 8 principles
