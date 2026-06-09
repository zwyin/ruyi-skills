# Phase Pipeline: From Analysis to Delivery

The walkthrough generation follows a strict five-phase pipeline. Each phase has defined inputs, outputs, and quality gates. Understanding this pipeline is essential for anyone contributing to the project.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────┐
│ Phase 0: Analyze & Confirm                              │
│   Input:  Raw project directory                         │
│   Output: analysis.md + user-confirmed scope config     │
│   Gate:   User confirmation (unless --no-confirm)       │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Explore                                        │
│   Input:  Confirmed scope config                        │
│   Output: Project understanding (in-memory)             │
│   Gate:   None (quality depends on thoroughness)        │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Plan                                           │
│   Input:  Exploration results + scope config            │
│   Output: Chapter outline mapped to source files        │
│   Gate:   User review (if confirmed in Phase 0)         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Generate Markdown                              │
│   Input:  Chapter outline + verified claims             │
│   Output: sources-manifest.json + NN-*.md files         │
│   Gate:   Manifest completeness + line range audit      │
│   Sub-phases: 3A (verify) → 3B (write) → 3C (validate) │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Generate HTML                                  │
│   Input:  Markdown chapters directory                   │
│   Output: Self-contained interactive HTML               │
│   Tool:   python scripts/md_to_html.py                  │
│   Gate:   Automated verification (--verify)             │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 5: Verify & Deliver                               │
│   Input:  All generated files                           │
│   Output: verify-result.json + delivery report          │
│   Gate:   Hard delivery gate (PASSED required)          │
│   Recovery: 3-retry loop with targeted fixes            │
└─────────────────────────────────────────────────────────┘
```

## Phase 0: Analyze & Confirm (~5% of time)

This phase was added in v1.1.0 to solve the problem of data loss when large documents were forced into too few chapters.

**Phase 0.1 — Load Preferences:** Check for `.project-walkthrough/EXTEND.md` (project-level) or `~/.project-walkthrough/EXTEND.md` (user-level). Load saved defaults for scope, depth, and language.

**Phase 0.2 — Content Analysis:** Analyze the project's content type, scope (file count, line count), content structure, and technical density. Save results to `analysis.md`.

**Phase 0.3 — Confirmation Gate:** Present analysis to the user with interactive questions about scope, depth, format, and language. The `--depth` flag pre-selects recommended options.

```text
// Simplified from: skills/ruyi-project-walkthrough/SKILL.md:349-364
**Display to user:**
Content Analysis:
├─ Type: [software-project / document-report / mixed]
├─ Scope: [N files/chapters, X lines]
├─ Content: [statistics, case studies, code, etc.]
└─ Recommended: [scope] scope, [N] chapters, [depth] depth
```

Skip condition: `--no-confirm` flag or EXTEND.md with `confirm_scope: false`.

## Phase 1: Explore (~15% of time)

Read source files based on confirmed scope. The exploration protocol (defined in `docs/exploration-protocol.md`) guides the model through:

1. Identify project type (AI tool, Library, Web app, CLI tool, Document, Report)
2. Read core files (README, ARCHITECTURE, CLAUDE.md, package.json, configs)
3. Read key source files (entry points, core modules)
4. Extract 3-5 unique innovations or design decisions
5. Map component architecture

Exploration depth adapts to scope: full scope reads all files, focused reads key files + skims rest, overview reads core files only.

## Phase 2: Plan (~10% of time)

Plan chapters using templates from `docs/chapter-templates.md`. Chapter count comes from scope config, not fixed presets. Each chapter is mapped to source files that provide its content.

```text
// Simplified from: skills/ruyi-project-walkthrough/SKILL.md:457-469
1. Select chapter template based on content type
2. Determine chapter count from scope config
3. Adapt template to the specific project
4. Map each chapter to source files
5. Plan cross-references between chapters
```

If the user confirmed outline review in Phase 0, the chapter list is presented for approval before Phase 3.

## Phase 3: Generate Markdown (~40% of time)

The most complex phase, split into three gated sub-phases:

**Phase 3A — Verify & Build Manifest:** For each chapter, list all planned claims, read the actual source files, verify each claim, and create manifest entries. Unverifiable claims are dropped.

**Phase 3B — Write Chapter Content:** Using only verified claims from 3A, write the chapter markdown. Every code block must have a `// Simplified from: path:lines` citation.

**Phase 3C — Validate Coverage:** Read back each chapter, cross-check against manifest, audit line ranges, run `verify_sources.py`.

## Phase 4: Generate HTML (~30% of time)

Run the converter tool:

```bash
python scripts/md_to_html.py <docs_dir> <output.html> \
  --title "Project Name" --accent "#hex" --lang <lang> --quiz-chapter <N>
```

Then verify the output:

```bash
python scripts/md_to_html.py --verify <output.html> --source-dir <docs_dir>
```

No manual fallback. Python is a hard requirement. The converter handles all HTML generation including sidebar, theme toggle, quiz, and watermark.

## Phase 5: Verify & Deliver (~5% of time)

A hard delivery gate with four steps:

1. **Automated structural verification** — reads `verify-result.json` for section count, file size ratio, nav consistency
2. **Automated content verification** — checks broken links, code block count against manifest
3. **Error recovery loop** — up to 3 retries for fixable issues (empty sections, broken links)
4. **Delivery gate** — final checkpoint before reporting to user

No output is delivered without `verify-result.json` containing `"passed": true`.

## Time Distribution

The pipeline allocates time proportionally:

| Phase | Allocation | Purpose |
|-------|-----------|---------|
| Phase 0 | ~5% | Analysis + user confirmation |
| Phase 1 | ~15% | Source code exploration |
| Phase 2 | ~10% | Chapter planning |
| Phase 3 | ~40% | Markdown generation + verification |
| Phase 4 | ~30% | HTML conversion + verification |
| Phase 5 | ~5% | Final delivery checks |

[Previous: Architecture & Design](02-architecture-design-philosophy.md) | [Next: The Converter Engine](04-converter-engine.md)
