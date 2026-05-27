"""
tests/test_convert.py — Validate scripts/convert.sh output

Ensures all platform-specific skill files are generated correctly
from the canonical SKILL.md.

Usage:
  pytest tests/test_convert.py -v
"""

import subprocess
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "convert.sh"
SKILL_MD = ROOT / "skills" / "ruyi-project-walkthrough/SKILL.md"
CURSOR_FILE = ROOT / "cursor" / "ruyi-project-walkthrough.mdc"
WINDSURF_FILE = ROOT / ".windsurf" / "rules" / "ruyi-project-walkthrough.md"
OPENCODE_FILE = ROOT / ".opencode" / "skills" / "ruyi-project-walkthrough" / "SKILL.md"
MAX_WINDSURF_CHARS = 12000


def run_convert(*args):
    result = subprocess.run(
        ["bash", str(SCRIPT)] + list(args),
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return result


def read_frontmatter(path):
    text = path.read_text()
    match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return {}, text
    fm = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    body = text[match.end():].lstrip("\n")
    return fm, body


def extract_canonical_body():
    _, body = read_frontmatter(SKILL_MD)
    return body


class TestCursorFile:
    def test_exists(self):
        assert CURSOR_FILE.is_file()

    def test_frontmatter_has_description(self):
        fm, _ = read_frontmatter(CURSOR_FILE)
        assert "description" in fm
        assert "walk through" in fm["description"].lower()

    def test_frontmatter_has_alwaysApply_false(self):
        fm, _ = read_frontmatter(CURSOR_FILE)
        assert fm.get("alwaysApply") == "false"

    def test_body_matches_canonical(self):
        _, cursor_body = read_frontmatter(CURSOR_FILE)
        canonical = extract_canonical_body()
        assert cursor_body.strip() == canonical.strip()


class TestWindsurfFile:
    def test_exists(self):
        assert WINDSURF_FILE.is_file()

    def test_frontmatter_has_trigger(self):
        fm, _ = read_frontmatter(WINDSURF_FILE)
        assert fm.get("trigger") == "model_decision"

    def test_frontmatter_has_description(self):
        fm, _ = read_frontmatter(WINDSURF_FILE)
        assert "description" in fm
        assert "walk through" in fm["description"].lower()

    def test_under_char_limit(self):
        chars = WINDSURF_FILE.stat().st_size
        assert chars <= MAX_WINDSURF_CHARS, \
            f"Windsurf file is {chars} chars, limit is {MAX_WINDSURF_CHARS}"

    def test_no_innerhtml(self):
        content = WINDSURF_FILE.read_text()
        assert "innerHTML" not in content


class TestOpenCodeFile:
    def test_exists(self):
        assert OPENCODE_FILE.is_file()

    def test_frontmatter_has_name(self):
        fm, _ = read_frontmatter(OPENCODE_FILE)
        assert fm.get("name") == "ruyi-project-walkthrough"

    def test_frontmatter_has_license(self):
        fm, _ = read_frontmatter(OPENCODE_FILE)
        assert fm.get("license") == "MIT"

    def test_frontmatter_has_compatibility(self):
        fm, _ = read_frontmatter(OPENCODE_FILE)
        assert fm.get("compatibility") == "opencode"

    def test_body_matches_canonical(self):
        _, opencode_body = read_frontmatter(OPENCODE_FILE)
        canonical = extract_canonical_body()
        assert opencode_body.strip() == canonical.strip()


class TestConvertScript:
    def test_check_mode_passes(self):
        result = run_convert("--check")
        assert result.returncode == 0, \
            f"--check failed:\n{result.stdout}\n{result.stderr}"
        assert "All platforms in sync" in result.stdout

    def test_regenerate_idempotent(self):
        result1 = run_convert("all")
        assert result1.returncode == 0
        cursor_before = CURSOR_FILE.read_text()
        opencode_before = OPENCODE_FILE.read_text()
        windsurf_before = WINDSURF_FILE.read_text()

        result2 = run_convert("all")
        assert result2.returncode == 0
        assert CURSOR_FILE.read_text() == cursor_before
        assert OPENCODE_FILE.read_text() == opencode_before
        assert WINDSURF_FILE.read_text() == windsurf_before

    def test_single_platform_cursor(self):
        result = run_convert("cursor")
        assert result.returncode == 0
        assert "Cursor" in result.stdout

    def test_single_platform_windsurf(self):
        result = run_convert("windsurf")
        assert result.returncode == 0
        assert "Windsurf" in result.stdout

    def test_single_platform_opencode(self):
        result = run_convert("opencode")
        assert result.returncode == 0
        assert "OpenCode" in result.stdout

    def test_invalid_arg_exits_nonzero(self):
        result = run_convert("invalid_platform")
        assert result.returncode != 0
