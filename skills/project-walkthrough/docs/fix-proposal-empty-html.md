# Fix Proposal v3 (Final): Prevent Empty HTML + Delivery Quality Gates

**Bug:** v1.5.0 produced walkthrough HTML with empty chapter sections — 11 nav items, only quiz had content.

**Root cause:** Phase 4 requires inline HTML via Write tool with DOM API (no innerHTML). Impractical for rich content. Model silently dropped chapter content.

**Fix strategy:** Make `md_to_html.py` the canonical HTML generator for ALL depth levels. Upgrade it from a deep-mode-only utility to a general-purpose converter with i18n, quiz support, robust parsing, and automated verification.

**Design principle:** Content decisions happen in Phase 3 (markdown). Phase 4 is mechanical conversion. Phase 5 is automated verification with a fix-retry loop before delivery. **No output is delivered to the user without passing programmatic quality gates.**

**Reviewed by 5 independent reviewers** — see review findings at end of document.

---

## Change 1: SKILL.md — Phase 4 rewrite

**File:** `skills/project-walkthrough/SKILL.md` (lines 542-582)

Replace Phase 4 content with:

```markdown
### Phase 4: Generate HTML (~30% of time)

1. One self-contained HTML file per depth level
2. Follow the structure in `../../docs/html-reference.md`

**CRITICAL — Converter-first generation (all depths):**

3. Run the converter tool as the primary HTML generation method:
   ```
   python scripts/md_to_html.py <docs_dir> <output.html> \
     --title "Project Name" --accent "#hex" --lang <lang> --quiz-chapter <N>
   ```
   - `docs_dir`: directory with markdown chapters
     - Brief: `docs/`  |  Medium: `docs/medium/`  |  Deep: `docs/deep/`
   - `--lang <lang>`: one of zh, zh-pure, en, bilingual (matches Phase 0 choice)
   - `--quiz-chapter <N>`: 1-based index of the chapter containing quiz questions.
     The converter extracts the `## Quiz` section from that chapter and renders it
     as an interactive quiz. The quiz section is removed from the chapter's regular
     content to avoid duplication. If no chapter contains a quiz, omit this flag.
   - The script reads ALL .md files, converts every element to styled HTML
   - Output is self-contained interactive HTML with sidebar nav, dark/light toggle,
     mobile responsive, print-friendly, interactive quiz section
   - Content parity: every element from the markdown is preserved

4. Verify the output:
   ```
   python scripts/md_to_html.py --verify <output.html> --source-dir <docs_dir>
   ```
   - Checks: section count = file count, per-section content, file size >= 80% of markdown,
     no broken .md links, nav items match sections, quiz section present (if --quiz-chapter used)
   - If verification FAILS → see Phase 5 error recovery loop

5. NO manual fallback. Python is a hard requirement for HTML generation.
   If Python is unavailable, report the error and skip HTML generation
   (markdown output is still complete and usable).

**Depth-specific content strategy (applied in Phase 3, not Phase 4):**

- **Brief and Medium:** Phase 3 markdown is already curated (key takeaways, summaries).
  The converter preserves this curation exactly.
- **Deep:** Phase 3 markdown is full content. The converter preserves everything (zero trimming).

Phase 4 does NOT modify content — it converts what Phase 3 produced.
```

## Change 2: SKILL.md — Phase 5 rewrite with delivery quality gates

**File:** `skills/project-walkthrough/SKILL.md` (lines ~583-594, ~658-680)

Replace Phase 5 content and the HTML checklist with:

```markdown
### Phase 5: Verify & Deliver (~5% of time)

**This phase is a hard delivery gate. No output reaches the user without passing all checks.**

#### Step 1: Automated structural verification (MANDATORY)

Run converter verification:
```
python scripts/md_to_html.py --verify <output.html> --source-dir <docs_dir>
```

This checks:
1. **Section count** = number of .md files in source dir
2. **Per-section content**: each chapter div has at least one heading (h1-h4) AND one content element (p/pre/table/ul/ol/blockquote/details)
3. **File size ratio**: HTML >= 80% of total markdown size
4. **No broken .md links**: zero `href="*.md"` in HTML
5. **Navigation integrity**: sidebar item count = chapter count
6. **Quiz present**: quiz section exists if `--quiz-chapter` was used

#### Step 2: Automated content verification

Run these additional programmatic checks:
```bash
# No .md href links (belt-and-suspenders with verify check #4)
grep -c 'href="[^"]*\.md"' <output.html>  # must be 0

# Count code blocks — should match manifest code_example count
grep -c '<pre><code>' <output.html>

# File count in docs/ matches expectations
ls <docs_dir>/*.md | wc -l
```

Cross-check against sources-manifest.json:
- Every code block in HTML has a corresponding code_example entry in manifest
- Every manifest entry's source file exists and line range is valid
- Spot-check 3+ entries for content accuracy

#### Step 3: Error recovery loop (max 3 retries)

If --verify fails, read the SPECIFIC error output and take the corresponding action:

| Error message pattern | Action |
|----------------------|--------|
| "Section count X != expected Y" | Check if all .md files were generated in Phase 3. Re-generate missing ones. |
| "Chapter N is empty" | Re-read the corresponding .md file. If it has content, this is a converter bug — report to user. If empty, re-generate that chapter in Phase 3. |
| "HTML size Xb is Y% of markdown" | Compare HTML sections to markdown files to identify which chapters lost content. Re-examine those .md files for unsupported markdown syntax. |
| "Found N broken .md links" | Re-run converter (safety net should strip these). If residual, manually remove. |
| "Nav items X != section count Y" | Re-run converter. If persistent, check for malformed chapter HTML that breaks the regex. |
| "Quiz section expected but not found" | Verify the quiz chapter index is correct and the chapter contains a ## Quiz section. |

After each fix attempt, re-run --verify from Step 1.

If 3 retries exhausted:
- STOP. Do NOT deliver HTML.
- Report ALL specific error messages to the user with diagnostic details.
- Deliver markdown output (always complete and usable).
- Provide the exact converter command for the user to run manually.

#### Step 4: Delivery gate (FINAL CHECKPOINT)

Do NOT claim completion or deliver HTML until ALL of these pass:

**Automated checks (programmatic):**
- [ ] `--verify` passes with exit code 0
- [ ] `grep -c 'href="[^"]*\.md"' <html>` returns 0
- [ ] sources-manifest.json exists for each depth level
- [ ] Every code block has a code_example entry in manifest

**Model-verified checks (LLM reads output):**
- [ ] Spot-check 2-3 chapters for content completeness (not just headings)
- [ ] No placeholder or TODO content remaining
- [ ] Quiz answers are correct (if quiz exists)

**Report to user:**
```
Walkthrough Generation Complete
================================
Output: <output_directory>
├─ Markdown: <N> chapters in docs/
├─ HTML: walkthrough-<project>-<depth>-<timestamp>.html
├─ Manifest: sources-manifest.json (<M> verified claims)
└─ Verification: PASSED (all gates)

Quality metrics:
├─ Chapters: <N> (expected: <N>)
├─ HTML size: <X>KB (markdown: <Y>KB, ratio: <Z>%)
├─ Code blocks: <C> (manifest entries: <M>)
├─ Quiz: <Q> questions
└─ Broken links: 0
```

If any gate failed:
```
Walkthrough Generation PARTIALLY COMPLETE
==========================================
Markdown output: COMPLETE (<N> chapters)
HTML output: FAILED — <specific error messages>

The markdown files in docs/ are complete and usable.
To generate HTML manually:
  python scripts/md_to_html.py <docs_dir> output.html --title "..." --lang zh
```
```

## Change 3: md_to_html.py — Major upgrade

**File:** `scripts/md_to_html.py`

### 3a. Fix parsing defects + security hardening

```python
def sanitize_url(url):
    """Block javascript:, data:, vbscript: URLs to prevent XSS."""
    scheme = re.match(r'^([a-zA-Z][a-zA-Z0-9+.-]*):', url.strip())
    if scheme and scheme.group(1).lower() not in ('http', 'https', 'mailto', 'tel', ''):
        return '#'
    return url

def preprocess_md(text):
    """Strip HTML comments and normalize markdown before conversion."""
    # Remove HTML comments (<!-- ... -->)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text

def process_inline(text):
    text = escape_html(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Images: ![alt](url) -> <img> (must come before links)
    def img_repl(m):
        return f'<img src="{sanitize_url(m.group(2))}" alt="{m.group(1)}" style="max-width:100%">'
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', img_repl, text)
    # Links: [text](url)
    def link_repl(m):
        return f'<a href="{sanitize_url(m.group(2))}">{m.group(1)}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, text)
    return text

# In parse_table(), protect pipe-in-inline-code before splitting:
def parse_table(lines):
    if len(lines) < 2:
        return ""
    code_store = []
    def mask_code(m):
        code_store.append(m.group(0))
        return f"__CODE{len(code_store)-1}__"
    masked = [re.sub(r'`[^`]+`', mask_code, line) for line in lines]
    def row(l):
        return [re.sub(r'__CODE(\d+)__', lambda m: code_store[int(m.group(1))],
                        c.strip()) for c in l.strip().strip("|").split("|")]
    # ... rest of parse_table unchanged ...

# In the <details> passthrough code path, sanitize body content:
# Replace raw passthrough with tag-preserving sanitization:
elif s.startswith("<details"):
    d = []
    while i < len(lines):
        line = lines[i]
        # Sanitize content between <summary>...</summary> and </details>
        # but preserve the <details>/<summary> tags themselves
        if not (line.strip().startswith("<details") or
                line.strip().startswith("</details") or
                line.strip().startswith("<summary") or
                line.strip().startswith("</summary")):
            line = escape_html(line)  # sanitize body content
        d.append(line)
        if "</details>" in lines[i]: i += 1; break
        i += 1
    out.append('\n'.join(d))
```

### 3b. Add --lang flag with i18n

```python
I18N = {
    "zh": {
        "lang": "zh-CN", "chapters": "章节",
        "prev": "&larr; 上一章", "next": "下一章 &rarr;",
        "theme_dark": "☀", "theme_light": "☾",
        "nav_skip": r'\[[^\]]*(?:上一章|下一章|返回目录)[^\]]*\]\([^\)]+\.md\)',
    },
    "zh-pure": {
        "lang": "zh-CN", "chapters": "章节",
        "prev": "&larr; 上一章", "next": "下一章 &rarr;",
        "theme_dark": "☀", "theme_light": "☾",
        "nav_skip": r'\[[^\]]*(?:上一章|下一章|返回目录)[^\]]*\]\([^\)]+\.md\)',
    },
    "en": {
        "lang": "en", "chapters": "Chapters",
        "prev": "&larr; Previous", "next": "Next &rarr;",
        "theme_dark": "☀", "theme_light": "☾",
        "nav_skip": r'\[[^\]]*(?:Previous|Prev|Next|Back to|Continue|Table of Contents|Home)[^\]]*\]\([^\)]+\.md\)',
    },
    "bilingual": {
        "lang": "zh-CN", "chapters": "Chapters / 章节",
        "prev": "&larr; Prev / 上一章", "next": "Next / 下一章 &rarr;",
        "theme_dark": "☀", "theme_light": "☾",
        "nav_skip": r'\[[^\]]*(?:上一章|下一章|返回目录|Previous|Prev|Next|Back to|Continue)[^\]]*\]\([^\)]+\.md\)',
    },
}
```

### 3c. Add --quiz-chapter flag

**Design decision:** Use `--quiz-chapter <N>` (1-based index) instead of `--quiz <file>`.
The converter detects `## Quiz` heading in the specified chapter, extracts quiz content,
renders it as interactive quiz section, and removes it from the regular chapter content.

**Canonical quiz markdown format** (defined in SKILL.md Phase 3B):

```markdown
## Quiz

**Q1:** Question text?
- A. Option A
- B. Option B
- C. Option C
- D. Option D

**Answer: B**

**Explanation:** Because of X, Y, Z.

---

**Q2:** Next question?
- A. ...
```

For bilingual mode, questions contain both languages:
```markdown
**Q1:** Chinese question?
English question?
- A. Option
```

The `parse_quiz_md()` function extracts `{q, o: [...], c: int, e: str}` structs.
The `build_quiz_js()` function generates a `<script>` block with `quizData` JS array
and DOM-based quiz rendering. Inside `<script>` tags in a self-contained HTML file,
`innerHTML` is safe (static build-time content, no user input) and is allowed for
implementation simplicity.

```python
def parse_quiz_md(md_text):
    """Parse quiz section from markdown into quizData structure."""
    questions = []
    # Split on **Q\d+:** or **Q\d+：** patterns
    # Extract question text, options (A-D list items), answer letter, explanation
    # For bilingual: combine both language paragraphs in q and e fields with <br>
    return questions

def build_quiz_section(questions, lang_strings):
    """Generate quiz chapter div with interactive quiz JS."""
    if not questions:
        return ""  # No quiz if 0 questions
    # Generate quizData JS variable
    # Generate DOM-based quiz rendering (createElement, textContent, addEventListener)
    # Returns HTML string for the quiz chapter div
    pass
```

### 3d. Add --verify with --source-dir

```python
def verify_html(html_path, source_dir=None, quiz_expected=False):
    """Post-build validation with per-section checks and relative size metric."""
    content = Path(html_path).read_text("utf-8")
    file_size = Path(html_path).stat().st_size
    errors = []

    # Determine expected chapter count from source dir
    if source_dir:
        md_files = sorted(Path(source_dir).glob("*.md"))
        expected = len(md_files)
        total_md_size = sum(f.stat().st_size for f in md_files)
    else:
        expected = 0
        total_md_size = 0

    # 1. Section count (exact match)
    section_count = content.count('class="chapter"')
    if expected > 0 and section_count != expected:
        errors.append(f"Section count {section_count} != expected {expected} "
                     f"(.md files in {source_dir})")

    # 2. Per-section content check (CRITICAL -- prevents the empty-section bug)
    chapter_pattern = re.compile(
        r'<div class="chapter"[^>]*>(.*?)</div>\s*(?=<div class="chapter"|</main>)',
        re.DOTALL
    )
    chapters = chapter_pattern.findall(content)
    for i, ch in enumerate(chapters):
        has_heading = bool(re.search(r'<h[1-4][> ]', ch))
        has_content = bool(re.search(r'<(p|pre|table|ul|ol|blockquote|details)[> ]', ch))
        if not has_heading and not has_content:
            errors.append(f"Chapter {i+1} is empty (no heading or content element found)")

    # 3. Relative file size (>= 80% of markdown total)
    if total_md_size > 0:
        ratio = file_size / total_md_size
        if ratio < 0.80:
            errors.append(f"HTML size {file_size:,}b is {ratio:.0%} of markdown "
                         f"({total_md_size:,}b), below 80% threshold")

    # 4. No broken .md links
    md_links = re.findall(r'href="[^"]*\.md"', content)
    if md_links:
        errors.append(f"Found {len(md_links)} broken .md links: {md_links[:3]}")

    # 5. Navigation consistency
    nav_count = len(re.findall(r'onclick="showChapter\(\d+\)"', content))
    if expected > 0 and nav_count != expected:
        errors.append(f"Nav items {nav_count} != section count {expected}")

    # 6. Quiz section (if expected)
    if quiz_expected:
        has_quiz = 'quizData' in content or 'class="quiz' in content
        if not has_quiz:
            errors.append("Quiz section expected (--quiz-chapter used) but not found in HTML")

    return errors
```

Argparse additions:
```python
p.add_argument("--lang", default="zh", choices=["zh", "zh-pure", "en", "bilingual"])
p.add_argument("--quiz-chapter", type=int, default=None,
               help="1-based index of chapter containing ## Quiz section")
p.add_argument("--verify", metavar="HTML_FILE", help="Verify instead of generate")
p.add_argument("--source-dir", default=None,
               help="Source markdown dir for --verify (enables section count + size checks)")
```

## Change 4: SKILL.md — Define canonical quiz markdown format

**File:** `skills/project-walkthrough/SKILL.md` (add to Phase 3B section)

```markdown
#### Quiz chapter format

The last numbered chapter in each depth level MUST include a quiz section. The quiz follows this exact format:

```markdown
## Quiz

**Q1:** Question text here?
- A. First option
- B. Second option
- C. Third option
- D. Fourth option

**Answer: B**

**Explanation:** Explanation of why B is correct and others are wrong.

---

**Q2:** Next question?
- A. ...
- B. ...
- C. ...
- D. ...

**Answer: A**

**Explanation:** ...
```

Rules:
- Questions use `**Q<N>:**` bold prefix (not headings)
- Options are unordered list items with `A.` / `B.` / `C.` / `D.` prefix
- Answer line: `**Answer: <LETTER>**` on its own paragraph
- Explanation: `**Explanation:** <text>` on its own paragraph
- Questions separated by `---` horizontal rules
- For bilingual mode: question text and explanation contain both languages sequentially
  (Chinese paragraph, then English paragraph, both before the options)

Question counts by depth: Brief 5-7, Medium 10-12, Deep 15-20.
```

## Change 5: html-reference.md — Update to match converter output

**File:** `docs/html-reference.md`

### 5a. Add Generation Strategy section (after File Requirements)

```markdown
## Generation Strategy

The converter tool (`scripts/md_to_html.py`) is the canonical HTML generation method for ALL depth levels.

**Converter command:**
```bash
python scripts/md_to_html.py <docs_dir> <output.html> \
  --title "Title" --accent "#hex" --lang zh --quiz-chapter 6
```

**Converter output structure:**
- Chapters: `<div class="chapter">` with `showChapter(N)` JS navigation
- Sidebar: `<nav class="sidebar">` with `<a onclick="showChapter(N)">` links
- Theme: dark/light toggle via `data-theme` attribute on `<html>`
- Quiz: interactive quiz section with `quizData` JS array and DOM-based rendering
- CSS: inline `:root` / `[data-theme="dark"]` rules (no CSS variables)

**Why converter-first:**
- The security hook blocks innerHTML in Write tool calls
- DOM API generation is 3-5x more verbose and error-prone
- Manual generation caused silent content omission bugs (empty sections)
- The converter has built-in XSS protection (URL sanitization, HTML escaping)

**Python is required for HTML output.** If Python is unavailable, markdown output is the deliverable.
```

### 5b. Update DOM API Rules and content density sections

Replace the innerHTML warning and soft density guidance with:

```markdown
## Security (for converter developers)

The converter applies these protections automatically:
- HTML escaping of all user content (prevents XSS)
- URL protocol filtering (blocks javascript:, data: URLs)
- HTML comment stripping (prevents hidden content)
- `<details>` body sanitization (prevents script injection)

## Content Density Gate (HARD REQUIREMENT)

After generating HTML, verification is MANDATORY:
```bash
python scripts/md_to_html.py --verify <output.html> --source-dir <docs_dir>
```

Checks per-section (each chapter individually):
- Has at least one heading AND one content element
- File size >= 80% of total markdown size
- Section count = .md file count (exact)
- Zero broken .md links
- Navigation = chapters (exact)

**If any check fails, the HTML is NOT deliverable.** See Phase 5 error recovery.
```

## Change 6: CI test expansion

**File:** `tests/test_walkthrough_output.py`

Add a new test class `TestConverter` (separate from `TestHTML` which tests fixtures):

```python
class TestConverter:
    """Tests for md_to_html.py converter and --verify flag."""

    def test_basic_conversion_and_verify(self): ...
    def test_strips_html_comments(self): ...
    def test_converts_images(self): ...
    def test_handles_pipe_in_code_tables(self): ...
    def test_lang_zh_output(self): ...
    def test_lang_en_output(self): ...
    def test_lang_bilingual_output(self): ...
    def test_quiz_generation(self): ...
    def test_verify_detects_empty_section(self): ...
    def test_verify_detects_section_count_mismatch(self): ...
    def test_verify_detects_small_file_size(self): ...
    def test_verify_detects_md_links(self): ...
    def test_sanitizes_javascript_urls(self): ...
```

## Change 7: Migration plan

**Fixture regeneration commands:**
```bash
# For each fixture project:
python scripts/md_to_html.py tests/fixtures/<project>/docs \
  tests/fixtures/<project>/interactive/walkthrough.html \
  --title "<Project>" --lang zh --quiz-chapter <N>
```

**Test updates required:**
- `test_html_has_expandable_sections`: Change assertion to check for `<details>` elements
  instead of "expandable" CSS class (converter maps expandables to `<details>`)
- `test_html_has_quiz`: Update to check for `quizData` JS variable
- `test_html_no_innerhtml`: Remove `xfail` markers — converter output has no innerHTML
- `test_html_content_density`: Update to check `class="chapter"` instead of `el('div','section')`
- Regenerate all 3 fixture HTML files + 20 example HTML files

---

## Implementation Order

```
Phase A (safe foundation):
  1. Change 3a — parsing fixes + security hardening
  2. Change 3d — --verify upgrade with per-section checks
  3. Change 6 — CI test expansion (happy path + failure cases)

Phase B (new features):
  4. Change 3b — --lang i18n
  5. Change 3c — --quiz-chapter (single commit with 3b)
  6. Change 4 — quiz format definition in SKILL.md

Phase C (behavioral change):
  7. Change 1 — Phase 4 rewrite (converter-first for all depths)
  8. Change 2 — Phase 5 delivery quality gates
  9. Change 5 — html-reference.md alignment

Phase D (migration):
  10. Change 7 — regenerate fixtures, update tests
```

---

## Summary of changes

| # | File | Change | Risk |
|---|------|--------|------|
| 1 | SKILL.md Phase 4 | Converter-first for all depths | Medium |
| 2 | SKILL.md Phase 5 | Delivery quality gates with error recovery | Low |
| 3a | md_to_html.py | Parsing fixes + XSS protection | Low |
| 3b | md_to_html.py | --lang i18n (4 modes) | Medium |
| 3c | md_to_html.py | --quiz-chapter for interactive quiz | Medium |
| 3d | md_to_html.py | --verify with per-section + relative size checks | Low |
| 4 | SKILL.md Phase 3B | Canonical quiz markdown format definition | Low |
| 5 | html-reference.md | Generation strategy + security + density gate | Low |
| 6 | test_walkthrough_output.py | 13 new converter/verify tests | Low |
| 7 | fixtures + examples | Regenerate HTML, update test expectations | Medium |

## What this prevents

1. Empty HTML sections — converter + per-section verify
2. Silent content omission — individual chapter checks
3. innerHTML conflict — converter bypasses entirely
4. Language mismatch — --lang for all 4 modes
5. Missing quizzes --quiz-chapter extraction
6. XSS from markdown content — URL sanitization + HTML escaping + details sanitization
7. Unverified delivery — Phase 5 delivery gate with quality metrics report
8. Infinite retry loops — max 3 retries with diagnostic escalation

---

## Appendix: Review Findings (5 rounds)

### Round 1 (Architecture) — PASS with changes
- Converter output must align with html-reference.md or vice versa
- Per-section content validation needed in verify
- Relative file-size metric (80% of markdown) not fixed per-chapter
- Fallback path still had original bug (removed in v3)

### Round 2 (Robustness) — BLOCK resolved
- Parsing defects: HTML comments, images, nested lists, pipe-in-code (fixed in 3a)
- No i18n (fixed in 3b)
- No quiz generation (fixed in 3c)
- No error recovery loop (fixed in Change 2)

### Round 3 (i18n + Quiz) — BLOCK resolved
- Quiz format undefined (fixed in Change 4)
- --quiz semantics unclear (changed to --quiz-chapter <index>)
- Theme toggle labels missing from i18n (added to I18N dict)
- English nav_skip too narrow (expanded regex)

### Round 4 (Test + CI) — BLOCK resolved
- 2 tests will break: expandable + quiz (migration plan in Change 7)
- Test coverage insufficient (13 new tests in Change 6)
- Migration plan incomplete (Change 7 has concrete commands)

### Round 5 (Security + Open-Source) — APPROVE WITH CHANGES
- XSS: javascript: URLs pass through (fixed in 3a with sanitize_url)
- XSS: <details> passthrough allows <script> (fixed in 3a with body sanitization)
- No migration guide for external users (added to html-reference.md 5a)
- Error messages need actual values (added specific counts to verify output)
