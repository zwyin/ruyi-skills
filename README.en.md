# ruyi-skills

[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![platform](https://img.shields.io/badge/platform-Claude%20Code-purple)](https://claude.ai/code)

Claude Code skills that simplify complex tasks — one command to rule them all.

[中文](README.md)

> **Ruyi** (如意): a Chinese cultural symbol meaning "as you wish." Every skill in this collection turns complex, time-consuming tasks into a single command.

## Install Skills

### Quick Install (recommended)

```bash
git clone https://github.com/zwyin/ruyi-skills.git
cd ruyi-skills && bash scripts/install.sh
```

`install.sh` auto-detects local agents (`~/.claude` → Claude Code, `~/.codex` → Codex CLI) and copies every skill into the matching skill roots. Idempotent — rerun anytime. Flags: `--agent claude|codex`, `--skill <name>`, `--list`, `--uninstall`.

### Install Matrix (multi-agent)

| Agent | Install | Verify |
|-------|---------|--------|
| Claude Code (same paths for GLM and other Anthropic-compatible endpoints) | Quick Install above copies into `~/.claude/skills/<name>/` by default; or use the plugin options below | `ls ~/.claude/skills/`, then invoke the skill in a new session |
| Codex CLI | Quick Install above copies into `~/.codex/skills/<name>/` (force with `--agent codex`); project-level: `bash scripts/convert.sh --all`, then copy `dist/codex/<name>/` into `<repo>/.agents/skills/` (SKILL.md is natively recognized, no format change) | `codex debug prompt-input "hi" 2>/dev/null \| grep <name>` (no login needed, see [docs/portability/codex.md](docs/portability/codex.md)) |
| Cursor (community path, not load-tested) | `bash scripts/convert.sh --all`, then copy `dist/cursor/.cursor/rules/` into `~/.cursor/rules/` | Restart Cursor, check Settings → Rules |
| Windsurf (community path, not load-tested) | `bash scripts/convert.sh --all`, then merge `dist/windsurf/.windsurfrules/` files into the project `.windsurfrules` (or global rules) | Rules activation prompt in Windsurf |
| OpenCode (community path, not load-tested) | `bash scripts/convert.sh --all`, then copy `dist/opencode/.opencode/skills/` into the project `.opencode/skills/` | Skill listed once `opencode` starts |

> Codex paths and verification follow official docs plus binary testing (`docs/portability/codex.md`); the Cursor / Windsurf / OpenCode rows are community conventions, not load-tested by this collection.

### Plugin options (Claude Code)

**Via Browse UI**

Select **Browse and install plugins** → Select **ruyi-skills** → Select **Install now**

**Direct Install**

```bash
# 1. Add marketplace
/plugin marketplace add zwyin/ruyi-skills

# 2. Install the plugin
/plugin install ruyi-skills@ruyi-skills

# 3. Reload plugins
/reload-plugins
```

**Ask the Agent**

Simply tell the Agent:

```
Please install Skills from github.com/zwyin/ruyi-skills
```

**Quick Install (npx)**

```bash
npx skills add zwyin/ruyi-skills
```

**ClawHub (coming soon)**

> Not yet published to ClawHub registry. Track progress at [github.com/zwyin/ruyi-skills](https://github.com/zwyin/ruyi-skills).

```bash
clawhub install ruyi-github-safe-publish
clawhub install ruyi-project-walkthrough
```

**Manual Install**

```bash
git clone https://github.com/zwyin/ruyi-skills.git
claude --plugin-dir ./ruyi-skills
```

---

## Skills

### ruyi-github-safe-publish

Safely publish to GitHub — two-layer desensitization scanning (135 rules + AI), auto-fix, backup & rollback, end-to-end workflow.

[![version](https://img.shields.io/badge/version-0.7.1-blue)](skills/ruyi-github-safe-publish/skills/ruyi-github-safe-publish/SKILL.md)

**Covers 6 dimensions**: Secrets & Credentials (100 rules), Database Connections (5 rules), PII (8 rules), Internal Infrastructure (6 rules), File Blacklist (12 rules), Git History (4 rules).

**Competitor Comparison**:

| Feature | GitHub Safe Publish | Gitleaks | TruffleHog | git-secrets |
|------|:-:|:-:|:-:|:-:|
| Price | **Free / Open Source** | Free | Free | Free |
| Detection Method | Rules + AI (two layers) | Rules only | Rules only | Rules only |
| Rule Count | **135 rules** | ~120 rules | 800+ detectors | ~20 rules |
| Auto-fix | **Yes** | No | No | No |
| Publishing Flow | **End-to-end** | No | No | No |
| Backup & Rollback | **Yes** | No | No | No |
| PII Detection | **Yes (email/phone/national ID)** | No | No | No |
| Internal Infra | **Yes (internal IP/domain/path)** | No | No | No |
| AI Semantic Analysis | **Yes** | No | No | No |
| File Blacklist | **Yes (.env/.pem/.key etc.)** | No | Partial | No |
| Git History Scan | **Yes** | Yes | Yes | No |
| Platform | Claude Code | CLI | CLI | CLI |
| SEO Optimization | **Yes** | No | No | No |
| CI Generation | **Yes** | No | No | No |

> **Positioning difference**: Gitleaks/TruffleHog are pure secret detection tools, ideal for CI integration. GitHub Safe Publish is an end-to-end publishing assistant — scan, fix, create repo, and push in one shot, with AI covering semantic leaks that regex rules can't catch.

```bash
# Full workflow: scan → fix → publish to GitHub
/ruyi-github-safe-publish

# Core + SEO optimization (description, topics, badges)
/ruyi-github-safe-publish --seo

# Core + CI generation (auto-detect project type, generate .github/workflows/test.yml)
/ruyi-github-safe-publish --ci

# Full: core + SEO + CI
/ruyi-github-safe-publish --seo --ci

# Scan only — output report, no fix, no publish
/ruyi-github-safe-publish --scan

# Dry run — scan + fix suggestions, but no actual changes
/ruyi-github-safe-publish --dry-run
```

| Flag | Description | Mutual Exclusion |
|------|-------------|------------------|
| (none) | Core workflow: scan + publish | — |
| `--seo` | Add SEO optimization (description, topics, badges, README) | Cannot combine with `--scan` / `--dry-run` |
| `--ci` | Add CI generation (auto-detect and generate workflow) | Cannot combine with `--scan` / `--dry-run` |
| `--scan` | Scan only, output report | Cannot combine with `--seo` / `--ci` / `--dry-run` |
| `--dry-run` | Dry run: scan + suggestions, no changes | Cannot combine with `--seo` / `--ci` / `--scan` |

[→ Full documentation](skills/ruyi-github-safe-publish/README.md)

---

### ruyi-project-walkthrough

Project walkthrough generator — multi-depth, multi-audience, multi-language, outputs markdown + interactive HTML.

[![version](https://img.shields.io/badge/version-1.6.6-blue)](skills/ruyi-project-walkthrough/skills/ruyi-project-walkthrough/SKILL.md)

```bash
# Auto-analyze current directory, recommend depth
/ruyi-project-walkthrough

# Specify project path
/ruyi-project-walkthrough /path/to/project

# Quick overview (small projects or first-time review)
/ruyi-project-walkthrough --depth brief

# Deep walkthrough (comprehensive analysis)
/ruyi-project-walkthrough --depth deep

# Full walkthrough (all details, large projects)
/ruyi-project-walkthrough --depth all

# For developer audience
/ruyi-project-walkthrough --audience dev

# Pure English output
/ruyi-project-walkthrough --lang en

# Bilingual output (Chinese + English side by side)
/ruyi-project-walkthrough --lang bilingual

# Skip confirmation, use recommended defaults (automation-friendly)
/ruyi-project-walkthrough --no-confirm

# Combine: deep walkthrough + dev audience + English
/ruyi-project-walkthrough --depth deep --audience dev --lang en

# Print version
/ruyi-project-walkthrough --version
```

| Flag | Description | Values | Default |
|------|-------------|--------|---------|
| `path` | Project path | any directory path | current directory |
| `--depth` | Walkthrough depth | `brief` / `medium` / `deep` / `all` | auto-recommended |
| `--audience` | Target audience | `general` / `dev` | `general` |
| `--lang` | Output language | `zh` / `zh-pure` / `en` / `bilingual` | `zh` |
| `--no-confirm` | Skip confirmation | (flag, no value) | — |
| `--version` | Print version | (flag, no value) | — |

[→ Full documentation](skills/ruyi-project-walkthrough/README.md)

### ruyi-version-check

Version-consistency checker — a pre-release health check that verifies every version surface in the collection (frontmatter / manifests / Phase 0 banner / badges / CHANGELOG / dist) agrees. A maintainer tooling skill, not an end-user feature.

[![version](https://img.shields.io/badge/version-0.1.2-blue)](skills/ruyi-version-check/skills/ruyi-version-check/SKILL.md)

```bash
python3 skills/ruyi-version-check/scripts/validate_versions.py --root .
```

---

## Version & Update

### Check Installed Version

Look for the `version` field in the SKILL.md frontmatter:

```bash
# macOS / Linux
cat ~/.claude/plugins/cache/ruyi-skills/*/skills/*/skills/*/SKILL.md | grep version
```

Or ask Claude directly:

```
What version of ruyi-skills do I have installed?
```

### Update to Latest Version

Re-install to get the latest version:

```bash
/plugin install ruyi-skills@ruyi-skills
/reload-plugins
```

Or via npx:

```bash
npx skills add zwyin/ruyi-skills
```

---

## Version & Update

### Check Installed Version

Look for the `version` field in the SKILL.md frontmatter:

```bash
# macOS / Linux
cat ~/.claude/plugins/cache/ruyi-skills/*/skills/*/skills/*/SKILL.md | grep version
```

Or ask Claude directly:

```
What version of ruyi-skills do I have installed?
```

### Update to Latest Version

Re-install to get the latest version:

```bash
/plugin install ruyi-skills@ruyi-skills
/reload-plugins
```

Or via npx:

```bash
npx skills add zwyin/ruyi-skills
```

---

## License

[MIT](LICENSE)
