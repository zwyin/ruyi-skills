# Changelog

## [Unreleased] - 2026-06-14

### Added

- **Competitor comparison table** in project homepage `README.md` and `README.en.md` for the ruyi-github-safe-publish skill section. Sourced from `github-safe-publish` upstream `docs/README_zh.md`. Covers GitHub Safe Publish vs Gitleaks / TruffleHog / git-secrets on 14 dimensions (price, detection method, rule count, auto-fix, publishing flow, backup, PII, internal infra, AI semantic, file blacklist, git history, platform, SEO, CI).
- **brand-sync Step 3b** in `brand-sync-tool/sync.sh`: auto-propagates `ruyi-skills/README.en.md` to all brand `README.en.md` on every sync. Previously required a manual `git commit && git push` from `output/<brand>/` after each sync.

### Changed

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
