# Changelog

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
