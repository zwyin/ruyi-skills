"""
tests/test_check_portability.py — Validate scripts/check_portability.py

Covers the five portability checks (license, description trigger line,
mirror, size gate, hardcoded script paths). Each check has at least one
passing and one failing case, built from minimal tmp_path skill trees.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "check_portability.py"

# A fully compliant skill: license present, English single-line description
# containing "Use when" (no colon — pins the口径), small body.
GOOD_FRONTMATTER = """\
---
name: demo
version: "0.1.0"
license: MIT
description: Generate a demo report from any input. Use when the user asks for a structured summary.
argument-hint: "[path]"
---

# Demo

Body text.
"""

# Block-scalar description (safe-publish shape): first non-empty line is
# Chinese -> must fail the trigger check even though a later line has
# "Use when".
CHINESE_BLOCK_DESCRIPTION = """\
---
name: demo
version: "0.1.0"
license: MIT
description: |
  将本地 Git 项目安全地发布到 GitHub 公开仓库。包含两层脱敏扫描。
  Use when: "push to github", "publish to github".
argument-hint: "[--scan]"
---

# Demo

Body text.
"""


def _run(root):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def _make_skill(root, name="demo", outer=None, inner=None, scripts=None):
    """Build a minimal two-layer skill tree under root/skills/<name>."""
    skill_root = root / "skills" / name
    inner_dir = skill_root / "skills" / name
    inner_dir.mkdir(parents=True, exist_ok=True)
    content = inner if inner is not None else GOOD_FRONTMATTER
    (inner_dir / "SKILL.md").write_text(content, encoding="utf-8")
    outer_content = outer if outer is not None else content
    (skill_root / "SKILL.md").write_text(outer_content, encoding="utf-8")
    for rel, text in (scripts or {}).items():
        target = skill_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return skill_root


def _replace_description(new_description):
    old = "description: Generate a demo report from any input. Use when the user asks for a structured summary."
    assert old in GOOD_FRONTMATTER
    return GOOD_FRONTMATTER.replace(old, f"description: {new_description}")


def _exact_line_count(frontmatter_text, total):
    """Return a SKILL.md string with exactly `total` lines."""
    lines = frontmatter_text.splitlines()
    assert len(lines) <= total
    filler = ["filler line"] * (total - len(lines))
    return "\n".join(lines + filler) + "\n"


class TestLicense:
    def test_license_present_passes(self, tmp_path):
        _make_skill(tmp_path)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "✓ demo: license" in r.stdout

    def test_missing_license_fails(self, tmp_path):
        content = GOOD_FRONTMATTER.replace("license: MIT\n", "")
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: license" in r.stdout


class TestDescriptionTrigger:
    def test_use_when_without_colon_and_with_em_dash_passes(self, tmp_path):
        # Pins the口径: 'use when' needs no colon, is case-insensitive, and
        # em-dash (—) is NOT Chinese.
        content = _replace_description(
            "Generate a demo report — any input. Use when user wants a summary."
        )
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: description-trigger" in r.stdout

    def test_lowercase_use_when_passes(self, tmp_path):
        content = _replace_description("Analyze a project. use when asked for a study.")
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: description-trigger" in r.stdout

    def test_chinese_block_scalar_first_line_fails(self, tmp_path):
        # safe-publish shape: first non-empty description line is Chinese.
        _make_skill(tmp_path, inner=CHINESE_BLOCK_DESCRIPTION)
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: description-trigger" in r.stdout

    def test_english_line_without_use_when_fails(self, tmp_path):
        content = _replace_description(
            "Publish a local Git project to a public GitHub repository safely."
        )
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: description-trigger" in r.stdout

    def test_chinese_punctuation_in_first_line_fails(self, tmp_path):
        # Fullwidth comma (，) counts as Chinese even in an English sentence
        # that does contain 'use when'.
        content = _replace_description(
            "Generate a report，then stop. Use when asked for a summary."
        )
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: description-trigger" in r.stdout


class TestMirror:
    def test_identical_layers_pass(self, tmp_path):
        _make_skill(tmp_path)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: mirror" in r.stdout

    def test_drifted_layers_fail(self, tmp_path):
        _make_skill(
            tmp_path,
            outer=GOOD_FRONTMATTER + "\nouter-only drift line\n",
        )
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: mirror" in r.stdout
        # Content checks read the inner (canonical) copy, which is good.
        assert "✓ demo: license" in r.stdout

    def test_missing_inner_skill_md_fails(self, tmp_path):
        skill_root = _make_skill(tmp_path)
        (skill_root / "skills" / "demo" / "SKILL.md").unlink()
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: mirror" in r.stdout
        # Outer copy still exists, so content checks still run.
        assert "✓ demo: license" in r.stdout

    def test_missing_outer_skill_md_fails(self, tmp_path):
        skill_root = _make_skill(tmp_path)
        (skill_root / "SKILL.md").unlink()
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: mirror" in r.stdout


class TestSize:
    def test_small_file_passes_without_warning(self, tmp_path):
        _make_skill(tmp_path)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: size" in r.stdout
        assert "WARN" not in r.stdout

    def test_oversize_between_500_and_1500_warns_but_passes(self, tmp_path):
        content = _exact_line_count(GOOD_FRONTMATTER, 600)
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: size" in r.stdout
        assert "WARN demo: size" in r.stdout

    def test_exactly_1500_lines_warns_but_passes(self, tmp_path):
        content = _exact_line_count(GOOD_FRONTMATTER, 1500)
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: size" in r.stdout
        assert "WARN demo: size" in r.stdout

    def test_exactly_1501_lines_fails(self, tmp_path):
        content = _exact_line_count(GOOD_FRONTMATTER, 1501)
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: size" in r.stdout


class TestScriptPaths:
    def test_clean_scripts_pass(self, tmp_path):
        _make_skill(tmp_path, scripts={"scripts/foo.sh": "#!/bin/bash\nls -la\n"})
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: script-paths" in r.stdout

    def test_users_path_in_shell_script_fails(self, tmp_path):
        _make_skill(
            tmp_path,
            scripts={"scripts/foo.sh": "#!/bin/bash\ncp /Users/alice/secret.txt /tmp/\n"},
        )
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: script-paths" in r.stdout
        assert "foo.sh" in r.stdout

    def test_home_path_in_nested_python_script_fails(self, tmp_path):
        _make_skill(
            tmp_path,
            scripts={"scripts/deep/mod.py": "DATA = '/home/bob/data'\n"},
        )
        r = _run(tmp_path)
        assert r.returncode == 1
        assert "✗ demo: script-paths" in r.stdout
        assert "mod.py" in r.stdout

    def test_tests_and_fixtures_dirs_exempt(self, tmp_path):
        _make_skill(
            tmp_path,
            scripts={
                "scripts/tests/test_run.py": "EXPECTED = '/Users/alice/out'\n",
                "scripts/fixtures/env.sh": "export REF=/home/bob/env\n",
            },
        )
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: script-paths" in r.stdout

    def test_skill_md_teaching_text_not_scanned(self, tmp_path):
        # /Users/xxx/ inside SKILL.md is rule-teaching text, not a hardcoded
        # local path — the path scan must not read SKILL.md.
        content = GOOD_FRONTMATTER + "\nRule: scrub paths like /Users/xxx/ before publish.\n"
        _make_skill(tmp_path, inner=content)
        r = _run(tmp_path)
        assert r.returncode == 0, r.stdout
        assert "✓ demo: script-paths" in r.stdout


class TestAggregation:
    def test_multiple_failures_all_reported(self, tmp_path):
        content = GOOD_FRONTMATTER.replace("license: MIT\n", "")
        content = _replace_description_in(
            content, "将项目发布到 GitHub。Use when asked to publish."
        )
        _make_skill(
            tmp_path,
            inner=content,
            outer=content + "\ndrift\n",
            scripts={"scripts/run.sh": "#!/bin/bash\nrm -rf /Users/alice/tmp\n"},
        )
        r = _run(tmp_path)
        assert r.returncode == 1
        for fail in (
            "✗ demo: license",
            "✗ demo: description-trigger",
            "✗ demo: mirror",
            "✗ demo: script-paths",
        ):
            assert fail in r.stdout, f"missing {fail} in:\n{r.stdout}"

    def test_missing_skills_dir_errors(self, tmp_path):
        r = _run(tmp_path)
        assert r.returncode != 0
        assert "skills" in (r.stderr + r.stdout).lower()


def _replace_description_in(text, new_description):
    old = "description: Generate a demo report from any input. Use when the user asks for a structured summary."
    assert old in text
    return text.replace(old, f"description: {new_description}")
