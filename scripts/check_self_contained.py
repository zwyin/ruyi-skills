#!/usr/bin/env python3
"""Check that no SKILL.md or references/ file links outside its skill directory."""

import os
import re
import sys

SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'skills')
SKILLS_DIR = os.path.normpath(SKILLS_DIR)

# Patterns that indicate cross-skill or external links
CROSS_LINK = re.compile(r'\[.*?\]\((?!https?://)(?!#)(?!`)(?!\./)(\.\./.+?)\)')

errors = []

for skill_name in os.listdir(SKILLS_DIR):
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    if not os.path.isdir(skill_dir):
        continue

    for root, dirs, files in os.walk(skill_dir):
        # Only check .md files in skill root and references/
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, SKILLS_DIR)

            with open(fpath, encoding='utf-8') as f:
                for lineno, line in enumerate(f, 1):
                    for m in CROSS_LINK.finditer(line):
                        target = m.group(1)
                        # Check if target goes outside skill directory
                        parts = target.split('/')
                        if parts and parts[0] == '..':
                            # Goes up - check if it leaves the skill dir
                            file_dir = os.path.dirname(fpath)
                            resolved = os.path.normpath(os.path.join(file_dir, target))
                            if not resolved.startswith(skill_dir + os.sep) and resolved != skill_dir:
                                errors.append(f"{relpath}:{lineno}: cross-skill link: {target}")

if errors:
    print("ERROR: Found cross-skill links (violates self-containment rule):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("OK: All skills are self-contained.")
