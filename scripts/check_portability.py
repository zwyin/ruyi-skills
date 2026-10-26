#!/usr/bin/env python3
"""Portability lint for the skill collection.

For every skill (outer skills/<name>/SKILL.md + inner
skills/<name>/skills/<name>/SKILL.md) run five checks and print one
`✓/✗ <skill>: <check>` line per check:

  1. license             frontmatter declares a `license:` field
  2. description-trigger first non-empty description line contains
                         'use when' (case-insensitive, colon not required)
                         and contains no Chinese (CJK unified ideographs or
                         CJK punctuation; em-dash and other non-CJK
                         punctuation do not count)
  3. mirror              outer and inner SKILL.md are byte-identical
                         (filecmp.cmp shallow=False; symlinks are followed)
  4. size                SKILL.md <= 500 lines; 500 < n <= 1500 is ✓ with a
                         WARN line; n > 1500 fails
  5. script-paths        skills/<name>/scripts/** *.py/*.sh contain no
                         /Users/ or /home/ (files under tests/ or fixtures/
                         are exempt; SKILL.md and docs/ are never scanned —
                         /Users/xxx/ inside SKILL.md is rule-teaching text)

Content checks (1, 2, 4) read the inner SKILL.md — the canonical copy the
marketplace points at — falling back to the outer copy when the inner one
is missing. Any ✗ exits 1. Stdlib only.
"""

import argparse
import filecmp
import os
import re
import sys

KEY_RE = re.compile(r'^(\s*)([A-Za-z0-9_-]+):')

HARDCODED_PATH_PATTERNS = ('/Users/', '/home/')
SCRIPT_SUFFIXES = ('.py', '.sh')
EXEMPT_DIR_NAMES = ('tests', 'fixtures')
SIZE_WARN_THRESHOLD = 500
SIZE_FAIL_THRESHOLD = 1500

# Chinese = CJK unified ideographs (一-鿿) + CJK punctuation blocks +
# curly quotes ""''. Em-dash (U+2014) and other non-CJK punctuation are
# deliberately NOT in this set.
CJK_CODEPOINT_RANGES = (
    (0x4E00, 0x9FFF),  # CJK unified ideographs 一-鿿
    (0x3000, 0x303F),  # CJK symbols and punctuation 、。《》「」…
    (0xFF01, 0xFF64),  # fullwidth ！，：；？（） and halfwidth CJK forms
)
CHINESE_EXTRA_CHARS = frozenset('“”‘’')  # "" ''


def split_frontmatter(text):
    """Return the lines between the opening --- and the closing ---."""
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return []
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return lines[1:i]
    return []  # unterminated frontmatter


def frontmatter_has_key(fm_lines, key):
    for line in fm_lines:
        m = KEY_RE.match(line)
        if m and m.group(2) == key:
            return True
    return False


def _is_block_indicator(value):
    """True for block scalar headers: |, |-, |+, >, >-, >+."""
    return bool(value) and value[0] in '|>' and set(value) <= set('|>+-')


def _first_block_line(fm_lines, start, key_indent):
    """First non-empty line indented deeper than the key, else None."""
    for k in range(start, len(fm_lines)):
        line = fm_lines[k]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= key_indent:
            break  # dedent -> next frontmatter key
        return line.strip()
    return None


def description_trigger_line(fm_lines):
    """First non-empty line of the description value (plain or block), or None."""
    for i, line in enumerate(fm_lines):
        m = KEY_RE.match(line)
        if not m or m.group(2) != 'description':
            continue
        key_indent = len(m.group(1))
        inline = line[m.end():].strip()
        if _is_block_indicator(inline):
            return _first_block_line(fm_lines, i + 1, key_indent)
        if inline:
            return inline
        # Empty inline value: tolerate the indicator on the next line too.
        if i + 1 < len(fm_lines) and _is_block_indicator(fm_lines[i + 1].strip()):
            return _first_block_line(fm_lines, i + 2, key_indent)
        return None
    return None


def first_chinese_char(text):
    """Return the first Chinese character in text, or None."""
    for ch in text:
        if ch in CHINESE_EXTRA_CHARS:
            return ch
        cp = ord(ch)
        for lo, hi in CJK_CODEPOINT_RANGES:
            if lo <= cp <= hi:
                return ch
    return None


def scan_scripts(scripts_dir):
    """Return hardcoded-path hits as 'scripts/<relpath>:<lineno>' strings."""
    hits = []
    for dirpath, _dirnames, filenames in os.walk(scripts_dir):
        for fname in sorted(filenames):
            if not fname.endswith(SCRIPT_SUFFIXES):
                continue
            fpath = os.path.join(dirpath, fname)
            parts = os.path.relpath(fpath, scripts_dir).split(os.sep)
            if any(d in EXEMPT_DIR_NAMES for d in parts[:-1]):
                continue
            rel_display = 'scripts/' + '/'.join(parts)
            try:
                with open(fpath, encoding='utf-8', errors='replace') as f:
                    for lineno, line in enumerate(f, 1):
                        if any(p in line for p in HARDCODED_PATH_PATTERNS):
                            hits.append(f'{rel_display}:{lineno}')
                            break
            except OSError as exc:
                hits.append(f'{rel_display}: unreadable ({exc})')
    return hits


def check_skill(name, outer, inner):
    """Yield (status, message) pairs; status is 'ok', 'fail', or 'warn'."""
    # 3. mirror — byte-identical outer and inner SKILL.md.
    outer_exists = os.path.exists(outer)
    inner_exists = os.path.exists(inner)
    if outer_exists and inner_exists:
        if filecmp.cmp(outer, inner, shallow=False):
            yield 'ok', f'{name}: mirror'
        else:
            yield 'fail', f'{name}: mirror — outer and inner SKILL.md differ'
    else:
        missing = 'inner' if not inner_exists else 'outer'
        yield 'fail', f'{name}: mirror — missing {missing} SKILL.md'

    canonical = inner if inner_exists else outer
    if canonical is None:
        return
    try:
        with open(canonical, encoding='utf-8', errors='replace') as f:
            text = f.read()
    except OSError as exc:
        yield 'fail', f'{name}: license — cannot read SKILL.md ({exc})'
        return
    fm_lines = split_frontmatter(text)

    # 1. license field in frontmatter.
    if frontmatter_has_key(fm_lines, 'license'):
        yield 'ok', f'{name}: license'
    else:
        yield 'fail', f'{name}: license — frontmatter has no `license:` field'

    # 2. description trigger line.
    trigger = description_trigger_line(fm_lines)
    reasons = []
    if trigger is None:
        reasons.append('no description found in frontmatter')
    else:
        if 'use when' not in trigger.lower():
            reasons.append("no 'use when' (case-insensitive)")
        ch = first_chinese_char(trigger)
        if ch:
            reasons.append(f'contains Chinese (first: {ch})')
    if reasons:
        yield 'fail', f"{name}: description-trigger — first description line: {'; '.join(reasons)}"
    else:
        yield 'ok', f'{name}: description-trigger'

    # 4. size gate.
    n_lines = len(text.splitlines())
    if n_lines > SIZE_FAIL_THRESHOLD:
        yield 'fail', f'{name}: size — {n_lines} lines > {SIZE_FAIL_THRESHOLD}'
    else:
        yield 'ok', f'{name}: size ({n_lines} lines)'
        if n_lines > SIZE_WARN_THRESHOLD:
            yield ('warn',
                   f'{name}: size — {n_lines} lines > {SIZE_WARN_THRESHOLD} '
                   f'(FAIL above {SIZE_FAIL_THRESHOLD}); consider splitting')

    # 5. hardcoded local paths in executable scripts.
    scripts_dir = os.path.join(os.path.dirname(outer), 'scripts')
    hits = scan_scripts(scripts_dir) if os.path.isdir(scripts_dir) else []
    if hits:
        yield 'fail', f"{name}: script-paths — hardcoded home path(s): {', '.join(hits)}"
    else:
        yield 'ok', f'{name}: script-paths'


def check_collection(root):
    """Yield (status, message) pairs for every skill under root/skills/."""
    skills_dir = os.path.join(root, 'skills')
    if not os.path.isdir(skills_dir):
        print(f'error: no skills/ directory under {root}', file=sys.stderr)
        sys.exit(2)
    for name in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, name)
        if not os.path.isdir(skill_dir):
            continue
        outer = os.path.join(skill_dir, 'SKILL.md')
        inner = os.path.join(skill_dir, 'skills', name, 'SKILL.md')
        if not (os.path.exists(outer) or os.path.exists(inner)):
            continue  # not a skill directory
        yield from check_skill(name, outer, inner)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Portability lint for the skill collection.')
    parser.add_argument('--root', default='.',
                        help='collection root containing skills/ (default: .)')
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)

    marks = {'ok': '✓', 'fail': '✗', 'warn': 'WARN'}
    n_ok = n_fail = n_warn = 0
    for status, message in check_collection(root):
        print(f'{marks[status]} {message}')
        if status == 'ok':
            n_ok += 1
        elif status == 'fail':
            n_fail += 1
        else:
            n_warn += 1
    print(f'\n{n_ok + n_fail} checks: {n_fail} failed, {n_warn} warning(s)')
    return 1 if n_fail else 0


if __name__ == '__main__':
    sys.exit(main())
