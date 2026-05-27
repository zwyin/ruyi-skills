---
name: scope-matrix
description: Content signal to scope/depth mapping for walkthrough generation
---

# Scope Matrix

Maps content signals to recommended output parameters. Like baoyu-comic's auto-selection, but for walkthrough generation.

## Content Signal Matrix

### Software Projects

| Project signals | Scope | Chapters | Depth per chapter | Manifest |
|----------------|-------|----------|-------------------|----------|
| CLI tool, small library (< 20 files) | overview | 5-8 | standard | required |
| Web app, API service (20-100 files) | focused | 10-15 | detailed | required |
| Large framework, monorepo (100-500 files) | full | 15-25 | detailed | required |
| Massive ecosystem (500+ files) | full | 20-30+ | detailed | required |
| Plugin/skill system, AI tool | full | 12-20 | detailed | required |

### Documents/Reports

| Document signals | Scope | Chapter strategy | Depth per chapter | Manifest |
|-----------------|-------|-----------------|-------------------|----------|
| Research paper, study report | full | 1:1 preserve | detailed | optional |
| Playbook, manual, guide | full | 1:1 preserve | detailed | optional |
| Case study collection | full | 1:1 preserve each case | standard | optional |
| Meeting notes, logs | focused | Group by theme | summary | skip |
| Mixed: tutorial with code | full | Preserve structure | detailed | optional |
| Very long (> 30 chapters) | focused | Select top 20-25 | detailed | optional |

### Mixed Content

| Mixed signals | Scope | Strategy | Depth | Manifest |
|--------------|-------|----------|-------|----------|
| Tutorial repo (code + docs) | full | Code chapters + doc chapters | detailed | required for code, optional for docs |
| Literate programming | full | Follow source structure | detailed | required |
| Code-heavy blog/book | full | 1:1 preserve | detailed | optional |

## Depth Definitions

### detailed (deep analysis)

Each chapter gets:
- Complete content coverage (no truncation)
- Data tables preserved verbatim
- Code examples with source citations
- Cross-references to related chapters
- Quiz questions (3-5 per chapter)
- Critical assessment where applicable
- Architecture/structure diagrams

### standard (balanced)

Each chapter gets:
- Key points and main findings
- Important data tables (summary, not all rows)
- Selected code examples
- Cross-references to major related chapters
- Quiz questions (1-2 per chapter)

### summary (overview)

Each chapter gets:
- Core finding or purpose (2-5 sentences)
- Key statistics or metrics only
- No code examples
- No quiz
- Navigation links

## Enrichment Options

| Enrichment | Description | Default for | Optional for |
|-----------|-------------|------------|-------------|
| quiz | Interactive quiz with instant feedback | detailed | standard |
| cross_references | Links between related chapters | detailed, standard | summary |
| critical_assessment | Strengths/limitations/quality review | detailed (software) | documents |
| architecture_diagrams | Import graph, data flow, structure | software projects | documents |
| case_study_analysis | Individual case breakdown | documents with cases | software |
| data_tables | Full data preservation | documents with data | all |
| source_citations | `// Simplified from:` comments | software projects | documents |

## Confirmation Gate Defaults

When presenting options to the user, these are the defaults based on content type:

### Software project (detected)

```
Recommended: full scope, 15-25 chapters, detailed, manifest required
```

### Document/report (detected)

```
Recommended: full scope, N chapters (= input count), detailed, manifest optional
```

### Mixed (detected)

```
Recommended: full scope, preserve structure, detailed, manifest for code sections
```

## Priority Order

Like baoyu-comic's priority system:

1. **User-specified options** (`--depth`, `--audience`, explicit scope request)
2. **EXTEND.md defaults**
3. **Content signal analysis** (this matrix)
4. **Fallback**: full scope, detailed, manifest required

## Scope Override Examples

User can override recommendations at confirmation gate:

| User intent | Override | Effect |
|-------------|---------|--------|
| "Just give me an overview" | scope: overview | Consolidate to 5-8 thematic chapters |
| "Focus on the key findings" | scope: focused | Select 8-10 most important chapters |
| "I want everything" | scope: full | Preserve all chapters with full depth |
| "Quick summary only" | depth: summary | Each chapter gets 2-5 sentence summary |
| "I need this for teaching" | depth: detailed + quiz | Full analysis with quiz for each chapter |
