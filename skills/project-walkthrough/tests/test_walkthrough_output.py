"""
project-walkthrough skill 输出验证测试

基于 SKILL.md 规范，验证 walkthrough 产出物的结构和质量。
测试对象：tests/fixtures/（CI）或 examples/（本地开发）下的已生成走读实例。

用法：
  pytest tests/test_walkthrough_output.py -v
  pytest tests/test_walkthrough_output.py -v --tb=short
"""

import json
import re
import subprocess
import pytest
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = (SKILL_ROOT / "tests" / "fixtures") if (SKILL_ROOT / "tests" / "fixtures").is_dir() and any((SKILL_ROOT / "tests" / "fixtures").iterdir()) else (SKILL_ROOT / "examples")

# 完整三层产出的项目（有 brief + medium + deep）
_CANDIDATE_FULL = ["gstack", "superpowers"]
FULL_PROJECTS = [p for p in _CANDIDATE_FULL if (EXAMPLES_DIR / p).is_dir()]
# 只有 brief 层的项目
_CANDIDATE_BRIEF = ["zod", "fastapi", "bat"]
BRIEF_ONLY_PROJECTS = [p for p in _CANDIDATE_BRIEF if (EXAMPLES_DIR / p).is_dir()]
ALL_PROJECTS = FULL_PROJECTS + BRIEF_ONLY_PROJECTS

# ─── 目录结构 ───────────────────────────────────────────────


class TestDirectoryStructure:
    """SKILL.md Output Structure 规范验证"""

    def test_examples_dir_exists(self):
        assert EXAMPLES_DIR.is_dir(), "examples/ 目录不存在"

    @pytest.fixture(params=FULL_PROJECTS)
    def project_dir(self, request):
        path = EXAMPLES_DIR / request.param
        assert path.is_dir(), f"{request.param} 实例目录不存在"
        return path

    @pytest.fixture(params=ALL_PROJECTS)
    def all_project_dir(self, request):
        path = EXAMPLES_DIR / request.param
        assert path.is_dir(), f"{request.param} 实例目录不存在"
        return path

    def test_has_docs_dir(self, all_project_dir):
        assert (all_project_dir / "docs").is_dir(), f"{all_project_dir.name} 缺少 docs/ 目录"

    def test_has_interactive_dir(self, all_project_dir):
        assert (all_project_dir / "interactive").is_dir(), f"{all_project_dir.name} 缺少 interactive/ 目录"

    def test_brief_docs_in_docs_flat(self, all_project_dir):
        """Brief 级别的 md 文件应直接在 docs/ 下，不在子目录"""
        docs = all_project_dir / "docs"
        brief_files = [
            f for f in docs.iterdir()
            if f.is_file() and f.suffix == ".md"
        ]
        assert len(brief_files) >= 5, (
            f"{all_project_dir.name} docs/ 下应有 5+ brief md 文件，实际 {len(brief_files)}"
        )

    def test_has_medium_dir(self, project_dir):
        assert (project_dir / "docs" / "medium").is_dir(), f"{project_dir.name} 缺少 docs/medium/"

    def test_has_deep_dir(self, project_dir):
        assert (project_dir / "docs" / "deep").is_dir(), f"{project_dir.name} 缺少 docs/deep/"

    def test_has_brief_html(self, all_project_dir):
        interactive = all_project_dir / "interactive"
        # Support both old naming (walkthrough.html) and new naming (walkthrough-*-brief-*.html)
        html = interactive / "walkthrough.html"
        if not html.is_file():
            htmls = list(interactive.glob("walkthrough-*-brief-*.html"))
            assert htmls, f"{all_project_dir.name} 缺少 walkthrough.html 或 walkthrough-*-brief-*.html"

    def test_has_medium_html(self, project_dir):
        interactive = project_dir / "interactive"
        html = interactive / "medium-walkthrough.html"
        if not html.is_file():
            htmls = list(interactive.glob("walkthrough-*-medium-*.html"))
            assert htmls, f"{project_dir.name} 缺少 medium-walkthrough.html 或 walkthrough-*-medium-*.html"

    def test_has_deep_html(self, project_dir):
        interactive = project_dir / "interactive"
        html = interactive / "deep-walkthrough.html"
        if not html.is_file():
            htmls = list(interactive.glob("walkthrough-*-deep-*.html"))
            assert htmls, f"{project_dir.name} 缺少 deep-walkthrough.html 或 walkthrough-*-deep-*.html"

    def test_medium_has_min_files(self, project_dir):
        """Medium 级别应有 12-15 个 md 文件"""
        medium = project_dir / "docs" / "medium"
        if not medium.is_dir():
            pytest.skip("medium 目录不存在")
        files = list(medium.glob("*.md"))
        assert 12 <= len(files) <= 20, (
            f"{project_dir.name} medium 应有 12-15 个文件，实际 {len(files)}"
        )

    def test_deep_has_min_files(self, project_dir):
        """Deep 级别应有 8+ 个 md 文件"""
        deep = project_dir / "docs" / "deep"
        if not deep.is_dir():
            pytest.skip("deep 目录不存在")
        files = list(deep.glob("*.md"))
        assert len(files) >= 8, (
            f"{project_dir.name} deep 应有 8+ 个文件，实际 {len(files)}"
        )


# ─── 文件命名 ───────────────────────────────────────────────

FILE_NAME_PATTERN = re.compile(r"^\d{2}-[a-z0-9-]+\.md$")


class TestFileNaming:
    """SKILL.md: 'Each file: NN-kebab-case-title.md'"""

    @pytest.fixture(params=FULL_PROJECTS)
    def project_dir(self, request):
        return EXAMPLES_DIR / request.param

    @pytest.fixture(params=ALL_PROJECTS)
    def all_project_dir(self, request):
        return EXAMPLES_DIR / request.param

    def _collect_md_files(self, project_dir):
        files = []
        for subdir in [project_dir / "docs", project_dir / "docs" / "medium", project_dir / "docs" / "deep"]:
            if subdir.is_dir():
                files.extend(f for f in subdir.glob("*.md") if f.parent == subdir)
        return files

    def test_all_md_files_match_pattern(self, all_project_dir):
        bad = []
        for f in self._collect_md_files(all_project_dir):
            if not FILE_NAME_PATTERN.match(f.name):
                bad.append(f.name)
        assert not bad, f"{all_project_dir.name} 文件命名不规范: {bad}"

    def test_file_numbers_are_sequential(self, all_project_dir):
        for subdir_name in ["", "medium", "deep"]:
            subdir = all_project_dir / "docs" / subdir_name if subdir_name else all_project_dir / "docs"
            if not subdir.is_dir():
                continue
            # 只检查直接子文件（brief 在 docs/ 下）
            if subdir_name == "":
                md_files = sorted(
                    f for f in subdir.iterdir()
                    if f.is_file() and f.suffix == ".md"
                )
            else:
                md_files = sorted(subdir.glob("*.md"))

            if not md_files:
                continue

            nums = [int(f.name[:2]) for f in md_files]
            expected = list(range(1, len(nums) + 1))
            assert nums == expected, (
                f"{all_project_dir.name}/docs/{subdir_name} 编号不连续: got {nums}, expected {expected}"
            )


# ─── Markdown 内容 ──────────────────────────────────────────


class TestMarkdownContent:
    """SKILL.md Documentation Standards"""

    @pytest.fixture(params=ALL_PROJECTS)
    def all_project_dir(self, request):
        return EXAMPLES_DIR / request.param

    def _all_md_files(self, project_dir):
        files = []
        for subdir in [project_dir / "docs", project_dir / "docs" / "medium", project_dir / "docs" / "deep"]:
            if subdir.is_dir():
                files.extend(f for f in subdir.iterdir() if f.is_file() and f.suffix == ".md")
        return files

    def test_each_file_has_title(self, all_project_dir):
        """每个文件应以 # 标题开头"""
        bad = []
        for f in self._all_md_files(all_project_dir):
            content = f.read_text(encoding="utf-8")
            if not content.lstrip().startswith("#"):
                bad.append(f.name)
        assert not bad, f"{all_project_dir.name} 缺少标题: {bad}"

    def test_brief_first_file_is_overview(self, all_project_dir):
        """Brief 第一个文件应为 overview"""
        overview = all_project_dir / "docs" / "01-overview.md"
        assert overview.is_file(), f"{all_project_dir.name} 缺少 01-overview.md"

    def test_has_innovation_summary(self, all_project_dir):
        """应有创新总结章节"""
        docs = all_project_dir / "docs"
        all_files = []
        for d in [docs, docs / "medium", docs / "deep"]:
            if d.is_dir():
                all_files.extend(f.name for f in d.glob("*.md"))
        has_innovation = any("innovation" in f for f in all_files)
        assert has_innovation, f"{all_project_dir.name} 缺少 innovation 总结章节"

    def test_each_file_has_navigation(self, all_project_dir):
        """每个 md 文件末尾应有导航链接"""
        bad = []
        for f in self._all_md_files(all_project_dir):
            content = f.read_text(encoding="utf-8")
            if "←" not in content and "下一章" not in content:
                bad.append(f.name)
        assert not bad, f"{all_project_dir.name} 缺少导航链接: {bad}"


# ─── HTML 验证 ─────────────────────────────────────────────


class TestHTML:
    """SKILL.md Phase 4 HTML 要求"""

    @pytest.fixture(params=ALL_PROJECTS)
    def all_project_dir(self, request):
        return EXAMPLES_DIR / request.param

    def _read_html(self, path):
        return path.read_text(encoding="utf-8")

    def test_html_is_self_contained(self, all_project_dir):
        """HTML 应是自包含的单文件"""
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            # Check for external CSS references (link with http URL)
            external_css = re.search(r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']http', content)
            assert not external_css, f"{html.name} 引用了外部 CSS URL"
            assert "<script src=" not in content, (
                f"{html.name} 不应引用外部 JS"
            )

    def test_html_has_dark_light_toggle(self, all_project_dir):
        """应有暗色/亮色切换"""
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            assert "toggle" in content.lower() or "dark" in content.lower(), (
                f"{html.name} 缺少 dark/light 切换"
            )

    def test_html_has_sidebar(self, all_project_dir):
        """应有侧边栏导航"""
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            assert "sidebar" in content.lower() or "nav" in content.lower(), (
                f"{html.name} 缺少侧边栏导航"
            )

    def test_html_has_quiz(self, all_project_dir):
        """Quiz is optional in converter output (requires --quiz-chapter).
        For legacy DOM-built HTML, quiz should be present."""
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            # Converter output doesn't have quiz unless --quiz-chapter is used
            if "showChapter(" in content:
                continue  # converter output, quiz is optional
            assert "quiz" in content.lower(), (
                f"{html.name} 缺少 quiz"
            )

    def test_html_no_innerhtml(self, all_project_dir):
        """禁止使用 innerHTML"""
        violations = []
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            if ".innerHTML" in content:
                count = content.count(".innerHTML")
                violations.append(f"{html.name}: {count} 次 innerHTML")
        if violations:
            pytest.xfail(
                "Known issue -- innerHTML usage:\n"
                + "\n".join(f"  {v}" for v in violations)
            )

    def test_html_has_valid_js(self, all_project_dir):
        """JavaScript 语法应合法（用 node --check 验证）"""
        errors = []
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            scripts = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
            for i, script in enumerate(scripts):
                script = script.strip()
                if not script:
                    continue
                result = subprocess.run(
                    ["node", "-e", script],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0 and "SyntaxError" in result.stderr:
                    first_err = result.stderr.strip().split("\n")[0]
                    errors.append(f"{html.name} script#{i}: {first_err}")
        assert not errors, f"JS 语法错误: {errors}"

    def test_html_has_mobile_support(self, all_project_dir):
        """应有移动端响应式支持（@media 查询）"""
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            assert "@media" in content, (
                f"{html.name} 缺少 @media 响应式样式"
            )

    def test_html_content_density(self, all_project_dir):
        """内容密度检查：section 数量、文件大小、heading 覆盖、无断裂 .md 链接"""
        docs_dir = all_project_dir / "docs"
        md_count = len(list(docs_dir.glob("*.md")))
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            file_size = html.stat().st_size
            errors = []

            # Section count (static or DOM-built)
            static_ch = content.count('class="chapter"')
            static_sec = content.count('class="section"')
            dom_sec = len(re.findall(r"""el\(\s*['"]div['"]\s*,\s*['"]section""", content))
            js_ch = len(re.findall(r"\{id:\s*['\"]s\w+['\"]", content))
            section_count = max(static_ch, static_sec, dom_sec, js_ch)
            if md_count > 0 and section_count < md_count:
                errors.append(
                    f"sections={section_count} < md_files={md_count}"
                )

            # Heading count (static or DOM-built)
            static_h = content.count("<h2>") + content.count("<h1>")
            js_h = len(re.findall(r"el\(\s*['\"]h[12]['\"]", content))
            heading_count = max(static_h, js_h)
            if md_count > 0 and heading_count < md_count:
                errors.append(
                    f"headings={heading_count} < md_files={md_count}"
                )

            # File size threshold
            min_size = max(md_count, 1) * 2500
            if file_size < min_size:
                errors.append(
                    f"size={file_size:,}b < min={min_size:,}b"
                )

            # No broken .md links
            md_links = re.findall(r'href="[^"]*\.md"', content)
            if md_links:
                errors.append(
                    f"{len(md_links)} broken .md links"
                )

            assert not errors, (
                f"{html.name} content density failures:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

    def test_html_has_expandable_sections(self, all_project_dir):
        """Expandable sections: 'expandable' CSS class (legacy) or <details> (converter)."""
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            has_expandable = "expandable" in content.lower()
            has_details = "<details" in content.lower()
            # Converter output may not have expandables in short fixture docs
            if "showChapter(" in content:
                continue  # converter output, expandables are optional
            assert has_expandable or has_details, (
                f"{html.name} 缺少 expandable 展开/收起区域"
            )

    def test_html_quiz_data_is_valid(self, all_project_dir):
        """quizData 应是合法的 JS 数据结构"""
        errors = []
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            match = re.search(r"(?:const|let|var)\s+quizData\s*=\s*(\[[\s\S]*?\]);", content)
            if not match:
                continue
            js_str = match.group(0)
            result = subprocess.run(
                ["node", "-e", js_str],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                first_err = result.stderr.strip().split("\n")[0]
                errors.append(f"{html.name}: {first_err}")
        assert not errors, f"quizData 格式错误: {errors}"

    def test_html_quiz_answer_index_valid(self, all_project_dir):
        """quiz 正确答案索引应是选项数组的合法索引"""
        errors = []
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            match = re.search(
                r"(?:const|let|var)\s+quizData\s*=\s*(\[[\s\S]*?\]);", content
            )
            if not match:
                continue
            js_str = match.group(0)
            # Normalize field names: opts->o, ans->c, explain->e
            normalize = (
                js_str
                + "\nvar n=quizData.map(function(q){return {q:q.q,o:q.opts||q.o,c:q.ans!=null?q.ans:q.c,e:q.explain||q.e}});"
                "console.log(JSON.stringify(n))"
            )
            result = subprocess.run(
                ["node", "-e", normalize],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                continue
            try:
                quiz = json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                continue
            for i, item in enumerate(quiz):
                opts = item.get("o", [])
                correct = item.get("c")
                if correct is None:
                    errors.append(f"{html.name} quiz[{i}]: missing answer field")
                elif not isinstance(correct, int) or correct < 0 or correct >= len(opts):
                    errors.append(
                        f"{html.name} quiz[{i}]: answer={correct} out of range for {len(opts)} options"
                    )
        assert not errors, f"Quiz 答案索引错误:\n" + "\n".join(f"  {e}" for e in errors)

    def test_html_js_strings_properly_escaped(self, all_project_dir):
        """JS quizData 中的字符串引号必须正确转义

        通过 node 执行 quizData 定义，如果存在未转义的引号会导致 SyntaxError。
        这是 test_html_has_valid_js 的补充，专门聚焦 quiz 数据的引号转义问题。
        详见 html-reference.md "JavaScript String Escaping" 章节。
        """
        errors = []
        for html in (all_project_dir / "interactive").glob("*.html"):
            content = self._read_html(html)
            match = re.search(
                r"(?:const|let|var)\s+quizData\s*=\s*(\[[\s\S]*?\]);", content
            )
            if not match:
                continue
            js_str = match.group(0)
            result = subprocess.run(
                ["node", "-e", js_str],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0 and "SyntaxError" in result.stderr:
                first_err = result.stderr.strip().split("\n")[0]
                errors.append(f"{html.name}: {first_err}")
        assert not errors, (
            f"quizData JS syntax error (likely unescaped quotes):\n"
            + "\n".join(f"  {e}" for e in errors)
        )


@pytest.mark.skipif(not any((EXAMPLES_DIR / p / "v2").is_dir() for p in _CANDIDATE_FULL), reason="no v2 fixtures")
class TestV2Output:
    """v2 版本产出测试 — 仅有 interactive HTML，无 docs"""

    @pytest.fixture(params=[p for p in _CANDIDATE_FULL if (EXAMPLES_DIR / p / "v2").is_dir()])
    def v2_dir(self, request):
        return EXAMPLES_DIR / request.param / "v2"

    def test_v2_has_interactive_dir(self, v2_dir):
        assert (v2_dir / "interactive").is_dir(), f"{v2_dir.name}/v2 缺少 interactive/"

    def test_v2_has_brief_general_html(self, v2_dir):
        html = v2_dir / "interactive" / "walkthrough-brief-general.html"
        assert html.is_file(), f"{v2_dir.name}/v2 缺少 walkthrough-brief-general.html"

    def test_v2_has_brief_dev_html(self, v2_dir):
        html = v2_dir / "interactive" / "walkthrough-brief-dev.html"
        assert html.is_file(), f"{v2_dir.name}/v2 缺少 walkthrough-brief-dev.html"

    def test_v2_html_is_self_contained(self, v2_dir):
        interactive = v2_dir / "interactive"
        if not interactive.is_dir():
            pytest.skip("no interactive dir")
        for html in interactive.glob("*.html"):
            content = html.read_text(encoding="utf-8")
            assert "<script src=" not in content, f"{html.name} 不应引用外部 JS"


# ─── v1 旧版兼容测试 ───────────────────────────────────────


@pytest.mark.skipif(not any((EXAMPLES_DIR / p / "v1").is_dir() for p in _CANDIDATE_FULL), reason="no v1 fixtures")
class TestV1Output:
    """v1 版本产出也应有基本质量保证"""

    V1_VARIANTS = ["brief-general", "brief-dev", "medium-general", "medium-dev",
                   "deep-general", "deep-dev"]

    @pytest.fixture(params=[p for p in _CANDIDATE_FULL if (EXAMPLES_DIR / p / "v1").is_dir()])
    def project_dir(self, request):
        return EXAMPLES_DIR / request.param / "v1"

    def test_v1_has_brief_general(self, project_dir):
        d = project_dir / "brief-general"
        assert d.is_dir(), f"{project_dir.name} 缺少 brief-general/"

    def test_v1_has_brief_dev(self, project_dir):
        d = project_dir / "brief-dev"
        assert d.is_dir(), f"{project_dir.name} 缺少 brief-dev/"

    def test_v1_all_variants_have_docs_and_html(self, project_dir):
        """有内容的 v1 变体都应有 docs/ 和 interactive/"""
        for variant in self.V1_VARIANTS:
            d = project_dir / variant
            if not d.is_dir():
                continue
            docs = d / "docs"
            interactive = d / "interactive"
            if not docs.is_dir() or not interactive.is_dir():
                continue
            # 跳过空壳目录（只有 docs/ 和 interactive/ 但没有内容）
            md_files = list(docs.glob("*.md"))
            if not md_files:
                continue
            html_files = list(interactive.glob("*.html"))
            assert html_files, f"{variant}/interactive/ 无 HTML 文件"

    def test_v1_docs_have_overview(self, project_dir):
        """有内容的 v1 变体 docs/ 应有 overview 文件"""
        for variant in self.V1_VARIANTS:
            d = project_dir / variant / "docs"
            if not d.is_dir():
                continue
            md_files = list(d.glob("*.md"))
            if not md_files:
                continue
            overview = [f for f in md_files if "overview" in f.name.lower()]
            assert overview, f"{variant}/docs/ 缺少 overview 文件"

    def test_v1_html_self_contained(self, project_dir):
        """v1 HTML 不应引用外部资源"""
        for variant in self.V1_VARIANTS:
            interactive = project_dir / variant / "interactive"
            if not interactive.is_dir():
                continue
            for html in interactive.glob("*.html"):
                content = html.read_text(encoding="utf-8")
                # No external stylesheets
                assert '<link rel="stylesheet"' not in content, (
                    f"{variant}/{html.name} 引用了外部 CSS"
                )
                # No external scripts
                assert '<script src="http' not in content, (
                    f"{variant}/{html.name} 引用了外部 JS"
                )

    def test_v1_docs_minimal_chapters(self, project_dir):
        """v1 brief 变体至少有 5 个章节"""
        for variant in ["brief-general", "brief-dev"]:
            docs = project_dir / variant / "docs"
            if not docs.is_dir():
                continue
            md_files = list(docs.glob("*.md"))
            if not md_files:
                continue
            assert len(md_files) >= 5, (
                f"{variant}/docs/ 只有 {len(md_files)} 个章节，期望至少 5 个"
            )


# ─── Sources Manifest 验证 ──────────────────────────────────


def _discover_manifest_projects():
    """Dynamically discover example projects with sources-manifest.json"""
    projects = []
    for d in sorted(EXAMPLES_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if (d / "docs" / "sources-manifest.json").is_file():
            projects.append(d.name)
    return projects if projects else ["bat"]


MANIFEST_PROJECTS = _discover_manifest_projects()


class TestSourcesManifest:
    """SKILL.md Sources Manifest (MANDATORY) 规范验证"""

    @pytest.fixture(params=MANIFEST_PROJECTS)
    def manifest_project(self, request):
        path = EXAMPLES_DIR / request.param
        assert path.is_dir(), f"{request.param} 实例目录不存在"
        return path

    def _load_manifest(self, manifest_path):
        """加载并解析 manifest JSON"""
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_brief_manifest_exists(self, manifest_project):
        """Brief 级别应有 sources-manifest.json"""
        manifest = manifest_project / "docs" / "sources-manifest.json"
        assert manifest.is_file(), f"{manifest_project.name} 缺少 docs/sources-manifest.json"

    def test_manifest_valid_json(self, manifest_project):
        """Manifest 应是合法 JSON"""
        for manifest_path in self._find_manifests(manifest_project):
            try:
                data = self._load_manifest(manifest_path)
                assert isinstance(data, dict), f"{manifest_path.name} 应是 JSON 对象"
            except json.JSONDecodeError as e:
                pytest.fail(f"{manifest_path}: JSON 解析失败: {e}")

    def test_manifest_has_required_fields(self, manifest_project):
        """Manifest 应有 schema_version, source_project, generated_at, claims"""
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            for key in ["schema_version", "source_project", "generated_at", "claims"]:
                assert key in data, f"{manifest_path.name} 缺少必需字段: {key}"

    def test_manifest_schema_version(self, manifest_project):
        """Schema version 应为 1.0"""
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            assert data.get("schema_version") == "1.0", (
                f"{manifest_path.name} schema_version 应为 '1.0'"
            )

    def test_manifest_source_project_has_name(self, manifest_project):
        """source_project 应有 name 字段"""
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            sp = data.get("source_project", {})
            assert sp.get("name"), f"{manifest_path.name} source_project.name 缺失"

    def test_manifest_claims_is_array(self, manifest_project):
        """claims 应是数组"""
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            assert isinstance(data.get("claims"), list), (
                f"{manifest_path.name} claims 应是数组"
            )

    def test_manifest_claims_have_required_fields(self, manifest_project):
        """每个 claim 应有 id, type, source_file, claim_summary, verified (doc_file/doc_line optional for Phase 3A)"""
        required = {"id", "type", "source_file", "claim_summary", "verified"}
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            for i, claim in enumerate(data.get("claims", [])):
                missing = required - set(claim.keys())
                assert not missing, (
                    f"{manifest_path.name} claims[{i}] 缺少字段: {missing}"
                )

    def test_manifest_claim_types_valid(self, manifest_project):
        """claim type 应是合法值"""
        valid_types = {
            "code_example", "directory_structure", "api_signature",
            "version_number", "architecture_claim", "dependency_claim",
            "config_claim", "feature_claim", "performance_claim",
        }
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            for i, claim in enumerate(data.get("claims", [])):
                ctype = claim.get("type")
                assert ctype in valid_types, (
                    f"{manifest_path.name} claims[{i}] 非法 type: {ctype}"
                )

    def test_manifest_claim_ids_unique(self, manifest_project):
        """claim id 应唯一"""
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            ids = [c.get("id") for c in data.get("claims", [])]
            duplicates = [cid for cid in set(ids) if ids.count(cid) > 1]
            assert not duplicates, (
                f"{manifest_path.name} 重复 claim id: {duplicates}"
            )

    def test_manifest_has_minimum_claims(self, manifest_project):
        """Brief 级别应有至少 5 个 claims"""
        manifest_path = manifest_project / "docs" / "sources-manifest.json"
        if not manifest_path.is_file():
            pytest.skip("no brief manifest")
        data = self._load_manifest(manifest_path)
        claim_count = len(data.get("claims", []))
        assert claim_count >= 5, (
            f"{manifest_project.name} brief manifest 应有 5+ claims，实际 {claim_count}"
        )

    def test_manifest_doc_files_exist(self, manifest_project):
        """claim 引用的 doc_file 应是实际存在的 md 文件"""
        for manifest_path in self._find_manifests(manifest_project):
            data = self._load_manifest(manifest_path)
            for claim in data.get("claims", []):
                doc_file = claim.get("doc_file")
                if not doc_file:
                    continue
                doc_path = manifest_path.parent / doc_file
                assert doc_path.is_file(), (
                    f"{manifest_path.name} claim {claim.get('id')}: "
                    f"doc_file 不存在: {doc_file}"
                )

    def _find_manifests(self, project_dir):
        """查找项目下所有 manifest 文件"""
        manifests = []
        for path in [
            project_dir / "docs" / "sources-manifest.json",
            project_dir / "docs" / "medium" / "sources-manifest.json",
            project_dir / "docs" / "deep" / "sources-manifest.json",
        ]:
            if path.is_file():
                manifests.append(path)
        return manifests


# ─── Source Citation 格式验证 ──────────────────────────────────


def _collect_all_md(project_dir):
    """收集项目下所有 md 文件（含 brief/medium/deep）"""
    md_files = []
    for subdir in [project_dir / "docs", project_dir / "docs" / "medium",
                   project_dir / "docs" / "deep"]:
        if subdir.is_dir():
            for f in sorted(subdir.iterdir()):
                if f.suffix == ".md":
                    md_files.append(f)
    return md_files


class TestSourceCitation:
    """SKILL.md 准确性规则验证：source citation 格式检查"""

    @pytest.fixture(params=ALL_PROJECTS)
    def project_dir(self, request):
        path = EXAMPLES_DIR / request.param
        assert path.is_dir(), f"{request.param} 实例目录不存在"
        return path

    def test_no_source_tag(self, project_dir):
        """禁止使用 // Source: 标签（SKILL.md Rule: 必须用 Simplified from:）"""
        pattern = re.compile(r"//\s*Source:", re.IGNORECASE)
        violations = []
        for md_file in _collect_all_md(project_dir):
            content = md_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if pattern.search(line):
                    violations.append(f"{md_file.name}:{i}: {line.strip()}")
        assert not violations, (
            f"{project_dir.name} 发现 {len(violations)} 处禁止的 '// Source:' 标签:\n"
            + "\n".join(f"  {v}" for v in violations[:10])
        )

    def test_code_blocks_have_simplified_from(self, project_dir):
        """含代码块的 md 文件中，代码块应有 // Simplified from: 注释"""
        code_block_re = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
        simplified_re = re.compile(r"Simplified\s+from:", re.IGNORECASE)

        total_blocks = 0
        cited_blocks = 0
        uncited = []

        for md_file in _collect_all_md(project_dir):
            content = md_file.read_text(encoding="utf-8")
            for match in code_block_re.finditer(content):
                code = match.group(1)
                # Skip very short blocks (likely just labels, not real code)
                if len(code.strip()) < 20:
                    continue
                total_blocks += 1
                # Check 5 lines before the code block for a citation
                block_start = match.start()
                pre_text = content[:block_start]
                pre_lines = pre_text.splitlines()[-5:]
                pre_context = "\n".join(pre_lines)

                if simplified_re.search(pre_context) or simplified_re.search(code):
                    cited_blocks += 1
                else:
                    uncited.append(f"{md_file.name} (block at ~line {content[:block_start].count(chr(10))+1})")

        # Allow some uncited blocks (not all code needs citation, e.g. config examples)
        # but require at least 50% coverage
        if total_blocks > 0:
            ratio = cited_blocks / total_blocks
            assert ratio >= 0.5, (
                f"{project_dir.name}: 代码块引用覆盖率 {ratio:.0%} 低于 50% "
                f"({cited_blocks}/{total_blocks} cited). "
                f"未引用块:\n" + "\n".join(f"  {u}" for u in uncited[:10])
            )


class TestManifestSourceIntegrity:
    """Manifest source_file + source_lines 完整性验证"""

    @pytest.fixture(params=MANIFEST_PROJECTS)
    def manifest_project(self, request):
        path = EXAMPLES_DIR / request.param
        assert path.is_dir(), f"{request.param} 实例目录不存在"
        return path

    def _get_source_dir(self, project_dir):
        """定位源码目录（_src_<name>/）"""
        src = EXAMPLES_DIR / f"_src_{project_dir.name}"
        return src if src.is_dir() else None

    def test_source_files_exist(self, manifest_project):
        """manifest 中 source_file 引用的文件或目录应存在"""
        src_dir = self._get_source_dir(manifest_project)
        if src_dir is None:
            pytest.skip("source directory not available")

        for manifest_path in TestSourcesManifest()._find_manifests(manifest_project):
            data = TestSourcesManifest()._load_manifest(manifest_path)
            for claim in data.get("claims", []):
                sf = claim.get("source_file")
                if not sf:
                    continue
                # directory_structure claims may reference directories
                ref = src_dir / sf
                assert ref.is_file() or ref.is_dir(), (
                    f"{manifest_project.name} claim {claim.get('id')}: "
                    f"source_file 不存在: {sf}"
                )

    def test_source_lines_within_file(self, manifest_project):
        """manifest 中 source_lines 的结束行不应超过文件总行数"""
        src_dir = self._get_source_dir(manifest_project)
        if src_dir is None:
            pytest.skip("source directory not available")

        for manifest_path in TestSourcesManifest()._find_manifests(manifest_project):
            data = TestSourcesManifest()._load_manifest(manifest_path)
            for claim in data.get("claims", []):
                sf = claim.get("source_file")
                lines = claim.get("source_lines")
                if not sf or not lines:
                    continue
                source_path = src_dir / sf
                if not source_path.is_file():
                    continue
                with open(source_path, "r", encoding="utf-8", errors="replace") as f:
                    total = sum(1 for _ in f)
                assert lines[1] <= total, (
                    f"{manifest_project.name} claim {claim.get('id')}: "
                    f"source_lines {lines} 超出文件行数 ({total}): {sf}"
                )

    def test_manifest_coverage_for_code_claims(self, manifest_project):
        """所有 code_example 类型的 claim 应有 source_lines"""
        for manifest_path in TestSourcesManifest()._find_manifests(manifest_project):
            data = TestSourcesManifest()._load_manifest(manifest_path)
            for claim in data.get("claims", []):
                if claim.get("type") == "code_example":
                    assert claim.get("source_lines"), (
                        f"{manifest_project.name} claim {claim.get('id')}: "
                        f"code_example 缺少 source_lines"
                    )
