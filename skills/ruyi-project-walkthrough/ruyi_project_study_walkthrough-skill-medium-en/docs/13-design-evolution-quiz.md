# Design Evolution & Lessons Learned

The project-walkthrough-skill went through 12 rounds of accuracy verification and 7 version releases in roughly two weeks. This chapter traces the major design decisions, the most critical bug, and what we learned along the way.

## Version Timeline

The project evolved rapidly from a basic concept to a production-quality tool:

| Version | Date | Theme |
|---------|------|-------|
| 1.0.0 | 2026-05-09 | Manifest-first accuracy, import graph, 185 tests |
| 1.1.0 | 2026-05-20 | Adaptive scope, multi-platform, document support |
| 1.2.0 | 2026-05-20 | AGENTS.md, GitHub Actions CI |
| 1.2.1 | 2026-05-20 | CI timeout fix, LICENSE, issue templates |
| 1.3.0 | 2026-05-20 | Release automation script |
| 1.4.0 | 2026-05-20 | 4 language modes (--lang), --version flag |
| 1.5.0 | 2026-05-20 | Deep HTML full-content conversion, file size gate |
| 1.6.0 | 2026-05-22 | Converter-first HTML, i18n in converter, quiz, XSS protection |
| 1.6.1 | 2026-05-22 | verify-result.json, delivery gate hardening |

The CHANGELOG follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format with Added/Changed/Fixed/Docs sections.

```text
// Simplified from: CHANGELOG.md:1-9
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.6.1] - 2026-05-22
```

## The 16-Hour Sprint: v1.0.0 → v1.2.1

The dev log from 2026-05-19 to 2026-05-20 records an intense development session:

- 25 non-merge commits across 15 PRs
- +3,161 / -135 lines of code changes
- 185 → 309 tests (+124 new tests)
- 4 version releases

This sprint introduced the three most important architectural additions:

1. **Adaptive scope system** (Phase 0) — solved the problem of data loss when processing large documents. A 19-chapter research report that was being crushed to 10 chapters now gets 1:1 chapter preservation.

2. **Multi-platform compatibility** — Cursor, Windsurf, OpenCode, and Gemini CLI all get platform-specific files generated from a single SKILL.md source.

3. **Automated toolchain** — `convert.sh` for platform generation, `release.sh` for version management, Makefile for standard commands.

```text
// Simplified from: docs/dev-log-20260519-20260520.md:10-17
| 指标 | 数据 |
|------|------|
| 提交数 | 25 个非合并提交 |
| PR 数 | 15 个（#2 ~ #16），全部合并到 master |
| 新增文件 | 19 个 |
| 修改文件 | 12 个 |
| 代码变更 | +3,161 / -135 行 |
| 测试数 | 185 → 309（+124 个新测试） |
```

## The Empty HTML Bug: A Case Study

The most critical bug in the project's history was the **empty HTML sections** issue discovered in v1.5.0.

### What Happened

When generating a walkthrough, the output HTML had 11 navigation items in the sidebar — but only the quiz section had any visible content. All chapter sections were empty.

### Root Cause

Phase 4 required generating inline HTML using the DOM API (`createElement`, `textContent`) — no `innerHTML` allowed. This was a deliberate security choice to prevent XSS. But for rich walkthrough content (paragraphs, code blocks, tables, blockquotes, expandable sections), manually constructing DOM elements via `createElement` calls was impractical at scale. The model silently dropped chapter content rather than attempt the massive DOM construction.

### The Fix: Converter-First HTML

The solution was a fundamental architectural shift documented in `docs/fix-proposal-empty-html.md`:

```text
// Simplified from: docs/fix-proposal-empty-html.md:1-9
# Fix Proposal v3 (Final): Prevent Empty HTML + Delivery Quality Gates

**Bug:** v1.5.0 produced walkthrough HTML with empty chapter sections
**Root cause:** Phase 4 requires inline HTML via Write tool with DOM API (no innerHTML).
              Impractical for rich content. Model silently dropped chapter content.
**Fix strategy:** Make md_to_html.py the canonical HTML generator for ALL depth levels.
```

Instead of the model manually constructing HTML, `md_to_html.py` became the single HTML generation engine. The Python script reads markdown files, converts every element to styled HTML, and produces a self-contained interactive page. Phase 4 went from "model writes HTML" to "model runs a script."

This fix introduced:
- **Converter-first generation** — all depths use `md_to_html.py`
- **Automated verification** — `--verify` flag checks section count, content density, broken links
- **Delivery quality gates** — Phase 5 is now a hard gate with `verify-result.json` as evidence
- **3-retry error recovery** — automated fixes for common failures before reporting to user

### What We Learned

1. **Security constraints can cause silent failures.** The innerHTML ban was correct for security, but the alternative (manual DOM construction) was impractical. The fix preserved security while moving complexity to a script.

2. **Content parity is a hard requirement.** The 80% file-size gate ensures HTML preserves markdown content. A 30K HTML from 160K markdown is a sign something was silently dropped.

3. **Automated verification prevents silent regressions.** The `verify-result.json` file is now the authoritative quality evidence. No output is delivered without it.

4. **Separation of concerns.** Phase 3 (markdown content) and Phase 4 (HTML conversion) are now cleanly separated. Phase 4 never modifies content — it only converts.

## Key Design Decisions

### Why `// Simplified from:` not `// Source:`

Early versions used `// Source: path:lines` for code citations. This caused accuracy problems because "source" implies character-for-character reproduction. But walkthrough code is always simplified — indentation changes, comments removed, surrounding context stripped. `Simplified from:` is always honest. This decision eliminated the most common accuracy issue in testing.

### Why Manifest-First (Not Manifest-After)

The original approach was to write content first, then build a manifest of claims. This led to fabricated claims being written before they could be caught. The manifest-first approach (Phase 3A → Phase 3B) structurally prevents this: you cannot write a claim that isn't in the manifest with `verified: true`.

### Why Six Locations for Version Numbers

Plugin metadata (`plugin.json`), marketplace registration (`marketplace.json`), README badge, CHANGELOG header, SKILL.md frontmatter, and `--version` output text. Six places that must stay in sync. The `release.sh` script automates this — editing one source (`SKILL.md` frontmatter) propagates to all six. Manual editing of any location except the source is forbidden.

### Why Multi-Platform from Day One

Different AI coding tools use different skill/rule formats. Rather than maintaining separate copies, the project uses `convert.sh` to generate platform-specific files from the canonical `SKILL.md`. This ensures all platforms get the same content and updates.

## Quiz

**Q1:** What was the root cause of the empty HTML sections bug in v1.5.0?
- A. The markdown files were empty
- B. The DOM API approach for rich content was impractical, causing silent content drops
- C. The quiz parser was consuming all chapter content
- D. The sidebar navigation was hiding chapter content

**Answer: B**

**Explanation:** Phase 4 required manual DOM API construction (createElement, textContent) without innerHTML. For rich walkthrough content at scale, this was impractical, and the model silently dropped chapter content. The fix was to use Python's md_to_html.py as the canonical converter.

---

**Q2:** Why was `// Simplified from:` chosen over `// Source:` for code citations?
- A. It's shorter to type
- B. "Source" implies exact reproduction, but walkthrough code is always simplified
- C. The parser only supports "Simplified from:" syntax
- D. It matches the markdown standard

**Answer: B**

**Explanation:** "Source" implies character-for-character accuracy, which is impractical for walkthroughs where code is always simplified (indentation changed, comments removed, context stripped). "Simplified from:" is always honest and eliminated the most common accuracy issue.

---

**Q3:** How many locations must version numbers stay synchronized across?
- A. 2
- B. 4
- C. 6
- D. 8

**Answer: C**

**Explanation:** Six locations: SKILL.md frontmatter (source of truth), SKILL.md --version text, plugin.json, marketplace.json, README badge, and CHANGELOG header. The release.sh script automates synchronization from the single source.

---

**Q4:** What does the manifest-first approach (Phase 3A → 3B) prevent?
- A. Slow HTML generation
- B. Fabricated claims being written before verification
- C. Quiz questions with wrong answers
- D. Version number mismatches

**Answer: B**

**Explanation:** By requiring all claims to be verified and recorded in sources-manifest.json before any chapter content is written, the manifest-first approach structurally prevents unverified or fabricated claims from appearing in the walkthrough.

---

**Q5:** What is the file size gate for deep-mode HTML?
- A. HTML must be exactly equal to markdown size
- B. HTML must be at least 50% of markdown size
- C. HTML must be at least 80% of markdown size
- D. There is no file size requirement

**Answer: C**

**Explanation:** Deep-mode HTML must be >= 80% of total markdown size. A significantly smaller HTML indicates content was silently dropped during conversion. This gate catches regressions like the empty HTML bug.

---

**Q6:** How many language modes does `--lang` support?
- A. 1 (Chinese only)
- B. 2 (Chinese and English)
- C. 4 (zh, zh-pure, en, bilingual)
- D. 6 (including Japanese and Korean)

**Answer: C**

**Explanation:** Four language modes: `zh` (Chinese body + English technical terms, default), `zh-pure` (pure Chinese), `en` (pure English), and `bilingual` (side-by-side Chinese-English).

---

**Q7:** What file serves as the single source of truth for all platform adapters?
- A. README.md
- B. plugin.json
- C. skills/ruyi-project-walkthrough/SKILL.md
- D. convert.sh

**Answer: C**

**Explanation:** `skills/ruyi-project-walkthrough/SKILL.md` is the canonical source. `convert.sh` generates Cursor (.mdc), Windsurf (.md), and OpenCode (SKILL.md) files from it. Platform files should never be manually edited.

---

**Q8:** What does `verify-result.json` contain?
- A. Only a pass/fail boolean
- B. Section count, file size ratio, nav count, errors list, and UTC timestamp
- C. The full HTML content for comparison
- D. Test suite results

**Answer: B**

**Explanation:** `verify-result.json` contains `passed` (boolean), `section_count`, `expected_sections`, `html_size`, `markdown_size`, `ratio_pct`, `sidebar_nav_count`, `errors` (list), and `timestamp`. It is the authoritative evidence of HTML quality — no output is delivered without it.

---

**Q9:** What was the adaptive scope system designed to solve?
- A. Projects with too many test files
- B. Data loss when large documents were forced into too few chapters
- C. Slow HTML generation for deep mode
- D. Version number synchronization issues

**Answer: B**

**Explanation:** The adaptive scope system (Phase 0) was created when a 19-chapter research report was being compressed to 10 chapters, losing 67% of the data. The system analyzes input, recommends scope, and gets user confirmation before generation.

---

**Q10:** How many rounds of accuracy verification did the project undergo?
- A. 3
- B. 6
- C. 12
- D. 20

**Answer: C**

**Explanation:** The project went through 12 rounds of accuracy verification, with rounds 10-12 achieving consecutive zero issues. This iterative process established the manifest-first verification system.

---

[Previous: Quality Assurance & CI](12-quality-assurance-ci.md)
