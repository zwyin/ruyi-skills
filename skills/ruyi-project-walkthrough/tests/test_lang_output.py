"""
--lang 参数输出语言验证测试

验证 4 种语言模式的产出特征：
- zh 模式：中文正文 + 英文术语保留
- zh-pure 模式：纯中文，术语尽量翻译
- en 模式：纯英文输出
- bilingual 模式：中英对照
"""

import re
import pytest
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = (SKILL_ROOT / "tests" / "fixtures") if (SKILL_ROOT / "tests" / "fixtures").is_dir() and any((SKILL_ROOT / "tests" / "fixtures").iterdir()) else (SKILL_ROOT / "examples")

_CANDIDATE_BRIEF = ["zod", "fastapi", "bat"]
BRIEF_PROJECTS = [p for p in _CANDIDATE_BRIEF if (EXAMPLES_DIR / p).is_dir()]

# Chinese character detection
ZH_PATTERN = re.compile(r'[一-鿿]')
# Technical term patterns that should stay in English
TECH_PATTERNS = [
    re.compile(r'// Simplified from:'),  # source citations always English
    re.compile(r'\.md\b'),               # file extensions
    re.compile(r'\.py\b'),
    re.compile(r'\.json\b'),
]


@pytest.fixture(params=BRIEF_PROJECTS)
def project_docs(request):
    """Return docs directory for a brief project"""
    docs = EXAMPLES_DIR / request.param / "docs"
    if not docs.is_dir():
        pytest.skip(f"{request.param} has no docs/")
    return docs


def _read_all_md(docs_dir):
    """Read all markdown files in a directory"""
    texts = []
    for md in sorted(docs_dir.glob("*.md")):
        texts.append(md.read_text(encoding="utf-8"))
    return texts


class TestDefaultLangIsZh:
    """Default (no --lang specified) should produce Chinese output"""

    def test_has_chinese_in_prose(self, project_docs):
        """At least one chapter should contain Chinese characters"""
        texts = _read_all_md(project_docs)
        has_zh = any(ZH_PATTERN.search(t) for t in texts)
        assert has_zh, "Default output should contain Chinese characters"

    def test_source_citations_in_english(self, project_docs):
        """Source citations should always be in English"""
        texts = _read_all_md(project_docs)
        for text in texts:
            citations = re.findall(r'// Simplified from:.*', text)
            for c in citations:
                assert not ZH_PATTERN.search(c), f"Citation should be English: {c}"

    def test_file_paths_in_english(self, project_docs):
        """File paths in output should not contain Chinese"""
        texts = _read_all_md(project_docs)
        for text in texts:
            # Match common path patterns like src/xxx, .claude/xxx, etc
            paths = re.findall(r'(?:src|lib|test|docs|\.claude|\.cursor)/[\w./-]+', text)
            for p in paths:
                assert not ZH_PATTERN.search(p), f"Path should be English: {p}"


class TestDocumentationStandards:
    """Verify documentation-standards.md has all lang modes"""

    def test_standards_file_exists(self):
        path = SKILL_ROOT / "docs" / "documentation-standards.md"
        assert path.is_file()

    def test_has_all_lang_modes(self):
        path = SKILL_ROOT / "docs" / "documentation-standards.md"
        content = path.read_text()
        assert "`zh`" in content, "Should define zh mode"
        assert "`zh-pure`" in content, "Should define zh-pure mode"
        assert "`en`" in content, "Should define en mode"
        assert "`bilingual`" in content, "Should define bilingual mode"

    def test_has_lang_section(self):
        path = SKILL_ROOT / "docs" / "documentation-standards.md"
        content = path.read_text()
        assert "Language" in content or "language" in content


class TestManifestSchemaHasLang:
    """Verify manifest schema includes lang field with all 4 modes"""

    def test_schema_has_lang(self):
        import json
        path = SKILL_ROOT / "docs" / "sources-manifest.schema.json"
        schema = json.loads(path.read_text())
        assert "lang" in schema["properties"], "Schema should have lang field"
        assert schema["properties"]["lang"]["enum"] == ["zh", "zh-pure", "en", "bilingual"]


class TestSkillDefinesAllLangModes:
    """Verify SKILL.md defines all 4 language modes"""

    @pytest.fixture
    def skill_content(self):
        path = SKILL_ROOT / "skills" / "project-walkthrough" / "SKILL.md"
        return path.read_text()

    def test_lang_param_has_4_modes(self, skill_content):
        assert "--lang zh|zh-pure|en|bilingual" in skill_content, \
            "argument-hint should list all 4 lang modes"

    def test_lang_parameter_docs(self, skill_content):
        assert "`zh-pure`" in skill_content, "Should document zh-pure mode"
        assert "`bilingual`" in skill_content, "Should document bilingual mode"

    def test_lang_q5_in_phase0(self, skill_content):
        assert "Q5: Output Language" in skill_content, \
            "Phase 0.3 should have Q5 language selection"

    def test_lang_mode_sections(self, skill_content):
        for mode in ["`zh`", "`zh-pure`", "`en`", "`bilingual`"]:
            # Each mode should have a ### heading
            assert f"### {mode}" in skill_content, f"Should have section for {mode}"


class TestVersionFlag:
    """Verify --version flag is properly defined"""

    @pytest.fixture
    def skill_content(self):
        path = SKILL_ROOT / "skills" / "project-walkthrough" / "SKILL.md"
        return path.read_text()

    @pytest.fixture
    def skill_version(self):
        """Extract version from SKILL.md frontmatter"""
        path = SKILL_ROOT / "skills" / "project-walkthrough" / "SKILL.md"
        import re
        m = re.search(r'^version:\s*"([^"]+)"', path.read_text(), re.MULTILINE)
        return m.group(1) if m else None

    def test_version_in_frontmatter(self, skill_content, skill_version):
        assert skill_version, "Frontmatter should have version field"
        assert f'version: "{skill_version}"' in skill_content

    def test_version_flag_in_usage(self, skill_content):
        assert "--version" in skill_content, "Should define --version flag"

    def test_version_flag_is_standalone(self, skill_content):
        # Find the line describing --version as standalone
        for line in skill_content.split("\n"):
            if "--version" in line and "standalone" in line.lower():
                return
        pytest.fail("--version should be documented as standalone flag")

    def test_version_example_exists(self, skill_content):
        assert "/project-walkthrough --version" in skill_content, \
            "Should have --version usage example"

    def test_version_startup_message(self, skill_content, skill_version):
        assert f"v{skill_version}" in skill_content, \
            "Should reference version in startup output"
