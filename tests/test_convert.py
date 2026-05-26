"""
tests/test_convert.py — Validate collection-level scripts/convert.sh output

Tests multi-skill platform conversion (Cursor, Windsurf, OpenCode).
"""

import subprocess
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "convert.sh"
DIST = ROOT / "dist"


def run_convert(*args):
    result = subprocess.run(
        ["bash", str(SCRIPT)] + list(args),
        capture_output=True, text=True, cwd=str(ROOT),
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


def _skill_names():
    return [d.name for d in (ROOT / "skills").iterdir() if d.is_dir()]


class TestCheckMode:
    def test_check_passes(self):
        r = run_convert("--check")
        assert r.returncode == 0, f"--check failed:\n{r.stdout}\n{r.stderr}"
        for name in _skill_names():
            assert f"✓ {name}" in r.stdout

    def test_check_lists_all_skills(self):
        r = run_convert("--check")
        assert r.returncode == 0
        lines = [l for l in r.stdout.strip().split("\n") if l.startswith("✓")]
        assert len(lines) == len(_skill_names())


class TestConvertAll:
    @classmethod
    def setup_class(cls):
        cls.result = run_convert("--all")
        assert cls.result.returncode == 0, f"--all failed:\n{cls.result.stdout}\n{cls.result.stderr}"

    def test_cursor_dir_exists(self):
        assert (DIST / "cursor" / ".cursor" / "rules").is_dir()

    def test_windsurf_dir_exists(self):
        assert (DIST / "windsurf" / ".windsurfrules").is_dir()

    def test_opencode_dir_exists(self):
        assert (DIST / "opencode" / ".opencode" / "skills").is_dir()

    def test_each_skill_has_opencode_copy(self):
        for name in _skill_names():
            skill_dir = DIST / "opencode" / ".opencode" / "skills" / name
            assert skill_dir.is_dir(), f"Missing opencode dir for {name}"
            assert (skill_dir / "SKILL.md").is_file(), f"Missing SKILL.md for {name}"

    def test_each_skill_has_windsurf_file(self):
        ws_dir = DIST / "windsurf" / ".windsurfrules"
        for name in _skill_names():
            assert (ws_dir / f"{name}.md").is_file(), f"Missing windsurf file for {name}"

    def test_opencode_skillmd_has_frontmatter(self):
        for name in _skill_names():
            path = DIST / "opencode" / ".opencode" / "skills" / name / "SKILL.md"
            fm, _ = read_frontmatter(path)
            assert fm.get("name") == name


class TestIdempotency:
    def test_double_run_produces_same_output(self):
        run_convert("--all")
        files_before = {}
        for p in DIST.rglob("*"):
            if p.is_file():
                files_before[str(p.relative_to(DIST))] = p.read_text()

        run_convert("--all")
        for relpath, content_before in files_before.items():
            content_after = (DIST / relpath).read_text()
            assert content_after == content_before, f"Idempotency broken: {relpath}"


class TestSinglePlatform:
    def test_cursor_only(self):
        r = run_convert("--cursor")
        assert r.returncode == 0
        for name in _skill_names():
            assert f"Cursor: {name}" in r.stdout

    def test_windsurf_only(self):
        r = run_convert("--windsurf")
        assert r.returncode == 0
        for name in _skill_names():
            assert f"Windsurf: {name}" in r.stdout

    def test_opencode_only(self):
        r = run_convert("--opencode")
        assert r.returncode == 0
        for name in _skill_names():
            assert f"OpenCode: {name}" in r.stdout


class TestInvalidArgs:
    def test_invalid_flag_exits_nonzero(self):
        r = run_convert("--invalid")
        assert r.returncode != 0
