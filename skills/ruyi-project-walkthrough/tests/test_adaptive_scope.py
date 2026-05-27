"""
project-walkthrough Phase 0 自适应内容分析测试

验证 SKILL.md Phase 0 (Analyze & Confirm) 的核心功能：
1. 内容类型检测 (software-project / document-report / mixed)
2. 范围推荐逻辑
3. EXTEND.md 偏好加载
4. 确认门存在性
5. 参考文档结构完整性

用法：
  pytest tests/test_adaptive_scope.py -v
"""

import re
import pytest
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
SKILL_MD = SKILL_ROOT / "skills" / "project-walkthrough" / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "skills" / "project-walkthrough" / "references"
DOCS_DIR = SKILL_ROOT / "docs"


class TestPhase0InSkillMd:
    """验证 SKILL.md 包含 Phase 0 的所有必要部分"""

    @pytest.fixture(autouse=True)
    def load_skill(self):
        self.content = SKILL_MD.read_text()

    def test_has_phase0_section(self):
        assert "Phase 0" in self.content, "SKILL.md 缺少 Phase 0 章节"
        assert "Analyze & Confirm" in self.content, "Phase 0 缺少 Analyze & Confirm 标题"

    def test_has_extend_md_section(self):
        assert "EXTEND.md" in self.content, "SKILL.md 缺少 EXTEND.md 章节"
        assert ".project-walkthrough/EXTEND.md" in self.content, "EXTEND.md 路径不正确"

    def test_has_confirmation_gate(self):
        assert "Confirmation Gate" in self.content or "confirmation gate" in self.content.lower(), \
            "SKILL.md 缺少确认门 (Confirmation Gate)"

    def test_has_askuserquestion_reference(self):
        assert "AskUserQuestion" in self.content, \
            "SKILL.md 缺少 AskUserQuestion 引用"

    def test_has_no_confirm_flag(self):
        assert "--no-confirm" in self.content, \
            "SKILL.md 缺少 --no-confirm 参数说明"

    def test_has_content_type_detection(self):
        """Phase 0.2 必须包含内容类型检测"""
        phase0_section = self.content[self.content.find("Phase 0"):self.content.find("Phase 1")]
        assert "content type" in phase0_section.lower() or "内容类型" in phase0_section, \
            "Phase 0 缺少内容类型检测"

    def test_has_scope_questions(self):
        """确认门必须包含 scope/depth/format/review 四个问题"""
        phase0_section = self.content[self.content.find("Phase 0"):self.content.find("Phase 1")]
        assert "Scope" in phase0_section, "确认门缺少 Scope 问题"
        assert "Depth" in phase0_section, "确认门缺少 Depth 问题"
        assert "Format" in phase0_section, "确认门缺少 Format 问题"
        assert "Review" in phase0_section, "确认门缺少 Review 问题"

    def test_depth_no_hard_upper_limit(self):
        """Deep 级别不能有硬上限"""
        deep_section = self.content[
            self.content.find("### Deep"):self.content.find("### `all`")
        ]
        assert "No hard upper limit" in deep_section or "no hard" in deep_section.lower(), \
            "Deep 级别仍有硬上限"

    def test_manifest_strictness_configurable(self):
        """Manifest 严格度应可配置"""
        assert "manifest_strictness" in self.content or "manifest strictness" in self.content.lower(), \
            "SKILL.md 缺少 manifest 严格度配置"

    def test_has_analysis_md_output(self):
        """Phase 0 应生成 analysis.md"""
        assert "analysis.md" in self.content, \
            "SKILL.md 缺少 analysis.md 输出要求"

    def test_html_naming_includes_timestamp(self):
        """HTML 文件名应包含时间戳"""
        assert "YYYYMMDD" in self.content, \
            "HTML 文件命名缺少时间戳"

    def test_backup_rule_for_html(self):
        """应有 HTML 备份规则"""
        assert "backup" in self.content.lower(), \
            "缺少 HTML 备份规则"


class TestReferenceDocuments:
    """验证 references/ 目录下的参考文档结构"""

    def test_references_dir_exists(self):
        assert REFERENCES_DIR.is_dir(), "references/ 目录不存在"

    def test_analysis_framework_exists(self):
        path = REFERENCES_DIR / "analysis-framework.md"
        assert path.is_file(), "references/analysis-framework.md 不存在"

    def test_scope_matrix_exists(self):
        path = REFERENCES_DIR / "scope-matrix.md"
        assert path.is_file(), "references/scope-matrix.md 不存在"

    def test_preferences_schema_exists(self):
        path = REFERENCES_DIR / "preferences-schema.md"
        assert path.is_file(), "references/preferences-schema.md 不存在"

    def test_analysis_framework_has_content_type(self):
        content = (REFERENCES_DIR / "analysis-framework.md").read_text()
        assert "software-project" in content, "analysis-framework 缺少 software-project 类型"
        assert "document-report" in content, "analysis-framework 缺少 document-report 类型"
        assert "mixed" in content, "analysis-framework 缺少 mixed 类型"

    def test_analysis_framework_has_yaml_format(self):
        content = (REFERENCES_DIR / "analysis-framework.md").read_text()
        assert "content_type:" in content, "analysis-framework 缺少 YAML front matter 示例"
        assert "recommended:" in content, "analysis-framework 缺少推荐字段"

    def test_scope_matrix_has_signal_matrix(self):
        content = (REFERENCES_DIR / "scope-matrix.md").read_text()
        assert "Content Signal Matrix" in content, "scope-matrix 缺少内容信号矩阵"
        assert "Software Projects" in content or "software" in content.lower(), \
            "scope-matrix 缺少软件项目信号"
        assert "Documents" in content or "document" in content.lower(), \
            "scope-matrix 缺少文档信号"

    def test_scope_matrix_has_depth_definitions(self):
        content = (REFERENCES_DIR / "scope-matrix.md").read_text()
        assert "detailed" in content, "scope-matrix 缺少 detailed 深度定义"
        assert "standard" in content, "scope-matrix 缺少 standard 深度定义"
        assert "summary" in content, "scope-matrix 缺少 summary 深度定义"

    def test_preferences_schema_has_extend_paths(self):
        content = (REFERENCES_DIR / "preferences-schema.md").read_text()
        assert ".project-walkthrough/EXTEND.md" in content, \
            "preferences-schema 缺少项目级路径"
        assert "version: 1" in content, "preferences-schema 缺少版本号"

    def test_preferences_schema_has_scope_options(self):
        content = (REFERENCES_DIR / "preferences-schema.md").read_text()
        assert "full" in content, "preferences-schema 缺少 full scope"
        assert "focused" in content, "preferences-schema 缺少 focused scope"
        assert "overview" in content, "preferences-schema 缺少 overview scope"


class TestExplorationProtocol:
    """验证 exploration-protocol.md 包含文档类型探测"""

    def test_protocol_has_document_type(self):
        content = (DOCS_DIR / "exploration-protocol.md").read_text()
        assert "Document" in content or "document" in content, \
            "exploration-protocol 缺少 Document/Report 类型"

    def test_protocol_has_detection_commands(self):
        content = (DOCS_DIR / "exploration-protocol.md").read_text()
        assert "find" in content, "exploration-protocol 缺少检测命令"
        assert "wc -l" in content, "exploration-protocol 缺少行数统计"

    def test_protocol_has_game_engine_type(self):
        content = (DOCS_DIR / "exploration-protocol.md").read_text()
        assert "Game engine" in content or "game engine" in content, \
            "exploration-protocol 缺少 Game engine 项目类型"

    def test_protocol_has_database_type(self):
        content = (DOCS_DIR / "exploration-protocol.md").read_text()
        assert "Database" in content, "exploration-protocol 缺少 Database 项目类型"

    def test_protocol_has_compiler_type(self):
        content = (DOCS_DIR / "exploration-protocol.md").read_text()
        assert "Compiler" in content, "exploration-protocol 缺少 Compiler 项目类型"


class TestChapterTemplates:
    """验证 chapter-templates.md 包含文档模板"""

    def test_has_document_template(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "Document/Report Template" in content, \
            "chapter-templates 缺少 Document/Report 模板"

    def test_has_1_to_1_preservation(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "1:1" in content, "chapter-templates 缺少 1:1 保留策略"

    def test_has_document_quiz_design(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "Quiz design" in content or "quiz" in content.lower(), \
            "chapter-templates 缺少文档 Quiz 设计说明"

    def test_has_depth_levels_for_documents(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "detailed" in content, "chapter-templates 缺少 detailed 深度说明"
        assert "summary" in content, "chapter-templates 缺少 summary 深度说明"

    def test_has_game_engine_template(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "Game Engine Template" in content, "chapter-templates 缺少 Game Engine 模板"
        assert "Rendering pipeline" in content or "rendering" in content.lower(), \
            "Game Engine 模板缺少渲染管线章节"

    def test_has_database_template(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "Database" in content and "Storage Engine Template" in content, \
            "chapter-templates 缺少 Database/Storage Engine 模板"
        assert "Transaction model" in content or "ACID" in content, \
            "Database 模板缺少事务模型章节"

    def test_has_compiler_template(self):
        content = (DOCS_DIR / "chapter-templates.md").read_text()
        assert "Compiler" in content and "Interpreter Template" in content, \
            "chapter-templates 缺少 Compiler/Interpreter 模板"
        assert "Type system" in content, "Compiler 模板缺少类型系统章节"


class TestContentTypeDetection:
    """基于目录结构的类型检测逻辑验证"""

    def _detect_type(self, directory: Path) -> str:
        """模拟 Phase 0.2 的类型检测逻辑"""
        source_patterns = ["*.py", "*.ts", "*.js", "*.rs", "*.go", "*.java", "*.c", "*.cpp"]
        manifest_files = ["package.json", "Cargo.toml", "pyproject.toml", "go.mod", "pom.xml"]

        source_count = 0
        for pattern in source_patterns:
            source_count += len(list(directory.rglob(pattern)))

        manifest_exists = any((directory / m).is_file() for m in manifest_files)

        md_chapters = len(list(directory.glob("[0-9]*.md")))
        md_chapters += len(list(directory.glob("ch*.md")))
        md_chapters += len(list(directory.glob("chapter-*.md")))
        # Check subdirectories
        for subdir in directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                md_chapters += len(list(subdir.glob("[0-9]*.md")))

        if source_count > 5 or manifest_exists:
            if md_chapters > 3:
                return "mixed"
            return "software-project"
        elif md_chapters >= 3:
            return "document-report"
        else:
            return "software-project"  # default fallback

    def test_stanford_detected_as_document(self):
        """Stanford AI playbook 应被检测为 document-report"""
        stanford = Path("/Users/zhiweiyin/repo_ds1600/study_enterprise_AI_playbook_stanford")
        if not stanford.is_dir():
            pytest.skip("Stanford test data not available")
        result = self._detect_type(stanford)
        assert result == "document-report", f"Stanford 项目应检测为 document-report，实际: {result}"

    def test_skill_project_detected_as_software(self):
        """project-walkthrough-skill 自身应被检测为 software-project"""
        result = self._detect_type(SKILL_ROOT)
        assert result in ("software-project", "mixed"), \
            f"Skill 项目应检测为 software-project 或 mixed，实际: {result}"


class TestEXTENDmdFormat:
    """验证 EXTEND.md YAML 格式正确性"""

    def test_minimal_preferences_valid_yaml(self):
        """preferences-schema 中的最小示例应为有效 YAML"""
        content = (REFERENCES_DIR / "preferences-schema.md").read_text()
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', content, re.DOTALL)
        assert len(yaml_blocks) >= 2, "preferences-schema 应包含至少 2 个 YAML 示例"

        import yaml
        for i, block in enumerate(yaml_blocks):
            try:
                # Split on --- to handle multi-document YAML, take the last doc (the actual content)
                docs = list(yaml.safe_load_all(block))
                # At least one document should be a dict with expected keys
                valid_docs = [d for d in docs if isinstance(d, dict)]
                assert len(valid_docs) > 0, f"YAML 示例 {i+1} 应包含至少一个 dict 文档"
            except yaml.YAMLError as e:
                pytest.fail(f"YAML 示例 {i+1} 解析失败: {e}\n{block[:200]}")
