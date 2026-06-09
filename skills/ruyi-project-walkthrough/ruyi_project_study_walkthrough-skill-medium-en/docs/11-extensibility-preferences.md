# Extensibility: EXTEND.md & Preferences

The project supports user-configurable preferences through EXTEND.md files, an analysis framework for content detection, and a scope matrix that maps content signals to generation parameters.

## EXTEND.md Preference System

Users can save their preferred settings to avoid specifying flags every time. The system checks two locations in priority order:

```text
// Simplified from: skills/ruyi-project-walkthrough/SKILL.md:147-159
| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.project-walkthrough/EXTEND.md` | Project |
| 2 | `$HOME/.project-walkthrough/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Read, parse, display summary → continue |
| Found but invalid YAML | Display error, offer first-time setup |
| Not found | Run first-time setup → save EXTEND.md → continue |
```

### EXTEND.md Format

The file uses YAML frontmatter in a Markdown file:

```yaml
// Simplified from: skills/ruyi-project-walkthrough/references/preferences-schema.md
---
scope: auto        # auto | full | focused | overview
depth: auto        # auto | detailed | standard | summary
language: zh       # zh | zh-pure | en | bilingual
manifest_strictness: auto  # auto | required | optional | skip
confirm_scope: true  # true | false
---
```

CLI flags override EXTEND.md defaults. For example, `--depth medium --lang en` overrides `depth: auto` and `language: zh` from the preferences file.

### First-Time Setup

When no EXTEND.md is found, the plugin runs an interactive setup:

1. Default scope? — auto / full / focused / overview
2. Default depth? — auto / detailed / standard / summary
3. Language? — zh / zh-pure / en / bilingual
4. Save location? — Project / User home

The schema is documented in `references/preferences-schema.md` with examples for common configurations.

## Analysis Framework

The content analysis phase (Phase 0.2) follows the framework in `references/analysis-framework.md` (179 lines). It defines five analysis dimensions:

### 1. Content Type Detection

```text
// Simplified from: skills/ruyi-project-walkthrough/references/analysis-framework.md
Signals:
- source code files present → software-project weight
- package manifests → software-project weight
- markdown chapters > 3 → document-report weight
- code/text ratio → distinguishes mixed from pure
```

Three possible types: `software-project`, `document-report`, `mixed`.

### 2. Input Scope Measurement

Quantifies the input:

- File/chapter count
- Total lines of content
- Directory depth (nesting levels)
- Number of distinct data types (code, tables, statistics, quotes)

### 3. Content Structure Analysis

Identifies what kinds of data are present:

| Signal | Indicates |
|--------|-----------|
| Code blocks | Technical content requiring excerpts |
| Tables | Structured data requiring formatting |
| Statistics/numbers | Quantitative claims needing verification |
| Case studies | Narrative content needing preservation |
| Architecture diagrams | Complex relationships needing simplification |

### 4. Technical Density Assessment

Classifies the content as low, medium, or high technical density:

- **Low** — mostly prose, few code blocks
- **Medium** — mixed code and prose
- **High** — primarily code with dense technical references

Density affects manifest strictness and code example selection.

### 5. Recommendation Generation

Produces specific recommendations:

- Scope (overview / focused / full)
- Chapter count range
- Per-chapter depth (standard / detailed)
- Manifest strictness (required / optional / skip)

## Scope Matrix

The `references/scope-matrix.md` (125 lines) maps content signals to scope/depth recommendations:

```text
// Simplified from: skills/ruyi-project-walkthrough/references/scope-matrix.md
| Content Signal | Recommended Scope | Chapter Guide |
|---------------|-------------------|---------------|
| < 10 source files | overview | 5-8 chapters |
| 10-30 source files | focused | 10-15 chapters |
| > 30 source files | full | No hard limit |
| Document < 10 chapters | full (1:1) | Match input |
| Document 10-20 chapters | focused | Select key ones |
| Document > 20 chapters | overview | Thematic groups |
```

The matrix also considers technical density: high-density content gets more detailed per-chapter analysis even at overview scope.

## Confirmation Gate Integration

Phase 0.3's confirmation gate uses the analysis results to pre-select recommended options:

- The `--depth` flag sets initial recommendations
- Content analysis adjusts recommendations based on actual input
- Users can override any recommendation at confirmation

This ensures users make informed decisions about scope trade-offs (e.g., warning when overview scope would discard >50% of chapters).

[Previous: Interactive HTML UX](10-interactive-html-ux.md) | [Next: Quality Assurance & CI](12-quality-assurance-ci.md)
