# Architecture & Design Philosophy

The project is built around a small number of deliberate design principles that shape every component. Understanding these principles makes the codebase much easier to navigate.

## Single Source of Truth: SKILL.md

The entire plugin's behavior is defined in one file: `skills/ruyi-project-walkthrough/SKILL.md`. This 890-line document contains the skill's frontmatter metadata, argument parsing rules, depth/scope mappings, the complete 5-phase generation process, accuracy rules, and the quality checklist.

All platform-specific files (Cursor `.mdc`, Windsurf `.md`, OpenCode `SKILL.md`) are generated from this single source via `convert.sh`. They should never be manually edited.

```text
// Simplified from: skills/ruyi-project-walkthrough/SKILL.md:1-6
---
name: ruyi-project-walkthrough
version: "1.6.1"
description: Generate a structured walkthrough of any project...
argument-hint: "[path] [--depth brief|medium|deep|all] [--audience general|dev] [--lang zh|zh-pure|en|bilingual] [--no-confirm]"
---
```

The CLAUDE.md file in the project root reinforces this principle:

```text
// Simplified from: CLAUDE.md:2-5
### 唯一版本源

版本号定义在 `skills/project-walkthrough/SKILL.md` frontmatter 的 `version` 字段。
**所有其他位置的版本号必须从这里同步，不允许手动分别修改。**
```

## Self-Contained Skill

Each skill must work when extracted from the repository. The SKILL.md and its `references/` directory cannot link to files outside the skill directory. This constraint means the skill can be installed independently without pulling in the entire repository.

## Multi-Layer Output Pipeline

The generation process follows a strict pipeline with five phases:

```
Phase 0: Analyze & Confirm → analysis.md
     ↓
Phase 1: Explore → read source files
     ↓
Phase 2: Plan → chapter outline
     ↓
Phase 3: Generate Markdown → sources-manifest.json + NN-*.md files
     ↓
Phase 4: Generate HTML → walkthrough.html
     ↓
Phase 5: Verify & Deliver → verify-result.json
```

Each phase feeds into the next. Phase 3 is further split into two gated sub-phases (3A: verify claims, 3B: write content) to enforce accuracy.

## Manifest-First Accuracy

The most distinctive design principle: **verify before write**. You cannot write a claim in a chapter unless it has been verified and recorded in `sources-manifest.json`. The manifest is a write permit, not an audit log.

This means:
1. Phase 3A lists all planned claims and verifies each one against the actual source code
2. Only verified claims get manifest entries with `verified: true`
3. Phase 3B can only write content that has a corresponding manifest entry
4. Unverifiable claims are dropped — they don't appear in the walkthrough

## Converter-First HTML

HTML generation is done entirely by `md_to_html.py`, not by the AI model. The model's job in Phase 4 is to run the converter script, not to write HTML. This separation ensures:

- Content decisions happen in Phase 3 (markdown)
- Phase 4 is mechanical conversion — no content modification
- Automated verification catches any conversion issues
- The same converter handles all depth levels

## Adaptive Scope

The plugin adapts its output to the input's size and type. Rather than forcing every project into the same structure, Phase 0 analyzes the content and recommends appropriate scope and depth. The user confirms before generation begins.

Content types detected:
- `software-project` — source code files > 5 or package manifest exists
- `document-report` — markdown chapters > 3 and source files < 3
- `mixed` — both code and document content

## Version Synchronization

Version numbers appear in six locations and must always match:

```text
// Simplified from: CLAUDE.md:9-18
| # | 文件 | 位置 | 说明 |
|---|------|------|------|
| 1 | SKILL.md | frontmatter version | **唯一版本源** |
| 2 | SKILL.md | --version flag 文档 | project-walkthrough vX.Y.Z |
| 3 | plugin.json | "version": "X.Y.Z" | 插件元数据 |
| 4 | marketplace.json | "version": "X.Y.Z" | Marketplace 注册 |
| 5 | README.md | version badge URL | badge/version-X.Y.Z-blue |
| 6 | CHANGELOG.md | 版本标题 | ## [X.Y.Z] - YYYY-MM-DD |
```

The `release.sh` script synchronizes all six from the SKILL.md frontmatter. Manual editing of any location except the source is forbidden.

[Previous: Project Overview](01-overview.md) | [Next: Phase Pipeline](03-phase-pipeline.md)
