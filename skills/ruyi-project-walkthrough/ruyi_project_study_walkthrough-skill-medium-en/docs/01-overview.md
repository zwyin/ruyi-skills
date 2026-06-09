# Project Overview

Project Walkthrough is a Claude Code skill plugin that generates structured technical walkthroughs of any software project. Given a codebase directory, it produces numbered markdown chapters and a self-contained interactive HTML file with sidebar navigation, dark/light theme toggle, and an interactive quiz.

## What It Does

The plugin analyzes a project's source code, identifies its architecture and key design decisions, and produces documentation at configurable depth levels:

- **Brief** — 5-8 thematic chapters, quick orientation (~30 min to produce)
- **Medium** — 10-15 chapters with code excerpts and design rationale (~60 min)
- **Deep** — Comprehensive analysis with line-by-line code walkthrough (~120 min)
- **All** — All three levels sequentially

It supports multiple audiences (general with analogies, or developer-focused) and four output languages (Chinese with English terms, pure Chinese, English, or bilingual).

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Skill definition | Markdown (SKILL.md) |
| Scripts | Python 3, Bash |
| Tests | pytest |
| Generated output | Markdown + HTML/CSS/JS |
| CI | GitHub Actions |
| Version management | shell script + sed |

The project has no runtime dependencies beyond Python 3 and a POSIX shell.

## Installation

The plugin installs through Claude Code's plugin system:

```text
// Simplified from: README.md:27-32
### Claude Code（推荐）

```bash
# 1. 添加 marketplace
/plugin marketplace add zwyin/project-walkthrough-skill

# 2. 安装插件
/plugin install project-walkthrough@project-walkthrough-skill
```
```

Alternative platforms (Cursor, Windsurf, OpenCode, Gemini CLI) each have their own installation paths detailed in the README.

## Key Features

The README lists the plugin's core capabilities:

```text
// Simplified from: README.md:9-21
- **多深度**：brief（概览）、medium（进阶）、deep（深入）、all（全部）
- **多受众**：general（类比+白话）、dev（纯技术）
- **多语言**：zh（中文+英文术语，默认）、zh-pure（纯中文）、en（纯英文）、bilingual（中英对照）
- **输出**：编号 markdown 章节 + 自包含交互式 HTML（暗色/亮色、侧边栏、quiz）
- **Converter-first HTML**：md_to_html.py 离线转换器，Python 预渲染静态 HTML
- **自动质量门禁**：生成后自动校验 section 完整性、内容密度、broken links
- **自适应范围**：Phase 0 分析内容类型，推荐 scope/depth/format
- **偏好配置**：支持项目级/用户级 EXTEND.md
- **自动探索协议**：识别项目类型 → 读核心文件 → 提取创新点 → 生成章节
- **Manifest-first 准确性保证**：先验证所有声明，再写内容
```

## Plugin Metadata

The plugin registers itself through two JSON files:

```json
// Simplified from: .claude-plugin/plugin.json:1-13
{
  "name": "project-walkthrough",
  "description": "Generate structured technical walkthroughs of any software project...",
  "version": "1.6.1",
  "author": { "name": "zwyin" },
  "homepage": "https://github.com/zwyin/project-walkthrough-skill",
  "license": "MIT",
  "skills": "./skills/"
}
```

The `marketplace.json` provides registration info for Claude Code's marketplace, listing the plugin under the "development" category with tags like "walkthrough", "documentation", "code-analysis", and "architecture".

## Project Structure

```
project-walkthrough-skill/
├── .claude-plugin/          # Plugin metadata
├── skills/                  # Skill definitions (SKILL.md)
├── scripts/                 # Python & Bash tools
├── tests/                   # pytest test suite
├── docs/                    # Design documentation
├── cursor/                  # Cursor IDE adapter
├── .windsurf/               # Windsurf adapter
├── .opencode/               # OpenCode adapter
├── CHANGELOG.md             # Version history
├── CLAUDE.md                # Project-specific instructions
├── Makefile                 # Build targets
└── README.md                # User-facing documentation
```

## Quick Start

```text
// Simplified from: README.md:64-66
# Basic usage (brief overview of current project)
/project-walkthrough

# Deep technical analysis
/project-walkthrough /path/to/project --depth deep --audience dev
```

[Next: Architecture & Design Philosophy](02-architecture-design-philosophy.md)
