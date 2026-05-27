#!/usr/bin/env python3
"""
Convert markdown chapter files into a single self-contained interactive HTML.
Build tool for project-walkthrough all-depth conversion.

Usage:
    python md_to_html.py <docs_dir> <output_html> [--title "Title"] [--accent "#hex"]
                         [--lang zh|zh-pure|en|bilingual] [--quiz-chapter N]
    python md_to_html.py --verify <html_file> [--source-dir <docs_dir>]
"""

import argparse
import re
import json
import html as html_module
from pathlib import Path
from datetime import datetime, timezone


# ── i18n ──────────────────────────────────────────────────────────

I18N = {
    "zh": {
        "lang": "zh-CN", "chapters": "章节",
        "prev": "&larr; 上一章", "next": "下一章 &rarr;",
        "quiz_title": "知识测验",
        "nav_skip": (r'\[[^\]]*(?:上一章|下一章|返回目录)[^\]]*\]'
                     r'\([^\)]+\.md\)'),
    },
    "zh-pure": {
        "lang": "zh-CN", "chapters": "章节",
        "prev": "&larr; 上一章", "next": "下一章 &rarr;",
        "quiz_title": "知识测验",
        "nav_skip": (r'\[[^\]]*(?:上一章|下一章|返回目录)[^\]]*\]'
                     r'\([^\)]+\.md\)'),
    },
    "en": {
        "lang": "en", "chapters": "Chapters",
        "prev": "&larr; Previous", "next": "Next &rarr;",
        "quiz_title": "Quiz",
        "nav_skip": (r'\[[^\]]*(?:Previous|Prev|Next|Back to|Continue'
                     r'|Table of Contents|Home)[^\]]*\]'
                     r'\([^\)]+\.md\)'),
    },
    "bilingual": {
        "lang": "zh-CN", "chapters": "Chapters / 章节",
        "prev": "&larr; Prev / 上一章", "next": "Next / 下一章 &rarr;",
        "quiz_title": "Quiz / 知识测验",
        "nav_skip": (r'\[[^\]]*(?:上一章|下一章|返回目录|Previous|Prev'
                     r'|Next|Back to|Continue)[^\]]*\]'
                     r'\([^\)]+\.md\)'),
    },
}


# ── Helpers ───────────────────────────────────────────────────────

def escape_html(s):
    return html_module.escape(s)


def sanitize_url(url):
    """Block javascript:, data:, vbscript: etc."""
    scheme = re.match(r'^([a-zA-Z][a-zA-Z0-9+.-]*):', url.strip())
    if scheme and scheme.group(1).lower() not in ('http', 'https', 'mailto', 'tel', ''):
        return '#'
    return url


def preprocess_md(text):
    """Strip HTML comments before conversion."""
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)


def escape_js_string(s):
    """Escape a string for embedding inside JS single-quoted string literal."""
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '')
    return s


def process_inline(text):
    text = escape_html(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Images before links
    text = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'<img src="{sanitize_url(m.group(2))}" alt="{m.group(1)}" style="max-width:100%">',
        text)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: f'<a href="{sanitize_url(m.group(2))}">{m.group(1)}</a>',
        text)
    return text


# ── Table parsing ─────────────────────────────────────────────────

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
    headers = row(masked[0])
    data = [row(l) for l in masked[2:] if l.strip()]
    parts = ['<table><thead><tr>']
    for h in headers: parts.append(f"<th>{escape_html(h)}</th>")
    parts.append('</tr></thead><tbody>')
    for r in data:
        parts.append('<tr>')
        for c in r: parts.append(f"<td>{process_inline(c)}</td>")
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return ''.join(parts)


# ── Markdown → HTML ───────────────────────────────────────────────

def convert_md_to_html(md_text, nav_skip_re=None):
    if nav_skip_re is None:
        nav_skip_re = re.compile(I18N["zh"]["nav_skip"])
    lines = md_text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1; continue

        if s.startswith("#### "):   out.append(f"<h4>{process_inline(s[5:])}</h4>"); i += 1
        elif s.startswith("### "):  out.append(f"<h3>{process_inline(s[4:])}</h3>"); i += 1
        elif s.startswith("## "):   out.append(f"<h2>{process_inline(s[3:])}</h2>"); i += 1
        elif s.startswith("# "):    out.append(f"<h1>{process_inline(s[2:])}</h1>"); i += 1
        elif s in ("---","***","___"): out.append("<hr>"); i += 1
        elif s.startswith("```"):
            code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            out.append(f'<pre><code>{escape_html(chr(10).join(code))}</code></pre>')
        elif "|" in s and i+1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i+1]):
            tbl = []
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip():
                tbl.append(lines[i]); i += 1
            out.append(parse_table(tbl))
        elif s.startswith("> "):
            q = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                q.append(lines[i].strip()[2:]); i += 1
            out.append(f'<blockquote><p>{"<br>".join(process_inline(l) for l in q)}</p></blockquote>')
        elif s.startswith("<details"):
            d = []
            while i < len(lines):
                line = lines[i]
                if not (line.strip().startswith("<details") or
                        line.strip().startswith("</details") or
                        line.strip().startswith("<summary") or
                        line.strip().startswith("</summary")):
                    line = process_inline(line)
                d.append(line)
                if "</details>" in lines[i]: i += 1; break
                i += 1
            out.append(chr(10).join(d))
        elif s.startswith("- ") or s.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                items.append(f"<li>{process_inline(lines[i].strip()[2:])}</li>"); i += 1
            out.append(f"<ul>{''.join(items)}</ul>")
        elif re.match(r'^\d+\.\s', s):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s', lines[i].strip()):
                items.append(f"<li>{process_inline(re.sub(r'^\s*\d+\.\s','',lines[i].strip()))}</li>"); i += 1
            out.append(f"<ol>{''.join(items)}</ol>")
        elif nav_skip_re.search(s):
            i += 1  # skip .md navigation links
        else:
            p = []
            while (i < len(lines) and lines[i].strip()
                   and not lines[i].startswith("#") and not lines[i].strip().startswith("```")
                   and not lines[i].strip().startswith("> ") and not lines[i].strip().startswith("- ")
                   and not lines[i].strip().startswith("* ") and not re.match(r'^\d+\.\s', lines[i].strip())
                   and lines[i].strip() not in ("---","***","___") and not lines[i].strip().startswith("<details")
                   and not ("|" in lines[i].strip() and i+1<len(lines) and re.match(r'^[\s|:-]+$', lines[i+1]))):
                p.append(lines[i].strip()); i += 1
            if p: out.append(f"<p>{process_inline(' '.join(p))}</p>")
    return chr(10).join(out)


# ── Quiz parsing ──────────────────────────────────────────────────

def extract_quiz_section(md_text):
    """Extract and remove ## Quiz section from markdown. Returns (quiz_md, remaining_md)."""
    lines = md_text.split("\n")
    quiz_lines = []
    remaining = []
    in_quiz = False
    for line in lines:
        if line.strip().startswith("## Quiz") or line.strip().startswith("## quiz"):
            in_quiz = True
            continue  # skip the heading itself
        if in_quiz:
            # Quiz section ends at next ## heading or end of file
            if line.strip().startswith("## ") and not line.strip().startswith("## Quiz"):
                in_quiz = False
                remaining.append(line)
            else:
                quiz_lines.append(line)
        else:
            remaining.append(line)
    return chr(10).join(quiz_lines), chr(10).join(remaining)


def parse_quiz_md(quiz_md):
    """Parse quiz markdown into quizData list of {q, o, c, e}."""
    questions = []
    # Split on **Q<N>:** or **Q<N>：**
    parts = re.split(r'\*\*Q\d+[：:]\s*\*\*\s*', quiz_md)
    for part in parts[1:]:  # skip text before first Q
        if not part.strip():
            continue
        lines = [l.strip() for l in part.strip().split("\n") if l.strip()]

        # Question text: everything before options
        q_lines = []
        opts = []
        answer = ""
        explanation = ""
        state = "question"

        for line in lines:
            # Options: "A. text" or "- A. text" or "* A. text"
            opt_match = re.match(r'^(?:[-*]\s+)?([A-D])[.)]\s+(.*)', line)
            if opt_match and state in ("question", "options"):
                state = "options"
                opts.append(opt_match.group(2))
            elif re.match(r'^\*\*Answer\s*[：:]\s*[A-D]\s*\*\*', line, re.IGNORECASE):
                m = re.search(r'([A-D])', line, re.IGNORECASE)
                if m: answer = m.group(1).upper()
                state = "answer"
            elif re.match(r'^\*\*Explanation\s*[：:]', line, re.IGNORECASE):
                explanation = re.sub(r'^\*\*Explanation\s*[：:]\s*\*\*\s*', '', line)
                state = "explanation"
            elif state == "explanation":
                explanation += " " + line
            elif state == "question":
                q_lines.append(line)

        if q_lines and opts and answer:
            correct = ord(answer) - ord('A')
            if 0 <= correct < len(opts):
                questions.append({
                    "q": " ".join(q_lines),
                    "o": opts,
                    "c": correct,
                    "e": explanation.strip(),
                })
    return questions


def build_quiz_section(questions, lang_strings):
    """Generate quiz chapter div with interactive quiz JS."""
    if not questions:
        return ""
    quiz_title = lang_strings.get("quiz_title", "Quiz")
    # Build quizData JS array
    items = []
    for q in questions:
        opts_js = "[" + ",".join(f"'{escape_js_string(o)}'" for o in q["o"]) + "]"
        items.append(f"{{q:'{escape_js_string(q['q'])}',o:{opts_js},c:{q['c']},"
                     f"e:'{escape_js_string(q['e'])}'}}")
    quiz_data = "[" + ",".join(items) + "]"
    return f'''<div class="chapter" id="ch-quiz">
<h1>{escape_html(quiz_title)}</h1>
<div id="quiz-container"></div>
<div class="nav-links"><span></span><span></span></div>
</div>
<script>
(function(){{
var data={quiz_data};
var container=document.getElementById('quiz-container');
data.forEach(function(item,idx){{
  var wrap=document.createElement('div');wrap.style.cssText='margin:24px 0;padding:20px;background:var(--card-bg);border:1px solid var(--card-border);border-radius:8px';
  var qTitle=document.createElement('div');qTitle.style.cssText='font-weight:600;margin-bottom:12px;font-size:16px';
  qTitle.textContent=(idx+1)+'. '+item.q;wrap.appendChild(qTitle);
  item.o.forEach(function(opt,oi){{
    var btn=document.createElement('button');
    btn.style.cssText='display:block;width:100%;text-align:left;padding:10px 16px;margin:6px 0;background:var(--card-bg);border:1px solid var(--card-border);border-radius:6px;cursor:pointer;font-size:14px;color:var(--text)';
    btn.textContent=String.fromCharCode(65+oi)+'. '+opt;
    btn.addEventListener('click',function(){{
      var buttons=wrap.querySelectorAll('button');buttons.forEach(function(b){{b.disabled=true;b.style.cursor='default'}});
      if(oi===item.c){{btn.style.background='#059669';btn.style.color='#fff'}}
      else{{btn.style.background='#dc2626';btn.style.color='#fff';buttons[item.c].style.background='#059669';buttons[item.c].style.color='#fff'}}
      var fb=document.createElement('div');fb.style.cssText='margin-top:12px;padding:12px;background:var(--quote-bg);border-left:4px solid var(--quote-border);font-size:14px;line-height:1.6';
      fb.textContent=item.e;wrap.appendChild(fb);
    }});
    wrap.appendChild(btn);
  }});
  container.appendChild(wrap);
}});
}})();
</script>'''


def build_watermark_section(tool_name, tool_url, lang="zh"):
    """Generate promo page as the last chapter of the HTML report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    is_en = lang in ("en", "bilingual")

    if is_en:
        heading = "About This Report"
        gen_line = f"Generated on {now}"
        tool_line = f"Built with <strong>{escape_html(tool_name)}</strong>"
        url_line = f'<a href="{sanitize_url(tool_url)}" target="_blank">{escape_html(tool_url)}</a>' if tool_url else ""
        closing = "Feedback and contributions are welcome!"
    else:
        heading = "关于本报告"
        gen_line = f"生成时间：{now}"
        tool_line = f"使用工具：<strong>{escape_html(tool_name)}</strong>"
        url_line = f'<a href="{sanitize_url(tool_url)}" target="_blank">{escape_html(tool_url)}</a>' if tool_url else ""
        closing = "欢迎大家使用、讨论和反馈！"

    parts = [f'<div class="chapter" id="ch-watermark">']
    parts.append(f'<h1>{heading}</h1>')
    parts.append(f'<div style="text-align:center;padding:40px 20px;">')
    parts.append(f'<p style="font-size:15px;color:var(--text);opacity:0.85;">{gen_line}</p>')
    parts.append(f'<p style="font-size:15px;color:var(--text);margin-top:16px;">{tool_line}</p>')
    if url_line:
        parts.append(f'<p style="margin-top:12px;">{url_line}</p>')
    parts.append(f'<p style="font-size:14px;color:var(--text);opacity:0.7;margin-top:24px;">{closing}</p>')
    parts.append('</div>')
    parts.append('<div class="nav-links"><span></span><span></span></div>')
    parts.append('</div>')
    return chr(10).join(parts)


# ── Title extraction ──────────────────────────────────────────────

def extract_title(md):
    for line in md.split(chr(10)):
        s = line.strip()
        if s.startswith("# "):
            return re.sub(r'^\d+\s+', '', s[2:])
    return "Untitled"


# ── HTML assembly ─────────────────────────────────────────────────

def build_html(chapters, accent, title, lang="zh", quiz_html="", watermark_html=""):
    l = I18N.get(lang, I18N["zh"])
    divs, links = [], []
    for idx, ch in enumerate(chapters):
        nav = '<div class="nav-links">'
        nav += f'<a href="#" onclick="showChapter({idx-1});return false;">{l["prev"]}</a>' if idx > 0 else '<span></span>'
        nav += f'<a href="#" onclick="showChapter({idx+1});return false;">{l["next"]}</a>' if idx < len(chapters)-1 else '<span></span>'
        nav += '</div>'
        divs.append(f'<div class="chapter" id="ch{idx}">{ch["html"]}\n{nav}</div>')
        links.append(f'<a href="#" onclick="showChapter({idx});return false;">{escape_html(ch["sidebar"])}</a>')

    # Quiz nav item
    if quiz_html:
        links.append(f'<a href="#" onclick="showChapter({len(chapters)});return false;">{escape_html(l["quiz_title"])}</a>')

    quiz_idx = len(chapters)
    # Watermark nav item
    watermark_idx = quiz_idx + (1 if quiz_html else 0)
    if watermark_html:
        wm_label = "About" if lang in ("en",) else ("About / 关于" if lang == "bilingual" else "关于")
        links.append(f'<a href="#" onclick="showChapter({watermark_idx});return false;">{escape_html(wm_label)}</a>')

    # Fix last chapter's Next link to point to quiz/watermark if they exist
    next_target = None
    if watermark_html:
        next_target = watermark_idx
    elif quiz_html:
        next_target = quiz_idx
    if next_target is not None and chapters:
        old_nav = '<span></span></div>'
        new_nav = f'<a href="#" onclick="showChapter({next_target});return false;">{l["next"]}</a></div>'
        divs[-1] = divs[-1].replace(old_nav, new_nav, 1)

    # Fix quiz Next link to point to watermark
    if quiz_html and watermark_html:
        pass  # watermark follows quiz in template, navigation is self-contained

    raw = f'''<!DOCTYPE html>
<html lang="{l["lang"]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(title)}</title>
<style>
:root{{--bg:#fff;--text:#1a1a2e;--sidebar-bg:#f0f0f5;--sidebar-text:#333;--sidebar-hover:#e0e0ea;--sidebar-active:#d0d0e0;--card-bg:#f8f8fc;--card-border:#e0e0e8;--accent:{accent};--link:{accent};--code-bg:#f4f4f8;--quote-bg:#f8f8ff;--quote-border:{accent}88}}
[data-theme="dark"]{{--bg:#1a1a2e;--text:#e0e0ea;--sidebar-bg:#16213e;--sidebar-text:#c0c0d0;--sidebar-hover:#1a2744;--sidebar-active:#1e2d4a;--card-bg:#1e2744;--card-border:#2a3555;--accent:{accent}cc;--link:{accent}cc;--code-bg:#162030;--quote-bg:#1a1a30;--quote-border:{accent}88}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.7;display:flex;min-height:100vh}}
.sidebar{{width:280px;background:var(--sidebar-bg);color:var(--sidebar-text);padding:20px 0;position:fixed;top:0;left:0;height:100vh;overflow-y:auto;border-right:1px solid var(--card-border);z-index:100}}
.sidebar h2{{font-size:14px;padding:8px 20px;color:var(--accent);text-transform:uppercase;letter-spacing:1px}}
.sidebar a{{display:block;padding:8px 20px;text-decoration:none;color:var(--sidebar-text);font-size:13px;border-left:3px solid transparent}}
.sidebar a:hover{{background:var(--sidebar-hover);border-left-color:var(--accent)}}
.sidebar a.active{{background:var(--sidebar-active);border-left-color:var(--accent);font-weight:600}}
.main{{margin-left:280px;padding:40px 60px;max-width:860px;width:100%}}
h1{{font-size:28px;margin-bottom:16px;color:var(--accent)}}h2{{font-size:22px;margin:32px 0 12px;color:var(--accent)}}h3{{font-size:18px;margin:24px 0 8px}}h4{{font-size:16px;margin:20px 0 8px;opacity:0.9}}
p{{margin-bottom:12px}}blockquote{{border-left:4px solid var(--quote-border);background:var(--quote-bg);padding:12px 20px;margin:16px 0;font-style:italic}}
table{{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px}}th,td{{border:1px solid var(--card-border);padding:8px 12px;text-align:left}}th{{background:var(--card-bg);font-weight:600}}
pre{{background:var(--code-bg);border:1px solid var(--card-border);border-radius:6px;padding:16px;overflow-x:auto;margin:16px 0;font-size:13px;line-height:1.5}}
code{{font-family:'SF Mono',Monaco,'Cascadia Code',monospace}}pre code{{background:none;border:none;padding:0}}p code,li code{{background:var(--code-bg);padding:2px 6px;border-radius:3px;font-size:0.9em}}
ul,ol{{margin:12px 0 12px 24px}}li{{margin-bottom:6px}}hr{{border:none;border-top:1px solid var(--card-border);margin:24px 0}}
details{{margin:12px 0;background:var(--card-bg);border:1px solid var(--card-border);border-radius:6px;padding:12px 16px}}summary{{cursor:pointer;color:var(--accent);font-weight:500;font-size:14px}}
.nav-links{{display:flex;justify-content:space-between;margin:40px 0 20px;padding-top:20px;border-top:1px solid var(--card-border)}}.nav-links a{{color:var(--link);text-decoration:none}}
.topbar{{display:none;position:fixed;top:0;left:0;right:0;height:50px;background:var(--sidebar-bg);border-bottom:1px solid var(--card-border);z-index:200;padding:0 16px;align-items:center;justify-content:space-between}}.topbar button{{background:none;border:none;color:var(--text);font-size:20px;cursor:pointer}}
.theme-toggle{{position:fixed;bottom:20px;right:20px;width:44px;height:44px;border-radius:50%;background:var(--accent);color:#fff;border:none;cursor:pointer;font-size:20px;z-index:300;box-shadow:0 2px 8px rgba(0,0,0,0.2)}}
.chapter{{display:none}}.chapter.active{{display:block}}
@media(max-width:768px){{.sidebar{{transform:translateX(-100%)}}.sidebar.open{{transform:translateX(0)}}.main{{margin-left:0;padding:60px 20px 40px}}.topbar{{display:flex}}}}
@media print{{.sidebar,.topbar,.theme-toggle{{display:none!important}}.main{{margin-left:0;padding:20px}}.chapter{{display:block!important;page-break-after:always}}}}
</style>
</head>
<body>
<button class="theme-toggle" onclick="toggleTheme()">&#9790;</button>
<div class="topbar"><button onclick="document.getElementById('sidebar').classList.toggle('open')">&#9776;</button><span>{escape_html(title)}</span><span></span></div>
<nav class="sidebar" id="sidebar"><h2>{l["chapters"]}</h2>{chr(10).join(links)}</nav>
<main class="main" id="main">{chr(10).join(divs)}
{quiz_html}
{watermark_html}
</main>
<script>
function toggleTheme(){{var d=document.documentElement,isDark=d.getAttribute('data-theme')==='dark';d.setAttribute('data-theme',isDark?'light':'dark');localStorage.setItem('theme',isDark?'light':'dark');document.querySelector('.theme-toggle').textContent=isDark?'&#9788;':'&#9790;'}}
(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else if(window.matchMedia('(prefers-color-scheme:dark)').matches)document.documentElement.setAttribute('data-theme','dark');document.querySelector('.theme-toggle').textContent=document.documentElement.getAttribute('data-theme')==='dark'?'&#9788;':'&#9790;'}})();
function showChapter(i){{document.querySelectorAll('.chapter').forEach(function(c){{c.classList.remove('active')}});document.querySelectorAll('.sidebar a').forEach(function(a){{a.classList.remove('active')}});if(document.querySelectorAll('.chapter')[i])document.querySelectorAll('.chapter')[i].classList.add('active');if(document.querySelectorAll('.sidebar a')[i])document.querySelectorAll('.sidebar a')[i].classList.add('active');window.scrollTo(0,0);document.getElementById('sidebar').classList.remove('open')}}
showChapter(0);
</script>
</body></html>'''

    # Safety net: remove residual .md links
    # 1. Standalone <p> with dual nav link (prev | next)
    raw = re.sub(r'<p>\s*<a href="[^"]*\.md">[^<]*</a>\s*\|\s*<a href="[^"]*\.md">[^<]*</a>\s*</p>', '', raw)
    # 2. Standalone <p> with single nav link
    raw = re.sub(r'<p>\s*<a href="[^"]*\.md">[^<]*</a>\s*</p>', '', raw)
    # 3. Inline .md links: replace href="*.md" with href="#" (keeps text, breaks link)
    raw = re.sub(r'href="[^"]*\.md"', 'href="#"', raw)
    return raw


# ── Verification ──────────────────────────────────────────────────

def verify_html(html_path, expected_chapters=0, source_dir=None):
    """Post-build validation with per-section checks and relative size metric."""
    p = Path(html_path)
    if not p.is_file():
        print(f"VERIFY FAILED: file not found: {html_path}")
        return 1, {"passed": False, "error": "file not found",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "html_file": str(html_path)}
    content = p.read_text("utf-8")
    file_size = p.stat().st_size
    errors = []

    total_md_size = 0
    expected_chapters = 0
    if source_dir:
        md_files = sorted(Path(source_dir).glob("*.md"))
        expected_chapters = len(md_files)
        total_md_size = sum(f.stat().st_size for f in md_files)

    # 1. Section count
    static_ch = content.count('class="chapter"')
    static_sec = content.count('class="section"')
    dom_sec = len(re.findall(r"""el\(\s*['"]div['"]\s*,\s*['"]section""", content))
    section_count = max(static_ch, static_sec, dom_sec)
    if expected_chapters > 0 and section_count < expected_chapters:
        errors.append(f"Section count {section_count} != expected {expected_chapters}")

    # 2. Per-section content check
    ch_pat = re.compile(
        r'<div class="chapter"[^>]*>(.*?)</div>\s*(?=<div class="chapter"|</main>)', re.DOTALL)
    for i, ch in enumerate(ch_pat.findall(content)):
        has_heading = bool(re.search(r'<h[1-4][> ]', ch))
        has_content = bool(re.search(r'<(p|pre|table|ul|ol|blockquote|details)[> ]', ch))
        if not has_heading and not has_content:
            errors.append(f"Chapter {i+1} is empty (no heading or content element)")

    # 3. Relative file size
    ratio_val = file_size / total_md_size if total_md_size > 0 else None
    if total_md_size > 0 and ratio_val is not None and ratio_val < 0.80:
        errors.append(f"HTML size {file_size:,}b is {ratio_val:.0%} of markdown "
                     f"({total_md_size:,}b), below 80% threshold")

    # 4. No broken .md links
    md_links = re.findall(r'href="[^"]*\.md"', content)
    if md_links:
        errors.append(f"Found {len(md_links)} broken .md links: {md_links[:3]}")

    # 5. Navigation consistency (sidebar only)
    sidebar_match = re.search(r'<nav class="sidebar"[^>]*>(.*?)</nav>', content, re.DOTALL)
    sidebar_links = sidebar_match.group(1).count('showChapter(') if sidebar_match else 0
    if expected_chapters > 0 and sidebar_links > 0 and sidebar_links < expected_chapters:
        errors.append(f"Sidebar nav {sidebar_links} < chapter count {expected_chapters}")

    # 6. Quiz presence (check if quiz HTML exists in output)
    quiz_in_html = bool(re.search(r'id="quiz-container"', content))
    quiz_in_source = False
    if source_dir:
        for md_f in sorted(Path(source_dir).glob("*.md")):
            if re.search(r'^##\s+Quiz\b', md_f.read_text("utf-8"), re.MULTILINE):
                quiz_in_source = True
                break
    if quiz_in_source and not quiz_in_html:
        errors.append("Quiz section in source markdown but not in HTML (quiz parsing may have failed)")

    # Build result dict
    result = {
        "passed": len(errors) == 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "html_file": str(html_path),
        "html_size": file_size,
        "markdown_size": total_md_size,
        "section_count": section_count,
        "expected_sections": expected_chapters,
        "ratio_pct": round(ratio_val * 100) if ratio_val else None,
        "sidebar_nav_count": sidebar_links,
        "errors": errors,
    }

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print(f"  x {e}")
        return 1, result
    else:
        ratio = f", {ratio_val:.0%} of md" if ratio_val else ""
        print(f"VERIFICATION PASSED: {file_size:,}b, {section_count} sections{ratio}")
        return 0, result


# ── Main ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Convert markdown chapters to self-contained interactive HTML")
    p.add_argument("docs_dir", nargs="?", help="Directory with .md chapter files")
    p.add_argument("output_html", nargs="?", help="Output HTML file path")
    p.add_argument("--title", default=None)
    p.add_argument("--accent", default="#4a6fa5")
    p.add_argument("--lang", default="zh", choices=list(I18N.keys()),
                   help="Language mode (default: zh)")
    p.add_argument("--quiz-chapter", type=int, default=None,
                   help="1-based index of chapter containing ## Quiz section")
    p.add_argument("--verify", metavar="HTML_FILE",
                   help="Verify a generated HTML file instead of generating")
    p.add_argument("--source-dir", default=None,
                   help="Source markdown dir for --verify")
    p.add_argument("--no-watermark", action="store_true",
                   help=argparse.SUPPRESS)
    p.add_argument("--tool-name", default=None,
                   help=argparse.SUPPRESS)
    p.add_argument("--tool-url", default=None,
                   help=argparse.SUPPRESS)
    a = p.parse_args()

    if a.verify:
        code, _ = verify_html(a.verify, source_dir=a.source_dir)
        return code

    if not a.docs_dir or not a.output_html:
        p.error("docs_dir and output_html are required when not using --verify")

    lang = I18N.get(a.lang, I18N["zh"])
    nav_skip_re = re.compile(lang["nav_skip"])

    dp = Path(a.docs_dir)
    mds = sorted(dp.glob("*.md"))
    if not mds:
        print(f"No .md files in {a.docs_dir}"); return 1

    # Quiz extraction
    quiz_html = ""
    quiz_questions = []
    quiz_chapter_idx = (a.quiz_chapter - 1) if a.quiz_chapter else None

    chapters, title = [], a.title
    for file_idx, f in enumerate(mds):
        t = f.read_text("utf-8"); ti = extract_title(t)
        if not title: title = ti
        sb = re.sub(r'^\d+\s+', '', ti)
        if len(sb) > 30: sb = sb[:28] + "..."

        # Extract quiz from specified chapter
        if quiz_chapter_idx is not None and file_idx == quiz_chapter_idx:
            quiz_md, remaining = extract_quiz_section(t)
            quiz_questions = parse_quiz_md(quiz_md)
            if quiz_questions:
                quiz_html = build_quiz_section(quiz_questions, lang)
            t = remaining  # convert remaining content without quiz section

        chapters.append({
            "title": ti,
            "sidebar": f"{f.stem[:2]} {sb}",
            "html": convert_md_to_html(preprocess_md(t), nav_skip_re),
        })

    # Watermark (promo page)
    watermark_html = ""
    if not a.no_watermark:
        tool_name = a.tool_name or "project-walkthrough"
        tool_url = a.tool_url or "https://github.com/zwyin/project-walkthrough-skill"
        watermark_html = build_watermark_section(tool_name, tool_url, a.lang)

    r = build_html(chapters, a.accent, title, a.lang, quiz_html, watermark_html)
    out = Path(a.output_html); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(r, "utf-8")
    mt = sum(f.stat().st_size for f in mds); hs = out.stat().st_size
    q_info = f", {len(quiz_questions)} quiz questions" if quiz_questions else ""
    w_info = ", +promo page" if watermark_html else ""
    print(f"Converted {len(mds)} files ({mt:,}b -> {hs:,}b, {hs/mt*100:.0f}%{q_info}{w_info})")

    # Auto-verify and write result
    v, result = verify_html(a.output_html, source_dir=a.docs_dir)
    if v != 0:
        print("WARNING: Post-generation verification failed!")
    # Write verify-result.json alongside HTML
    result_file = out.parent / "verify-result.json"
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    exit(main())
