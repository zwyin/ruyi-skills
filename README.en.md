# ruyi-skills

[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![platform](https://img.shields.io/badge/platform-Claude%20Code-purple)](https://claude.ai/code)

Claude Code skills that simplify complex tasks — one command to rule them all.

[中文](README.md)

> **Ruyi** (如意): a Chinese cultural symbol meaning "as you wish." Every skill in this collection turns complex, time-consuming tasks into a single command.

## Install Skills

### Option 1: Via Browse UI

Select **Browse and install plugins** → Select **ruyi-skills** → Select **Install now**

### Option 2: Direct Install

```bash
# 1. Add marketplace
/plugin marketplace add zwyin/ruyi-skills

# 2. Install the plugin
/plugin install ruyi-skills@ruyi-skills

# 3. Reload plugins
/reload-plugins
```

### Option 3: Ask the Agent

Simply tell the Agent:

```
Please install Skills from github.com/zwyin/ruyi-skills
```

### Option 4: Quick Install (npx)

```bash
npx skills add zwyin/ruyi-skills
```

### Option 5: ClawHub (coming soon)

> Not yet published to ClawHub registry. Track progress at [github.com/zwyin/ruyi-skills](https://github.com/zwyin/ruyi-skills).

```bash
clawhub install ruyi-github-safe-publish
clawhub install ruyi-project-walkthrough
```

### Option 6: Manual Install

```bash
git clone https://github.com/zwyin/ruyi-skills.git
claude --plugin-dir ./ruyi-skills
```

---

## Skills

### ruyi-github-safe-publish

Safely publish to GitHub — two-layer desensitization scanning (135 rules + AI), auto-fix, backup & rollback, end-to-end workflow.

[![version](https://img.shields.io/badge/version-0.7.0-blue)](skills/ruyi-github-safe-publish/skills/ruyi-github-safe-publish/SKILL.md)

**Covers 6 dimensions**: Secrets & Credentials (100 rules), Database Connections (5 rules), PII (8 rules), Internal Infrastructure (6 rules), File Blacklist (12 rules), Git History (4 rules).

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

---

### ruyi-project-walkthrough

Project walkthrough generator — multi-depth, multi-audience, multi-language, outputs markdown + interactive HTML.

[![version](https://img.shields.io/badge/version-1.6.1-blue)](skills/ruyi-project-walkthrough/skills/ruyi-project-walkthrough/SKILL.md)

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

---

## License

[MIT](LICENSE)
