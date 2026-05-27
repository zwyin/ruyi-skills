# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.7.0] - 2026-05-26

### Added

- `docs/README_zh.md`: Chinese documentation with competitive comparison, 6 dimensions detail, test coverage table
- "About the 135 Rules" section in both READMEs: explains 6-dimension vs single-dimension comparison with TruffleHog/Gitleaks
- Installation instructions updated: `/plugin marketplace add` + `/plugin install` commands, multi-platform table (Cursor/Windsurf/OpenCode)

### Fixed

- Corrected entropy example values in `docs/scanning-rules.md` (3.2→3.7, 4.0→4.7, 4.6→4.9)

### Changed

- `scripts/release.sh`: replaced `sed -i.bak` with `perl -pi -e` for macOS compatibility
- `scripts/validate_skill.sh`: displays version at startup
- `.github/workflows/test.yml`: test count floor (230) + coverage gate (95%)
- `README.md` test badge updated to 235 passing
- Expanded version sync check to 5/6 locations (README badge, CHANGELOG header)

## [0.6.1] - 2026-05-26

### Added

- Shannon entropy calculation tests (9 tests in `tests/test_entropy.py`)
- Detection tests expanded from 25 to 134 rules (134/135 = 99% rule coverage)
- Test suite expanded from 3 to 7 files (235 total tests, 99% coverage)
- CI regression guards: test count floor, coverage gate, version sync check
- New test helper `_detects_file()` for FILE dimension rules (uses `模式` field)
- Coverage: GitHub tokens (app/fine-grained/OAuth/refresh), cloud providers (GCP/DigitalOcean/Vercel/Netlify/Supabase/Fly.io/Deno/Scaleway), AI providers (Anthropic admin/HuggingFace/Perplexity/xAI/Replicate/DeepSeek), DevOps (GitLab deploy/runner/CICD/feed/K8s/Databricks/PlanetScale/Pulumi/Linear), SaaS (Notion/Shopify/Sendinblue/RubyGems/Postman/Artifactory), crypto (private key/JWT/K8s secret), PII (Chinese ID/US SSN/credit card/bank card/password), infrastructure (internal IP/hostname/path/URL/VPN), FILE dimension (12 rules), GIT history (3 rules)

## [0.6.0] - 2026-05-25

### Added

- `scripts/convert.sh`: multi-platform skill converter (Cursor .mdc, Windsurf .windsurfrules, OpenCode AGENTS.md)
- Cursor output: splits SKILL.md into core workflow + optional modules (`.cursor/rules/*.mdc` with YAML frontmatter)
- Windsurf output: single `.windsurfrules` file
- OpenCode output: single `AGENTS.md` file
- `tests/test_convert.py`: 13 tests validating all platform conversions

## [0.5.0] - 2026-05-25

### Added

- `README.md`: project overview, features, usage, architecture, installation, and testing instructions
- `.github/workflows/test.yml`: CI pipeline (Ubuntu + macOS, Python 3.10 + 3.12)
- `scripts/release.sh`: README.md guard (conditional sed) and dynamic branch detection

### Fixed

- 5-round independent review: rule count accuracy (132→135), regex fixes (Discord/Supabase/email/vault), flow logic (stash conflict, placeholder URL scope, filter-repo --force), cross-file consistency tests, CHANGELOG and CLAUDE.md corrections

## [0.4.0] - 2026-05-25

### Added

- **--seo module**: Description optimization, topic tags, shields.io badges, README structure check (SEO-1 to SEO-5)
- **--ci module**: Project type detection, platform matrix decision, `.github/workflows/test.yml` generation (CI-1 to CI-4)
- Plugin metadata: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for Claude Code marketplace
- Release script: `scripts/release.sh` for automated version bump + PR + tag workflow
- Plugin metadata tests: `tests/test_plugin_metadata.py` for validating plugin.json and marketplace.json

## [0.3.0] - 2026-05-25

### Added

- **Step 5**: Repository decision + push — interactive confirmation (visibility, name, description), placeholder URL replacement, auto-push via gh CLI with conflict handling, manual-push fallback
- **Step 6**: Verification + output report — auto-verify via gh repo view, three report formats (full / --scan-only / --dry-run)
- Step 5-6 structure tests (11 new tests)

## [0.2.0] - 2026-05-25

### Added

- **47 new scanning rules** based on Gitleaks (120+ rules) and TruffleHog (800+ detectors) source code analysis
- New dimension **A2: Database Connection Strings** (5 rules): PostgreSQL, MySQL, MongoDB, Redis, JDBC
- Total dimensions: 5 → 6 (added A2: Database)
- **Cloud/deploy platforms**: Vercel, Netlify, Supabase, Fly.io, Deno, Cloudflare Global/Origin CA, DigitalOcean, Scaleway
- **HashiCorp Vault**: service token (hvs.) + batch token (hvb.)
- **Source control**: Bitbucket (Client ID/Secret), GitLab (CI Job/Feed/K8s Agent tokens)
- **AI providers**: Google Gemini, DeepSeek, xAI, Replicate
- **Infra/DevOps**: Confluent, Fastly, LaunchDarkly, Codecov, Doppler, ClickHouse, PlanetScale, ngrok
- **Others**: Dropbox, GCP Service Account, Shopify Shared Secret, Sentry DSN, Sendinblue, Mattermost, MS Teams, Contentful
- 6 new scanning rule tests (database strings, vault tokens, cloud platforms, AI providers, bitbucket, connection string dimension)
- Rule count: 88 → 135

## [0.1.0] - 2026-05-25

### Added

- **Two-layer desensitization scanning architecture**: Layer 1 (88 deterministic regex rules, 5 dimensions) + Layer 2 (AI semantic scan via independent sub-agents)
- **5 scanning dimensions**: Keys/Credentials (58), PII (8), Internal Infrastructure (6), File Blacklist (12), Git History (4)
- **Step 1**: Pre-flight checks + centralized interactive confirmation (mode, push method, config summary)
- **Step 2**: Backup branch (`pre-publish-backup`) with stash handling and conflict resolution
- **Step 3**: Two-layer scanning with convergence (max 2 AI rounds)
- **Step 4**: Auto-fix + user confirmation (CRITICAL/WARNING/SAFE severity, 4 fix options, fix-verify loop)
- **Flow control matrix**: full / --scan-only / --dry-run modes
- Shannon entropy detection (threshold 4.5) for generic API key filtering
- `docs/scanning-rules.md`: complete regex reference for Layer 1 rules
- `tests/`: 33 structure and scanning rule tests
- `scripts/validate_skill.sh`: one-click validation script
- Competitive research: Gitleaks + TruffleHog analysis
