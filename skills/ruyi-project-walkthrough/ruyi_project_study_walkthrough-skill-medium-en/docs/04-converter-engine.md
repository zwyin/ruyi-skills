# The Converter Engine: md_to_html.py

The heart of HTML generation is `scripts/md_to_html.py` — a 643-line Python script that converts markdown chapter files into a single self-contained interactive HTML page. This chapter walks through its major subsystems.

## What It Does

Given a directory of numbered markdown files, `md_to_html.py` produces one HTML file that works when opened via `file://` with no server, no network, and no other files present. The output includes sidebar navigation, dark/light theme toggle, font size controls, interactive quiz, and a promo watermark page.

```text
// Simplified from: scripts/md_to_html.py:1-10
#!/usr/bin/env python3
"""
Convert markdown chapter files into a single self-contained interactive HTML.
Build tool for project-walkthrough all-depth conversion.

Usage:
    python md_to_html.py <docs_dir> <output_html> [--title "Title"] [--accent "#hex"]
                         [--lang zh|zh-pure|en|bilingual] [--quiz-chapter N]
    python md_to_html.py --verify <html_file> [--source-dir <docs_dir>]
"""
```

## i18n System

Four language modes are supported through the `I18N` dictionary:

```python
// Simplified from: scripts/md_to_html.py:20-53
I18N = {
    "zh": {
        "lang": "zh-CN", "chapters": "章节",
        "prev": "&larr; 上一章", "next": "下一章 &rarr;",
        "quiz_title": "知识测验",
    },
    "en": {
        "lang": "en", "chapters": "Chapters",
        "prev": "&larr; Previous", "next": "Next &rarr;",
        "quiz_title": "Quiz",
    },
    "bilingual": {
        "lang": "zh-CN", "chapters": "Chapters / 章节",
        "prev": "&larr; Prev / 上一章", "next": "Next / 下一章 &rarr;",
        "quiz_title": "Quiz / 知识测验",
    },
}
```

Each language mode defines sidebar labels, navigation button text, and regex patterns for skipping markdown navigation links.

## Markdown-to-HTML Conversion

The `convert_md_to_html()` function is a line-by-line state machine that processes markdown elements in priority order:

```python
// Simplified from: scripts/md_to_html.py:129-150
def convert_md_to_html(md_text, nav_skip_re=None):
    lines = md_text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1; continue

        if s.startswith("#### "):   out.append(f"<h4>...</h4>"); i += 1
        elif s.startswith("### "):  out.append(f"<h3>...</h3>"); i += 1
        elif s.startswith("## "):   out.append(f"<h2>...</h2>"); i += 1
        elif s.startswith("# "):    out.append(f"<h1>...</h1>"); i += 1
        elif s.startswith("```"):   # code blocks
            ...
        elif "|" in s and ...:      # tables
            ...
        elif s.startswith("> "):    # blockquotes
            ...
        elif s.startswith("<details"):  # expandable sections
            ...
        elif s.startswith("- ") or s.startswith("* "):  # unordered lists
            ...
        elif re.match(r'^\d+\.\s', s):  # ordered lists
            ...
        elif nav_skip_re.search(s):  # skip .md navigation links
            i += 1
        else:                        # paragraphs
            ...
```

Inline formatting (bold, italic, code, images, links) is handled by `process_inline()`, which applies HTML escaping first, then regex substitutions for markdown syntax.

## XSS Protection

The `sanitize_url()` function blocks dangerous URL schemes:

```python
// Simplified from: scripts/md_to_html.py:62-67
def sanitize_url(url):
    """Block javascript:, data:, vbscript: etc."""
    scheme = re.match(r'^([a-zA-Z][a-zA-Z0-9+.-]*):', url.strip())
    if scheme and scheme.group(1).lower() not in ('http', 'https', 'mailto', 'tel', ''):
        return '#'
    return url
```

Only `http`, `https`, `mailto`, and `tel` schemes are allowed. Everything else gets redirected to `#`.

## Quiz System

The quiz subsystem has three stages:

**1. Extract** — `extract_quiz_section()` pulls the `## Quiz` section from a markdown file and returns both the quiz text and the remaining content.

**2. Parse** — `parse_quiz_md()` splits on `**Q<N>:**` patterns, extracts options (`A.` through `D.`), answer letter, and explanation:

```python
// Simplified from: scripts/md_to_html.py:223-267
def parse_quiz_md(quiz_md):
    questions = []
    parts = re.split(r'\*\*Q\d+[：:]\s*\*\*\s*', quiz_md)
    for part in parts[1:]:
        ...
        opt_match = re.match(r'^(?:[-*]\s+)?([A-D])[.)]\s+(.*)', line)
        if opt_match and state in ("question", "options"):
            opts.append(opt_match.group(2))
        elif re.match(r'^\*\*Answer\s*[：:]\s*[A-D]\s*\*\*', line):
            answer = m.group(1).upper()
        elif re.match(r'^\*\*Explanation\s*[：:]', line):
            explanation = ...
```

**3. Build** — `build_quiz_section()` generates JavaScript that creates quiz DOM elements with click handlers for instant feedback (green for correct, red for incorrect, with explanation).

## HTML Assembly

The `build_html()` function assembles the final page with all interactive features:

```python
// Simplified from: scripts/md_to_html.py:358-367
def build_html(chapters, accent, title, lang="zh", quiz_html="", watermark_html=""):
    l = I18N.get(lang, I18N["zh"])
    divs, links = [], []
    for idx, ch in enumerate(chapters):
        nav = '<div class="nav-links">'
        nav += prev_link if idx > 0 else '<span></span>'
        nav += next_link if idx < len(chapters)-1 else '<span></span>'
        nav += '</div>'
        divs.append(f'<div class="chapter" id="ch{idx}">{ch["html"]}\n{nav}</div>')
        links.append(sidebar_link)
```

The generated HTML includes:
- CSS custom properties for light/dark theming
- Sidebar with chapter navigation links
- Theme toggle button (persists in localStorage)
- Font size adjustment buttons (persists in localStorage)
- Mobile responsive breakpoint at 768px
- Print-friendly styles (hides sidebar, shows all chapters)

## Verification

The `verify_html()` function performs post-build validation:

```python
// Simplified from: scripts/md_to_html.py:462-486
def verify_html(html_path, expected_chapters=0, source_dir=None):
    ...
    # 1. Section count matches .md file count
    # 2. Per-section content check (heading + content element)
    # 3. HTML size >= 80% of markdown size
    # 4. No broken .md links
    # 5. Navigation consistency
    # 6. Quiz presence check
```

The verification result is written to `verify-result.json` alongside the HTML file, providing structured evidence of quality.

## Safety Net: Broken Link Removal

After assembly, three regex passes remove any residual `.md` links that survived conversion:

```python
// Simplified from: scripts/md_to_html.py:451-456
# 1. Standalone <p> with dual nav link (prev | next)
raw = re.sub(r'<p>\s*<a href="[^"]*\.md">...</a>\s*\|\s*<a href="[^"]*\.md">...</a>\s*</p>', '', raw)
# 2. Standalone <p> with single nav link
raw = re.sub(r'<p>\s*<a href="[^"]*\.md">...</a>\s*</p>', '', raw)
# 3. Inline .md links: replace href="*.md" with href="#"
raw = re.sub(r'href="[^"]*\.md"', 'href="#"', raw)
```

This belt-and-suspenders approach ensures the HTML never has broken internal links.

[Previous: Phase Pipeline](03-phase-pipeline.md) | [Next: Accuracy System](05-accuracy-system.md)
