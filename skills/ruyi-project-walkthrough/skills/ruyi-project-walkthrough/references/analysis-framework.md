---
name: analysis-framework
description: Content analysis framework for determining walkthrough scope and depth
---

# Walkthrough Content Analysis Framework

Analyze input content before generating walkthrough to determine appropriate scope, depth, and structure.

## Purpose

Before generating any walkthrough content, analyze the input to:
- Detect content type (software project vs document/report vs mixed)
- Measure input scope (size, complexity, structure)
- Recommend output parameters (chapter count, depth, enrichment)
- Present recommendations for user confirmation

## Analysis Dimensions

### 1. Content Type Detection

**Signals to check:**

| Signal | How to detect | Weight |
|--------|--------------|--------|
| Source code files | Glob for `*.py`, `*.ts`, `*.js`, `*.rs`, `*.go`, `*.java`, `*.c`, `*.cpp` | High |
| Package manifests | Check for `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `pom.xml` | High |
| Continuous markdown chapters | Glob for `NN-*.md`, `ch*.md`, `chapter-*.md` patterns | High |
| README presence | Check for `README.md`, `readme.*` | Medium |
| Code/text ratio | Count code blocks vs prose in sampled files | Medium |
| Directory depth | `find -type d -maxdepth 3 | wc -l` | Low |

**Classification rules:**

| Type | Criteria | Example |
|------|----------|---------|
| `software-project` | Source code files > 5 OR package manifest exists AND code/text ratio > 20% | React app, CLI tool, library |
| `document-report` | Continuous markdown chapters exist AND source code files < 3 AND code/text ratio < 10% | Research paper, playbook, study guide |
| `mixed` | Both source code and document chapters present, or ambiguous signals | Tutorial repo with extensive docs, literate programming |

### 2. Input Scope Measurement

**For software projects:**

```
Metrics:
- file_count: find -type f | wc -l
- source_files: find -name "*.py" -o -name "*.ts" ... | wc -l
- total_lines: find -name "*.py" ... -exec cat {} + | wc -l
- directory_count: find -type d | wc -l
- module_count: count top-level directories under src/ or lib/
```

**For documents/reports:**

```
Metrics:
- chapter_count: count markdown files matching chapter pattern
- total_lines: cat chapters/*.md | wc -l
- avg_per_chapter: total_lines / chapter_count
- has_statistics: grep -c '%' or '[0-9]%' pattern
- has_case_studies: grep -ci 'case study\|案例'
- has_code_blocks: grep -c '```' in source files
- has_quotes: grep -c '>' blockquote markers
```

### 3. Content Structure Analysis

**What to look for:**

| Dimension | Detection | Implication |
|-----------|-----------|-------------|
| Hierarchical sections | Multiple `##` and `###` headers | Deep structure, preserve hierarchy |
| Data tables | `\|` pipe-delimited rows | Statistical content, preserve data |
| Code blocks | Triple backtick fences | Technical content, may need manifest |
| Block quotes | `>` markers | Citations/quotes, preserve faithfully |
| Lists (ordered/unordered) | Numbered or bulleted items | Actionable content, preserve structure |
| Cross-references | Links between sections | Connected content, preserve links |

### 4. Technical Density Assessment

| Level | Criteria | Impact on output |
|-------|----------|-----------------|
| Low | < 5% code, mostly prose and data | Skip manifest, focus on content preservation |
| Medium | 5-20% code, mix of technical and narrative | Optional manifest, selective code verification |
| High | > 20% code, API-heavy | Required manifest, full verification |

## Output Format

Analysis results are saved to `analysis.md` in the output directory.

### YAML Front Matter

```yaml
---
content_type: software-project  # software-project | document-report | mixed
input_scope:
  source_files: 47              # or chapter_count for documents
  total_lines: 5123
  directory_count: 12           # or 0 for documents
content_structure:
  has_statistics: true
  has_case_studies: true
  has_code: true
  has_quotes: true
  hierarchy_depth: 3            # max heading depth
technical_density: high         # low | medium | high
recommended:
  scope: full                   # full | focused | overview
  chapters: 15                  # recommended chapter count
  depth: detailed               # detailed | standard | summary
  manifest: required            # required | optional | skip
  enrichment:                   # what to include
    quiz: true
    cross_references: true
    critical_assessment: true
    architecture_diagrams: true
detected_language: zh
---
```

### Analysis Body

```markdown
# Content Analysis

## Detected Type: [type]

**Evidence:**
- [signal 1]: [value] → [implication]
- [signal 2]: [value] → [implication]
- ...

## Input Scope

| Metric | Value |
|--------|-------|
| [metric] | [value] |

## Recommended Output

Based on [content type] with [scope] scope:

- **Chapters**: [N] — [rationale]
- **Depth per chapter**: [level] — [rationale]
- **Manifest**: [strictness] — [rationale]
- **Enrichment**: [what and why]
```

## Scope Recommendation Heuristics

### Software projects

| Input size | Recommended scope | Chapters | Depth |
|------------|-------------------|----------|-------|
| Small (< 20 files, < 1000 lines) | overview | 5-8 | standard |
| Medium (20-100 files, 1K-10K lines) | focused | 10-15 | detailed |
| Large (100-500 files, 10K-50K lines) | full | 15-25 | detailed |
| Massive (500+ files, 50K+ lines) | full | 20-30+ | detailed |

### Documents/reports

| Input size | Recommended scope | Chapters | Depth |
|------------|-------------------|----------|-------|
| Short (< 5 chapters, < 500 lines) | full | = input chapters | standard |
| Medium (5-15 chapters, 500-3000 lines) | full | = input chapters | detailed |
| Long (15-30 chapters, 3000-10000 lines) | full | = input chapters | detailed |
| Massive (30+ chapters, 10000+ lines) | focused | select top 20-25 | detailed |

**Key principle for documents**: Default to 1:1 chapter preservation. Only consolidate when input exceeds 30 chapters. The user makes the final decision via confirmation gate.

## Analysis Checklist

- [ ] Content type detected with at least 2 supporting signals
- [ ] Input scope measured (file count or chapter count + total lines)
- [ ] Content structure analyzed (data types present)
- [ ] Technical density assessed
- [ ] Scope recommendation generated with rationale
- [ ] analysis.md saved to output directory
