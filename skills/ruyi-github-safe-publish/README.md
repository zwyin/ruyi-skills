# GitHub Safe Publish

[![version](https://img.shields.io/badge/version-0.7.0-blue)](skills/ruyi-github-safe-publish/SKILL.md) [![license](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![tests](https://img.shields.io/badge/tests-235%20passing-brightgreen)](tests/) [![platform](https://img.shields.io/badge/platform-Claude%20Code-purple)](https://claude.ai/code)

Safely publish local Git projects to GitHub public repositories with two-layer desensitization scanning (135 deterministic rules + AI semantic analysis), auto-fix, backup, and end-to-end publishing workflow.

A [Claude Code](https://claude.ai/code) skill / plugin.

[← Back to ruyi-skills collection](../../README.md) · [中文文档](docs/README_zh.md)

## Why

Pushing a local project to a public GitHub repo risks leaking secrets, PII, internal infrastructure details, and other sensitive data. Existing tools like Gitleaks and TruffleHog detect secrets but don't fix them or handle the full publishing workflow.

GitHub Safe Publish combines **deterministic rule scanning** (135 regex rules across 6 dimensions) with **AI semantic analysis** to find what regexes miss, then walks you through fixing, creating the repo, and pushing — all in one command.

## Features

- **Two-layer scanning**: 135 deterministic rules (Layer 1) + AI semantic analysis with independent sub-agents (Layer 2)
- **6 scanning dimensions**: Keys/Credentials (100), Database Connection Strings (5), PII (8), Internal Infrastructure (6), File Blacklist (12), Git History (4)
- **Auto-fix with user confirmation**: Replace secrets with placeholders, or choose manual fix / delete / accept risk
- **Backup branch**: `pre-publish-backup` created before any modifications for easy rollback
- **End-to-end publishing**: Interactive repo creation via `gh` CLI with visibility, name, and description confirmation
- **Optional `--seo`**: GitHub description optimization, topic tags, shields.io badges, README structure check
- **Optional `--ci`**: Auto-detect project type and generate `.github/workflows/test.yml`

## Usage

```
/github-safe-publish                    # Full flow: scan → fix → publish
/github-safe-publish --scan-only        # Scan only, output report, no fix/publish
/github-safe-publish --dry-run          # Scan + show fix suggestions, no actual changes
/github-safe-publish --seo              # Full flow + SEO optimization
/github-safe-publish --ci               # Full flow + CI workflow generation
/github-safe-publish --seo --ci         # Everything
```

### Flow Control

| Step | Full | --scan-only | --dry-run |
|------|------|-------------|-----------|
| 1. Pre-flight checks | yes | yes | yes |
| 2. Backup branch | yes | skip | skip |
| 3. Two-layer scan | yes | yes | yes |
| 4. Auto-fix + confirm | yes | skip | suggestions only |
| 5. Repo create + push | yes | skip | skip |
| 6. Verify + report | yes | scan report | scan report + suggestions |

## Architecture

```
Step 1: Pre-flight + interactive confirmation
Step 2: Create backup branch (pre-publish-backup)
Step 3: Two-layer desensitization scan
  Layer 1: 135 deterministic regex rules (6 dimensions)
  Layer 2: AI semantic scan (1-2 rounds, independent sub-agents)
Step 4: Auto-fix + user confirmation (CRITICAL / WARNING / SAFE)
Step 5: Repo decision + push (interactive, via gh CLI)
Step 6: Verification + report
```

### Scanning Dimensions

| Dimension | Rules | What it detects |
|-----------|-------|-----------------|
| A. Keys/Credentials | 100 | AWS, Azure, GCP, GitHub, GitLab, OpenAI, Stripe, Slack, and 90+ more providers |
| A2. Database Strings | 5 | PostgreSQL, MySQL, MongoDB, Redis, JDBC connection strings |
| B. PII | 8 | Email, phone, national ID, names |
| C. Infrastructure | 6 | Internal IPs, local paths, internal domains, NAS/VPN URLs |
| D. File Blacklist | 12 | .env, .pem, .key, .db, credentials.*, etc. |
| E. Git History | 4 | Sensitive data in commit messages, deleted files |

See [docs/scanning-rules.md](docs/scanning-rules.md) for the complete regex reference.

## About the 135 Rules

You might wonder: Gitleaks has ~120 rules, TruffleHog has 873+ detectors — why only 135?

**Apples vs oranges.** TruffleHog's 873 detectors are single-dimensional (API keys only), mostly covering niche SaaS services. Our 135 rules span **6 dimensions** — keys/credentials (100), database connection strings (5), PII (8), internal infrastructure (6), file blacklist (12), and git history (4). We overlap with TruffleHog on ~50 popular providers (AWS, Azure, GCP, GitHub, Stripe, etc.) and cover 15 providers they don't (npm, DigitalOcean, Cloudflare, Telegram, Discord, etc.).

The real differentiator isn't rule count — it's what happens **after** detection: AI semantic analysis catches what regexes miss, auto-fix replaces secrets with placeholders, and the end-to-end workflow handles repo creation and push. No other tool does this pipeline.

## Installation

### Option 1: Browse UI

Select **Browse and install plugins** → Select **github-safe-publish** → Select **Install now**

### Option 2: Marketplace Install

```bash
# 1. Add marketplace
/plugin marketplace add zwyin/github-safe-publish

# 2. Install plugin
/plugin install github-safe-publish@github-safe-publish
```

### Option 3: Ask the Agent

```
Please install github-safe-publish from github.com/zwyin/github-safe-publish
```

### Option 4: Quick Install (npx)

```bash
npx skills add zwyin/github-safe-publish
```

### Option 5: ClawHub

```bash
clawhub install github-safe-publish
```

### Option 6: Manual

```bash
git clone https://github.com/zwyin/github-safe-publish.git
claude --plugin-dir ./github-safe-publish
```

Or copy `skills/ruyi-github-safe-publish/SKILL.md` to your project's skill directory.

### Other Platforms

| Platform | Install |
|----------|---------|
| **Cursor** | Copy `dist/cursor/*.mdc` files to `.cursor/rules/` |
| **Windsurf** | Copy `dist/windsurf/.windsurfrules` to `.windsurf/rules/` |
| **OpenCode** | Copy `dist/opencode/AGENTS.md` to `.opencode/skills/` |

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

Or use the validation script:

```bash
bash scripts/validate_skill.sh
```

## Project Structure

```
github-safe-publish/
├── .claude-plugin/          # Plugin metadata
├── skills/                  # Skill definitions
│   └── github-safe-publish/
│       └── SKILL.md         # Single source of truth
├── docs/
│   ├── scanning-rules.md    # Complete regex reference (135 rules)
│   └── superpowers/specs/   # Design documents
├── scripts/
│   ├── release.sh           # Version bump + tag
│   └── validate_skill.sh    # One-click validation
├── tests/                   # 235 tests
├── CHANGELOG.md
├── CLAUDE.md
└── LICENSE
```

## License

[MIT](LICENSE)
