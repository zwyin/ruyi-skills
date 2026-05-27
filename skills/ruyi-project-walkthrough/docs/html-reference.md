# Interactive HTML Reference

Structure and patterns for generating walkthrough HTML files.

## File Requirements

- Single self-contained HTML file (no external CSS/JS/images)
- Open directly in any browser (no server needed)
- Shareable via zip/email

## Generation Strategy

The converter tool (`scripts/md_to_html.py`) is the canonical HTML generation method for **all depth levels** (brief, medium, deep).

### Converter command

```bash
# Generate HTML from markdown chapters
python scripts/md_to_html.py <docs_dir> <output.html> \
  --title "Project Name" --accent "#hex" --lang zh --quiz-chapter 6

# Verify generated HTML
python scripts/md_to_html.py --verify <output.html> --source-dir <docs_dir>
```

Flags:
- `--lang <lang>`: one of zh, zh-pure, en, bilingual (matches Phase 0 choice)
- `--quiz-chapter <N>`: 1-based index of the chapter containing `## Quiz` section. Omit if no quiz.
- `--verify <html>`: run verification checks instead of generating
- `--source-dir <dir>`: source markdown directory for --verify (enables section count + size checks)

### Converter output structure

- Chapters: `<div class="chapter">` with `showChapter(N)` JS navigation
- Sidebar: `<nav class="sidebar">` with `<a onclick="showChapter(N)">` links
- Theme: dark/light toggle via `data-theme` attribute on `<html>`
- Quiz: interactive quiz section with `quizData` JS array and DOM-based rendering
- CSS: inline styles in `<style>` tag (no external CSS)

### Why converter-first?

- Security hooks block dynamic DOM writes in tool calls
- DOM API generation (createElement + textContent) is 3-5x more verbose than equivalent HTML
- Rich content (tables, code blocks, blockquotes) is impractical to generate via DOM API
- Manual generation has caused silent content omission bugs (empty sections)
- The converter has built-in XSS protection (URL sanitization, HTML escaping)

### Converter output guarantees

- All markdown elements preserved (headings, paragraphs, lists, tables, code, blockquotes)
- Self-contained HTML (no external dependencies)
- Sidebar navigation, dark/light toggle, mobile responsive, print-friendly
- Navigation links stripped and replaced with JS-based `showChapter()` navigation
- Post-generation verification built-in (section count, heading count, file size, no broken links)

**Python is required for HTML output.** If Python is unavailable, markdown output is the deliverable.

## CSS Structure

### Theme Variables

```
:root {
  --bg: <dark background>
  --surface: <card/panel background>
  --surface2: <hover/secondary background>
  --border: <border color>
  --text: <primary text>
  --text2: <secondary text>
  --accent: <primary accent>
  --accent2: <lighter accent>
  --green: <correct/success>
  --red: <error/danger>
  --yellow: <warning>
  --blue: <info>
  --orange: <highlight>
}

html.light {
  /* Override all variables for light mode */
}
```

### Accent Color Per Project

Choose accent color based on the project's own design system:

| Project type | Suggested accent | CSS |
|-------------|-----------------|-----|
| Purple-themed tools | Purple | `--accent:#7c6aef;--accent2:#a78bfa` |
| Amber/orange tools | Amber | `--accent:#d97706;--accent2:#fbbf24` |
| Green/nature tools | Emerald | `--accent:#059669;--accent2:#34d399` |
| Blue/corporate | Blue | `--accent:#2563eb;--accent2:#60a5fa` |
| Red/bold tools | Red | `--accent:#dc2626;--accent2:#f87171` |

If the project doesn't have a visible brand color, use purple as default.

### Source Citation Style

Code blocks should show their source attribution above the code:

```css
.source-citation {
  font-size: 0.75em;
  color: var(--text2);
  font-style: italic;
  margin: 0 0 4px 8px;
  opacity: 0.7;
}
```

## Layout

```
+--------------------------------------------------+
| [Theme Toggle (dark/light)]              [fixed]  |
+---------+----------------------------------------+
| Sidebar | Main Content Area                      |
| (fixed) |                                        |
|         |  Chapter Title                         |
| 0 Guide |  subtitle text...                      |
| 1 Chap1 |                                        |
| 2 Chap2 |  [Content cards, code blocks,          |
| 3 Chap3 |   tables, expandables...]              |
| ...     |                                        |
| Q Quiz  |  [Prev] [Next]                         |
+---------+----------------------------------------+
```

### Mobile (< 768px)

- Sidebar hidden by default, toggle button visible
- Grid layouts collapse to single column
- Reduce padding

## JavaScript String Escaping

When text content (quiz questions, explanations, labels) contains characters that conflict with JavaScript string delimiters, they **must be escaped**.

### Rules

1. **Double-quote strings** — escape inner `"` as `\"`:
   ```javascript
   // WRONG — the inner " breaks the string literal
   e: "消息被"吞掉"了"
   // RIGHT — escape the inner quotes
   e: "消息被\"吞掉\"了"
   ```

2. **Prefer single-quote strings** for data that may contain `"`, or vice versa:
   ```javascript
   // Use single quotes when content has double quotes
   e: '消息被"吞掉"了'
   // Use double quotes when content has single quotes (apostrophes)
   e: "it's working correctly"
   ```

3. **Characters to watch for in JS string literals:**

   | Character | Must escape in `"..."` | Must escape in `'...'` |
   |-----------|----------------------|----------------------|
   | `"`       | `\"` or use `'...'`  | No                   |
   | `'`       | No                   | `\'` or use `"..."`  |
   | `\`       | `\\`                 | `\\`                 |
   | `` ` ``   | No (in `"..."`/`'...'`) | Only in template literals |
   | Newline   | Use `\n`             | Use `\n`             |

4. **Chinese punctuation is NOT a problem** — `""''《》【】` are distinct Unicode characters from ASCII `"`/`'` and do not need escaping in JS strings. Only ASCII `"` (U+0022) and `'` (U+0027) conflict with JS string delimiters.

### Validation

After generating the HTML file, run `node --check` or the test suite. Unescaped quotes will produce a SyntaxError.

## Security (for converter developers)

The converter applies these protections automatically:
- HTML escaping of all user content (prevents XSS)
- URL protocol filtering (blocks javascript:, data: URLs)
- HTML comment stripping (prevents hidden content)
- `<details>` body sanitization (prevents script injection)

## DOM API Rules

**These rules apply only to converter developers modifying `md_to_html.py`.**

The converter generates static HTML via Python file writes, which does not trigger security hooks. Manual HTML generation by the LLM is no longer supported (converter-first for all depths since v1.6.0).

### Correct patterns (for converter-generated output)

```javascript
// Create elements
var card = document.createElement('div');
card.className = 'card';

// Set text
var title = document.createElement('div');
title.className = 'card-title';
title.textContent = 'Chapter Title';

// Add children
card.appendChild(title);

// Add event listeners
var btn = document.createElement('button');
btn.addEventListener('click', function() { /* ... */ });

// Write to page
container.appendChild(card);
```

## Component Patterns

### Theme Toggle

HTML:
```html
<div class="theme-toggle" onclick="toggleTheme()">
  <span id="btn-dark" class="active">暗色</span>
  <span id="btn-light">亮色</span>
</div>
```

JS:
```javascript
function toggleTheme() {
  var h = document.documentElement;
  var dk = document.getElementById('btn-dark');
  var lt = document.getElementById('btn-light');
  if (h.classList.contains('light')) {
    h.classList.remove('light');
    dk.classList.add('active');
    lt.classList.remove('active');
    localStorage.setItem('theme', 'dark');
  } else {
    h.classList.add('light');
    lt.classList.add('active');
    dk.classList.remove('active');
    localStorage.setItem('theme', 'light');
  }
}
// Initialize from localStorage on page load
```

### Sidebar Navigation

HTML:
```html
<nav class="sidebar" id="sidebar">
  <div class="sidebar-title">Project Name<span>Depth Level</span></div>
  <a class="nav-item active" data-section="s0" onclick="showSection('s0')">
    <span class="nav-num">0</span>Reading Guide
  </a>
  <a class="nav-item" data-section="s1" onclick="showSection('s1')">
    <span class="nav-num">1</span>Chapter Title
  </a>
</nav>
```

JS:
```javascript
function showSection(id) {
  document.querySelectorAll('.section').forEach(function(s) {
    s.classList.remove('active');
  });
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(function(n) {
    n.classList.remove('active');
  });
  document.querySelector('.nav-item[data-section="'+id+'"]')
    .classList.add('active');
  document.querySelector('.sidebar').classList.remove('open');
  window.scrollTo(0, 0);
}
```

### Section Content — CRITICAL: Inline All Content

**Every chapter's full content must be written as HTML elements directly inside its `<div class="section">`.**

The HTML file will be shared as a standalone file (email, chat, offline). Recipients will NOT have access to any markdown files, server, or network.

**FORBIDDEN — Dynamic loading:**
```javascript
// WRONG — file:// blocks CORS, recipients don't have these files
fetch("docs/01-overview.md").then(...)
var xhr = new XMLHttpRequest(); xhr.open("GET", "docs/...");
```

**FORBIDDEN — Placeholder content:**
```html
<!-- WRONG — only a heading with no substance -->
<div class="section" id="s1">
  <h1>Chapter 1: Overview</h1>
  <p>This chapter covers the project overview.</p>
</div>
```

**REQUIRED — Full content inline:**
```html
<div class="section" id="s1">
  <h1>Chapter 1: Overview <span class="depth-badge">DEEP</span></h1>
  <p class="subtitle">Architecture, design decisions, and module breakdown</p>

  <div class="card">
    <div class="card-title">Core Architecture</div>
    <p>The system uses a layered architecture with three main components...</p>
    <p>The design was driven by the need for real-time processing...</p>
  </div>

  <div class="styled-table">
    <table>
      <tr><th>Module</th><th>Responsibility</th><th>Lines</th></tr>
      <tr><td>engine.ts</td><td>Core processing pipeline</td><td>1,200</td></tr>
      <tr><td>parser.ts</td><td>Input validation and parsing</td><td>800</td></tr>
    </table>
  </div>

  <div class="expandable" id="ex-arch-details">
    <div class="expandable-header" onclick="toggleExpand('ex-arch-details')">
      <span>Detailed design rationale</span><span class="arrow">▶</span>
    </div>
    <div class="expandable-body">
      <p>The original design used a monolithic approach but was refactored...</p>
      <p>Key trade-offs considered: performance vs. maintainability...</p>
    </div>
  </div>

  <blockquote>
    <p>Key insight: the project's biggest architectural bet was X, which paid off because Y.</p>
  </blockquote>

  <div class="section-nav">
    <button onclick="showSection('s0')">← Previous</button>
    <button onclick="showSection('s2')">Next →</button>
  </div>
</div>
```

Depth badge colors: `BRIEF` = green background, `MEDIUM` = blue, `DEEP` = red.

### Expandable Sections

HTML:
```html
<div class="expandable" id="ex-unique-id">
  <div class="expandable-header" onclick="toggleExpand('ex-unique-id')">
    <span>Click to expand</span>
    <span class="arrow">▶</span>
  </div>
  <div class="expandable-body">
    <!-- Hidden content revealed on click -->
  </div>
</div>
```

JS:
```javascript
function toggleExpand(id) {
  var el = document.getElementById(id);
  var h = el.querySelector('.expandable-header');
  var b = el.querySelector('.expandable-body');
  h.classList.toggle('open');
  b.classList.toggle('open');
}
```

### CSS Flow Diagrams

Use CSS boxes with arrows for simple flow diagrams:

```html
<div class="flow">
  <div class="flow-node process">Step 1</div>
  <div class="flow-arrow"></div>
  <div class="flow-node decision">Decision?</div>
  <div class="flow-arrow"></div>
  <div class="flow-node result">Result</div>
</div>
```

Node types and their colors:
- `process` -- amber/yellow, standard step
- `decision` -- yellow, branch point
- `result` -- green, outcome
- `danger` -- red, error/stop

### Quiz Section

Build the quiz dynamically with JavaScript (DOM API only). Data structure:

```javascript
var quizData = [
  {
    q: "Question text?",
    o: ["Option A", "Option B", "Option C", "Option D"],
    c: 1,  // correct answer index (0-based)
    e: "Explanation of why B is correct."
  }
];
```

Build loop:
```javascript
quizData.forEach(function(item, idx) {
  var wrap = document.createElement('div');
  // Style the wrap container
  var qTitle = document.createElement('div');
  qTitle.textContent = (idx + 1) + '. ' + item.q;
  wrap.appendChild(qTitle);

  item.o.forEach(function(opt, oi) {
    var btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.textContent = String.fromCharCode(65 + oi) + '. ' + opt;
    btn.addEventListener('click', function() {
      // Disable all options in this question
      // Highlight correct/wrong
      // Show feedback
    });
    wrap.appendChild(btn);
  });

  container.appendChild(wrap);
});
```

Quiz option behavior:
- Click an option: disable all options in that question
- Highlight clicked option: correct = green, wrong = red
- Also highlight the correct answer in green
- Show feedback text below

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

## CSS Classes Quick Reference

| Class | Purpose |
|-------|---------|
| `.card` | Content card with border |
| `.card-title` | Bold title inside card |
| `.code-block` | Monospace code display |
| `.source-citation` | Source attribution line above code blocks |
| `.styled-table` | Bordered data table |
| `.expandable` | Click-to-expand container |
| `.expandable-header` | Clickable header |
| `.expandable-body` | Hidden content |
| `.flow` | Vertical flow diagram container |
| `.flow-node` | Node in flow diagram |
| `.flow-arrow` | Arrow between nodes |
| `.quiz-option` | Quiz answer button |
| `.quiz-feedback` | Quiz result text |
| `.tag` | Small colored badge |
| `.tag-green/blue/orange/red/amber/purple` | Tag color variants |
| `.grid-2` / `.grid-3` | Responsive grid layout |
| `.section-nav` | Chapter navigation buttons |
| `.depth-badge` | BRIEF/MEDIUM/DEEP label |
| `.theme-toggle` | Dark/light mode switch |
| `.mobile-toggle` | Sidebar toggle (mobile only) |
