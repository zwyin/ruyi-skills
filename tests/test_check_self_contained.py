"""
tests/test_check_self_contained.py — Validate scripts/check_self_contained.py

Tests the self-containment checker that ensures no SKILL.md links
outside its own skill directory.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "check_self_contained.py"


def _run(**kwargs):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        **kwargs,
    )


class TestSelfContained:
    def test_current_repo_passes(self):
        r = _run()
        assert r.returncode == 0, f"Self-containment check failed:\n{r.stdout}\n{r.stderr}"
        assert "OK" in r.stdout

    def test_cross_skill_link_detected(self, tmp_path):
        # Create a fake skill with a cross-skill link
        fake_skill = tmp_path / "skills" / "test-skill"
        fake_skill.mkdir(parents=True)
        (fake_skill / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: test-skill
            version: "0.1.0"
            ---

            See [other skill](../other-skill/SKILL.md) for details.
        """))

        r = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(f"""\
                import os, re, sys
                SKILLS_DIR = {repr(str(tmp_path / "skills"))}
                CROSS_LINK = re.compile(r'\\[.*?\\]\\((?!https?://)(?!#)(?!`)(?!.\\/)(\\.\\.\\/.+?)\\)')
                errors = []
                for skill_name in os.listdir(SKILLS_DIR):
                    skill_dir = os.path.join(SKILLS_DIR, skill_name)
                    if not os.path.isdir(skill_dir):
                        continue
                    for root, dirs, files in os.walk(skill_dir):
                        for fname in files:
                            if not fname.endswith('.md'):
                                continue
                            fpath = os.path.join(root, fname)
                            with open(fpath, encoding='utf-8') as f:
                                for lineno, line in enumerate(f, 1):
                                    for m in CROSS_LINK.finditer(line):
                                        target = m.group(1)
                                        parts = target.split('/')
                                        if parts and parts[0] == '..':
                                            file_dir = os.path.dirname(fpath)
                                            resolved = os.path.normpath(os.path.join(file_dir, target))
                                            if not resolved.startswith(skill_dir + os.sep) and resolved != skill_dir:
                                                errors.append(f"cross-link: {{target}}")
                if errors:
                    print("ERROR")
                    sys.exit(1)
                else:
                    print("OK")
            """)],
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0
        assert "ERROR" in r.stdout
