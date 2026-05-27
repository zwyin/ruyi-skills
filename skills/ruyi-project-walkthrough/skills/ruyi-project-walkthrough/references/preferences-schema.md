---
name: preferences-schema
description: EXTEND.md YAML schema for project-walkthrough user preferences
---

# Preferences Schema

## Full Schema

```yaml
---
version: 1

defaults:
  scope: auto              # auto | full | focused | overview
  depth_per_chapter: auto  # auto | detailed | standard | summary
  manifest_strictness: auto # auto | required | optional | skip
  output_format: both      # both | markdown | html

language: zh               # zh | en

confirm_scope: true        # true | false — show confirmation gate

review_outline: true       # true | false — review chapters before generation
---
```

## Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | int | 1 | Schema version |
| `defaults.scope` | string | `auto` | Default walkthrough scope. `auto` = determined by content analysis. `full` = preserve all chapters/sections. `focused` = select key chapters. `overview` = consolidate to themes. |
| `defaults.depth_per_chapter` | string | `auto` | Default depth per chapter. `auto` = based on input scope. `detailed` = full analysis with quiz and cross-references. `standard` = key points with selected examples. `summary` = brief overview only. |
| `defaults.manifest_strictness` | string | `auto` | Sources manifest requirement. `auto` = required for software, optional for documents. `required` = always generate manifest. `optional` = generate if code examples present. `skip` = never generate manifest. |
| `defaults.output_format` | string | `both` | Output format. `both` = markdown + HTML. `markdown` = markdown only. `html` = HTML only. |
| `language` | string | `zh` | Output language for walkthrough content. |
| `confirm_scope` | bool | `true` | Show confirmation gate before generation. Set to `false` to skip and use defaults directly (like `--no-confirm`). |
| `review_outline` | bool | `true` | Show chapter outline for review before generation. |

## Scope Options

| Value | Description |
|-------|-------------|
| `auto` | Analyze content and recommend (default) |
| `full` | Preserve all input chapters/sections 1:1 |
| `focused` | Select 8-10 most important chapters, summarize rest |
| `overview` | Consolidate into 5-8 thematic chapters |

## Depth Options

| Value | Description |
|-------|-------------|
| `auto` | Based on input scope (default) |
| `detailed` | Full analysis + data + quiz + cross-references + critical assessment |
| `standard` | Key points + important data + selected examples |
| `summary` | Core findings only, 2-5 sentences per chapter |

## Manifest Strictness Options

| Value | Description |
|-------|-------------|
| `auto` | Required for software projects, optional for documents (default) |
| `required` | Always generate sources-manifest.json |
| `optional` | Generate manifest only if code examples are present |
| `skip` | Never generate manifest |

## EXTEND.md Paths

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.project-walkthrough/EXTEND.md` | Project |
| 2 | `~/.project-walkthrough/EXTEND.md` | User home |

## Example: Minimal Preferences

```yaml
---
version: 1
defaults:
  scope: auto
  depth_per_chapter: auto
language: zh
---
```

## Example: Document-focused Preferences

```yaml
---
version: 1
defaults:
  scope: full
  depth_per_chapter: detailed
  manifest_strictness: optional
  output_format: both
language: zh
confirm_scope: true
review_outline: true
---
```

## Example: Quick Overview Preferences

```yaml
---
version: 1
defaults:
  scope: overview
  depth_per_chapter: summary
  manifest_strictness: skip
  output_format: html
language: en
confirm_scope: false
review_outline: false
---
```

## First-Time Setup

When no EXTEND.md is found, ask the user:

1. **Default scope preference?** — auto (Recommended) / full / focused / overview
2. **Default depth preference?** — auto (Recommended) / detailed / standard / summary
3. **Default language?** — zh / en
4. **Save location?** — Project / User home

Save result and continue. This setup is blocking — must complete before analysis begins.

## Changing Preferences

- **Edit directly**: open EXTEND.md and change fields
- **Reconfigure**: delete EXTEND.md or say "reconfigure walkthrough preferences"
- **One-shot override**: use command flags (`--depth`, `--scope`) which override EXTEND.md for that run
