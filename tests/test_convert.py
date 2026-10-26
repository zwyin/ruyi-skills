"""
tests/test_convert.py — Validate collection-level scripts/convert.sh output

Tests multi-skill platform conversion (Cursor, Windsurf, OpenCode).
"""

import shutil
import subprocess
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "convert.sh"
DIST = ROOT / "dist"


def find_skill_md(skill_dir):
    """Source convert.sh (main dispatch guarded) and call _find_skill_md directly."""
    cmd = f'source "{SCRIPT}" >/dev/null 2>&1 && _find_skill_md "{skill_dir}"'
    result = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


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

    def test_each_skill_has_codex_copy(self):
        """Codex natively reads SKILL.md, so --all emits dist/codex/<name>/SKILL.md."""
        for name in _skill_names():
            skill_dir = DIST / "codex" / name
            assert skill_dir.is_dir(), f"Missing codex dir for {name}"
            assert (skill_dir / "SKILL.md").is_file(), f"Missing SKILL.md for {name}"

    def test_codex_copy_matches_canonical_skillmd(self):
        for name in _skill_names():
            out = DIST / "codex" / name / "SKILL.md"
            canonical = Path(find_skill_md(ROOT / "skills" / name))
            assert canonical, f"No canonical SKILL.md resolved for {name}"
            assert out.read_text() == canonical.read_text(), \
                f"codex SKILL.md differs from canonical for {name}"


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

    def test_codex_only(self):
        r = run_convert("--codex")
        assert r.returncode == 0, f"--codex failed:\n{r.stdout}\n{r.stderr}"
        for name in _skill_names():
            assert f"Codex: {name}" in r.stdout
            out = DIST / "codex" / name / "SKILL.md"
            assert out.is_file(), f"Missing codex SKILL.md for {name}"
            canonical = Path(find_skill_md(ROOT / "skills" / name))
            assert out.read_text() == canonical.read_text(), \
                f"codex SKILL.md differs from canonical for {name}"


class TestInvalidArgs:
    def test_invalid_flag_exits_nonzero(self):
        r = run_convert("--invalid")
        assert r.returncode != 0


class TestFindSkillMd:
    def test_prefers_nested_canonical(self):
        """skills/<name>/skills/<name>/SKILL.md wins over the outer copy."""
        for name in _skill_names():
            nested = ROOT / "skills" / name / "skills" / name / "SKILL.md"
            if nested.is_file():
                assert find_skill_md(ROOT / "skills" / name) == str(nested), \
                    f"{name}: expected canonical nested SKILL.md"

    def test_evals_fixture_trap_resolves_canonical(self):
        """evals/fixtures demo SKILL.md must never shadow the canonical file."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "trap-skill"
            # Create the trap first so a naive `find | head -n 1` can pick it
            trap = skill / "evals" / "fixtures" / "fixture-1" / "skills" / "demo-skill" / "skills" / "demo-skill" / "SKILL.md"
            trap.parent.mkdir(parents=True)
            trap.write_text('---\nname: demo-skill\nversion: "0.0.1"\n---\ndemo\n')
            canonical = skill / "skills" / "trap-skill" / "SKILL.md"
            canonical.parent.mkdir(parents=True)
            canonical.write_text('---\nname: trap-skill\nversion: "1.0.0"\n---\nbody\n')
            resolved = find_skill_md(skill)
            assert resolved == str(canonical)
            assert "evals" not in resolved

    def test_outer_fallback_when_no_nested(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "flat-skill"
            trap = skill / "evals" / "fixtures" / "f" / "SKILL.md"
            trap.parent.mkdir(parents=True)
            trap.write_text('---\nname: demo-skill\nversion: "0.0.1"\n---\ndemo\n')
            outer = skill / "SKILL.md"
            outer.write_text('---\nname: flat-skill\nversion: "1.0.0"\n---\nbody\n')
            assert find_skill_md(skill) == str(outer)

    def test_only_evals_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "broken-skill"
            trap = skill / "evals" / "fixtures" / "f" / "SKILL.md"
            trap.parent.mkdir(parents=True)
            trap.write_text('---\nname: demo-skill\nversion: "0.0.1"\n---\ndemo\n')
            assert find_skill_md(skill) == ""


class TestConvertAllNoDemoArtifacts:
    def test_all_after_clean_leaves_no_demo_artifacts(self):
        """A clean --all rebuild must not emit evals-fixture (demo-skill) artifacts."""
        shutil.rmtree(DIST, ignore_errors=True)
        r = run_convert("--all")
        assert r.returncode == 0, f"--all failed:\n{r.stdout}\n{r.stderr}"
        leftovers = [str(p.relative_to(DIST)) for p in DIST.rglob("*") if "demo-skill" in p.name]
        assert leftovers == [], f"demo artifacts leaked into dist/: {leftovers}"
