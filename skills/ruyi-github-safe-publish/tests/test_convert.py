"""Validate scripts/convert.sh output for all platforms."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONVERT_SH = ROOT / "scripts" / "convert.sh"
DIST = ROOT / "dist"
CURSOR_RULES = DIST / "cursor" / ".cursor" / "rules"


def _run_convert(flag):
    result = subprocess.run(
        ["bash", str(CONVERT_SH), flag],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"convert.sh {flag} failed: {result.stderr}"
    return result.stdout


def _skill_version():
    import re
    text = (ROOT / "skills" / "ruyi-github-safe-publish" / "SKILL.md").read_text()
    match = re.search(r'^version:\s*"?(\d+\.\d+\.\d+)"?', text, re.MULTILINE)
    assert match
    return match.group(1)


class TestConvertCursor:
    def test_generates_per_step_files(self):
        _run_convert("--cursor")
        assert (CURSOR_RULES / "github-safe-publish-overview.mdc").exists()
        for step in range(1, 7):
            assert (CURSOR_RULES / f"github-safe-publish-step{step}.mdc").exists()
        assert (CURSOR_RULES / "github-safe-publish-modules.mdc").exists()

    def test_overview_has_yaml_frontmatter(self):
        _run_convert("--cursor")
        content = (CURSOR_RULES / "github-safe-publish-overview.mdc").read_text()
        assert content.startswith("---\n")
        assert "description:" in content
        assert "alwaysApply: false" in content

    def test_step_files_contain_step_content(self):
        _run_convert("--cursor")
        for step in range(1, 7):
            content = (CURSOR_RULES / f"github-safe-publish-step{step}.mdc").read_text()
            assert f"Step {step}" in content, f"step{step}.mdc missing 'Step {step}'"

    def test_modules_mdc_contains_optional_modules(self):
        _run_convert("--cursor")
        content = (CURSOR_RULES / "github-safe-publish-modules.mdc").read_text()
        assert "SEO" in content or "seo" in content.lower()
        assert "CI" in content or "ci" in content.lower()

    def test_version_in_all_files(self):
        _run_convert("--cursor")
        version = _skill_version()
        for f in CURSOR_RULES.glob("*.mdc"):
            content = f.read_text()
            assert version in content, f"{f.name} missing version {version}"

    def test_no_monolithic_file(self):
        _run_convert("--cursor")
        assert not (CURSOR_RULES / "github-safe-publish.mdc").exists()

    def test_step_files_reasonable_size(self):
        _run_convert("--cursor")
        for f in CURSOR_RULES.glob("github-safe-publish-step*.mdc"):
            lines = f.read_text().count("\n")
            assert lines < 300, f"{f.name} has {lines} lines, should be < 300"


class TestConvertWindsurf:
    def test_generates_windsurfrules(self):
        _run_convert("--windsurf")
        assert (DIST / "windsurf" / ".windsurfrules").exists()

    def test_windsurfrules_is_markdown(self):
        _run_convert("--windsurf")
        content = (DIST / "windsurf" / ".windsurfrules").read_text()
        assert content.startswith("#")
        assert "GitHub Safe Publish" in content

    def test_windsurfrules_has_version(self):
        _run_convert("--windsurf")
        content = (DIST / "windsurf" / ".windsurfrules").read_text()
        version = _skill_version()
        assert version in content


class TestConvertOpenCode:
    def test_generates_agents_md(self):
        _run_convert("--opencode")
        assert (DIST / "opencode" / "AGENTS.md").exists()

    def test_agents_md_is_markdown(self):
        _run_convert("--opencode")
        content = (DIST / "opencode" / "AGENTS.md").read_text()
        assert content.startswith("#")
        assert "GitHub Safe Publish" in content

    def test_agents_md_has_version(self):
        _run_convert("--opencode")
        content = (DIST / "opencode" / "AGENTS.md").read_text()
        version = _skill_version()
        assert version in content


class TestConvertAll:
    def test_all_generates_all_formats(self):
        _run_convert("--all")
        assert (CURSOR_RULES / "github-safe-publish-step1.mdc").exists()
        assert (DIST / "windsurf" / ".windsurfrules").exists()
        assert (DIST / "opencode" / "AGENTS.md").exists()

    def test_list_flag(self):
        output = _run_convert("--list")
        assert "cursor" in output.lower()
        assert "windsurf" in output.lower()
        assert "opencode" in output.lower()
