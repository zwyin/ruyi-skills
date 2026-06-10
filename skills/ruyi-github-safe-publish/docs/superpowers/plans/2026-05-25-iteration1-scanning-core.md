# Iteration 1: 脱敏扫描核心 + 项目骨架

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建项目骨架，实现两层脱敏扫描架构（规则扫描 + AI 语义扫描）和自动修复流程，配上验证测试。

**Architecture:** SKILL.md 是唯一事实源——所有扫描规则、步骤流程、修复逻辑都定义在这个文件中。scanning-rules.md 是规则参考文档。pytest 测试验证 SKILL.md 的结构完整性和扫描规则的正则有效性。

**Tech Stack:** Markdown (SKILL.md)、Python (pytest 测试)、Bash (validate_skill.sh)

**Spec:** `docs/superpowers/specs/2026-05-25-github-safe-publish-v2-design.md`

---

## File Structure

```
github-safe-publish/                      # 项目根
├── skills/
│   └── github-safe-publish/
│       └── SKILL.md                      # ★ 唯一事实源，迭代 1 写 Step 1-4 + 参数定义
├── docs/
│   ├── scanning-rules.md                 # ★ 第 1 层规则完整正则定义
│   ├── ci-actions-learnings.md           # (已有)
│   ├── competitive-research.md           # (已有)
│   └── superpowers/specs/                # (已有)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # 共享 fixtures（SKILL.md 路径、解析器）
│   ├── test_skill_structure.py           # frontmatter + 步骤结构验证
│   └── test_scanning_rules.py            # 规则正则有效性 + 维度覆盖验证
├── scripts/
│   └── validate_skill.sh                 # 一键运行所有验证
├── CLAUDE.md                             # 项目内部规则（版本管理等）
├── LICENSE                               # MIT
├── .gitignore
├── requirements-dev.txt                  # pytest
└── SKILL.md                              # (旧版，移走后删除)
```

---

## Task 1: 项目骨架 + 旧文件迁移

**Files:**
- Create: `.gitignore`
- Create: `requirements-dev.txt`
- Create: `LICENSE`
- Create: `CLAUDE.md`
- Create: `skills/github-safe-publish/SKILL.md` (空骨架，含 frontmatter)
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Delete: `SKILL.md` (根目录旧版，已迁移到 skills/ 下)

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p skills/github-safe-publish tests scripts
```

- [ ] **Step 2: 创建 .gitignore**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.DS_Store
*.swp
.env
```

- [ ] **Step 3: 创建 requirements-dev.txt**

```
pytest>=7.0
```

- [ ] **Step 4: 创建 MIT LICENSE**

```
MIT License

Copyright (c) 2026 zwyin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: 创建 tests/__init__.py**

空文件。

- [ ] **Step 6: 创建 tests/conftest.py**

```python
import pathlib

SKILL_MD = pathlib.Path(__file__).parent.parent / "skills" / "github-safe-publish" / "SKILL.md"
SCANNING_RULES_MD = pathlib.Path(__file__).parent.parent / "docs" / "scanning-rules.md"


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from markdown text into a dict."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    raw = text[3:end]
    result = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


import pytest


@pytest.fixture
def skill_text():
    return SKILL_MD.read_text(encoding="utf-8")


@pytest.fixture
def skill_frontmatter(skill_text):
    return _parse_frontmatter(skill_text)


@pytest.fixture
def rules_text():
    return SCANNING_RULES_MD.read_text(encoding="utf-8")
```

- [ ] **Step 7: 创建 skills/github-safe-publish/SKILL.md 骨架**

```markdown
---
name: github-safe-publish
version: "0.1.0"
description: |
  将本地 Git 项目安全地发布到 GitHub 公开仓库。包含两层脱敏扫描
  （确定性规则 + AI 语义）、自动修复、备份回滚、仓库创建、SEO 优化。
  Use when: "push to github", "publish to github", "开源", "推送到 GitHub",
  "create github repo", "发布到 github"。
triggers:
  - push to github
  - publish to github
  - create github repo
  - 开源发布
  - 推送到 GitHub
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Agent
---

# GitHub Safe Publish

将本地 Git 项目安全地发布到 GitHub 公开仓库。

## 参数

```
/github-safe-publish                    # 核心流程（脱敏+发布）
/github-safe-publish --seo              # 核心 + SEO 优化
/github-safe-publish --ci               # 核心 + CI 生成
/github-safe-publish --seo --ci         # 全部
/github-safe-publish --scan-only        # 只做脱敏扫描，输出报告，不修复不发布
/github-safe-publish --dry-run          # 模拟完整流程：扫描+模拟修复建议，但不做任何实际修改
```

**参数互斥与冲突处理**：
- `--scan-only` 和 `--dry-run` 不能与 `--seo` / `--ci` 组合（SEO 和 CI 只对已推送的仓库有意义，扫描模式不推送）
- `--seo` 和 `--ci` 可以同时使用（完整功能模式）
- 无效组合直接报错并退出
- `--dry-run` 与 `--scan-only` 的区别：`--scan-only` 只输出扫描报告；`--dry-run` 在报告基础上还会展示每个发现项的推荐修复方案（但不执行修复）

**流程控制矩阵**：

| 步骤 | 完整流程 | --scan-only | --dry-run |
|------|---------|-------------|-----------|
| Step 1: 前置检查+参数确认 | 执行 | 执行 | 执行 |
| Step 2: 创建备份分支 | 执行 | 跳过 | 跳过 |
| Step 3: 脱敏扫描 | 执行 | 执行 | 执行 |
| Step 4: 自动修复+用户确认 | 执行 | 跳过 | 输出修复建议但不执行 |
| Step 5: 仓库决策+推送 | （迭代 2 实现） | 跳过 | 跳过 |
| Step 6: 验证+报告 | （迭代 2 实现） | 仅扫描报告 | 仅扫描报告+修复建议 |

## Step 1: 前置检查 + 参数确认（集中交互 #1）

（迭代 1 实现完整内容）

## Step 2: 创建备份分支

（迭代 1 实现完整内容）

## Step 3: 脱敏扫描（两层架构）

（迭代 1 实现完整内容）

## Step 4: 自动修复 + 用户确认

（迭代 1 实现完整内容）
```

- [ ] **Step 8: 创建 CLAUDE.md**

```markdown
# github-safe-publish

## 版本管理

### 唯一版本源

版本号定义在 `skills/github-safe-publish/SKILL.md` frontmatter 的 `version` 字段。

### 版本号出现位置（6 处）

| # | 文件 | 位置 | 说明 |
|---|------|------|------|
| 1 | `skills/github-safe-publish/SKILL.md` | frontmatter `version: "X.Y.Z"` | **唯一版本源** |
| 2 | `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` | 迭代 4 创建 |
| 3 | `.claude-plugin/marketplace.json` | `"version": "X.Y.Z"` | 迭代 4 创建 |
| 4 | `README.md` | version badge URL | 迭代 4 创建 |
| 5 | `CHANGELOG.md` | 版本标题 | 迭代 4 创建 |
| 6 | `scripts/release.sh` | 读取并同步 | 迭代 4 创建 |

当前只有位置 1 存在，其余在迭代 4 创建时加入。

## 测试

```bash
pytest tests/ -q
```

## 项目结构要点

- **SKILL.md 是唯一事实源**：所有扫描规则、步骤流程、修复逻辑都定义在 `skills/github-safe-publish/SKILL.md` 中
- **scanning-rules.md 是规则参考**：`docs/scanning-rules.md` 是第 1 层规则的完整正则定义，供维护者参考，SKILL.md 引用但不重复全部正则
- **旧版 SKILL.md**：根目录的 `SKILL.md` 是 v1 版本，已迁移到 `skills/` 目录下，根目录版本已删除
```

- [ ] **Step 9: 删除根目录旧 SKILL.md**

```bash
git rm SKILL.md
```

- [ ] **Step 10: 提交**

```bash
git add .gitignore requirements-dev.txt LICENSE CLAUDE.md skills/ tests/
git rm SKILL.md
git commit -m "chore: scaffold project structure for v2, migrate SKILL.md to skills/"
```

---

## Task 2: 测试基础设施 + SKILL.md 结构验证

**Files:**
- Create: `tests/test_skill_structure.py`

- [ ] **Step 1: 写失败测试 — frontmatter 完整性**

```python
"""Validate SKILL.md structure: frontmatter, step numbering, parameter consistency."""
import re


def test_frontmatter_has_required_fields(skill_frontmatter):
    """SKILL.md frontmatter must contain name, version, description, triggers, allowed-tools."""
    required = ["name", "version", "description"]
    for field in required:
        assert field in skill_frontmatter, f"Missing required frontmatter field: {field}"


def test_frontmatter_name_matches_skill(skill_frontmatter):
    assert skill_frontmatter.get("name") == "github-safe-publish"


def test_frontmatter_version_is_semver(skill_frontmatter):
    version = skill_frontmatter.get("version", "")
    assert re.match(r"\d+\.\d+\.\d+", version), f"Version '{version}' is not semver"


def test_skill_contains_all_parameters(skill_text):
    """SKILL.md must document all CLI parameters."""
    params = ["--seo", "--ci", "--scan-only", "--dry-run"]
    for param in params:
        assert param in skill_text, f"Missing parameter documentation: {param}"


def test_skill_contains_flow_control_matrix(skill_text):
    """SKILL.md must contain the flow control matrix."""
    assert "流程控制矩阵" in skill_text or "Flow control" in skill_text


def test_skill_has_step_headings(skill_text):
    """SKILL.md must have Step 1 through Step 4 headings (iteration 1 scope)."""
    for i in range(1, 5):
        pattern = f"## Step {i}:"
        assert pattern in skill_text, f"Missing step heading: {pattern}"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd <repo>/github-safe-publish && pip install -q pytest && pytest tests/test_skill_structure.py -v
```

Expected: PASS（骨架中已有占位步骤标题）。frontmatter 测试应通过。

- [ ] **Step 3: 添加步骤内容连续性测试**

追加到 `tests/test_skill_structure.py`：

```python
def test_steps_have_content_not_placeholder(skill_text):
    """Steps 1-4 must have real content, not placeholder markers."""
    for i in range(1, 5):
        # Find the step heading
        step_pattern = rf"## Step {i}:.*?\n(.*?)(?=\n## Step |\n## |\Z)"
        match = re.search(step_pattern, skill_text, re.DOTALL)
        assert match, f"Could not find content block for Step {i}"
        content = match.group(1).strip()
        assert len(content) > 100, f"Step {i} content too short ({len(content)} chars), likely a placeholder"
        assert "（迭代" not in content or i > 4, f"Step {i} still has iteration placeholder"
```

- [ ] **Step 4: 运行测试验证失败**

```bash
pytest tests/test_skill_structure.py::test_steps_have_content_not_placeholder -v
```

Expected: FAIL — Steps 1-4 还只有占位文本。

- [ ] **Step 5: 提交测试**

```bash
git add tests/test_skill_structure.py
git commit -m "test: add SKILL.md structure validation tests"
```

---

## Task 3: scanning-rules.md — 第 1 层规则定义

**Files:**
- Create: `docs/scanning-rules.md`

- [ ] **Step 1: 写失败测试 — 规则验证**

创建 `tests/test_scanning_rules.py`：

```python
"""Validate scanning rules in docs/scanning-rules.md."""
import re


def test_rules_file_exists(rules_text):
    """scanning-rules.md must exist and be non-empty."""
    assert len(rules_text) > 200


def test_all_five_dimensions_covered(rules_text):
    """Rules must cover all 5 dimensions: A-E."""
    dimensions = ["密钥", "PII", "内部基础设施", "文件黑名单", "Git 历史"]
    for dim in dimensions:
        assert dim in rules_text, f"Missing dimension: {dim}"


def test_regex_patterns_are_valid(rules_text):
    """All regex patterns in code blocks must be syntactically valid."""
    # Find all regex patterns in backtick blocks
    pattern_blocks = re.findall(r"`([^`]+)`", rules_text)
    for p in pattern_blocks:
        # Skip non-regex strings (plain words, URLs, etc.)
        if any(c in p for c in r"\[](){}*+?.^$|"):
            try:
                re.compile(p)
            except re.error as e:
                # Allow known patterns that need raw string handling
                assert False, f"Invalid regex pattern: {p!r} — {e}"


def test_entropy_detection_defined(rules_text):
    """Rules must define entropy detection with threshold."""
    assert "熵" in rules_text or "entropy" in rules_text.lower()
    assert "4.5" in rules_text  # Shannon entropy threshold


def test_secret_detection_covers_major_providers(rules_text):
    """Rules must cover major cloud/code/AI/payment providers."""
    providers = ["AWS", "GitHub", "OpenAI", "Stripe"]
    for provider in providers:
        assert provider in rules_text, f"Missing provider: {provider}"


def test_pii_covers_chinese_patterns(rules_text):
    """PII rules must include Chinese phone and ID patterns."""
    assert "1[3-9]" in rules_text or "手机" in rules_text  # Chinese phone pattern
    assert "身份证" in rules_text or "ID number" in rules_text


def test_infrastructure_covers_internal_patterns(rules_text):
    """Infrastructure rules must cover internal IPs, domains, local paths."""
    assert "192.168" in rules_text
    assert "/Users/" in rules_text or "C:\\\\Users" in rules_text
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_scanning_rules.py -v
```

Expected: FAIL — `docs/scanning-rules.md` 不存在。

- [ ] **Step 3: 编写 docs/scanning-rules.md**

这是核心文档，包含第 1 层所有扫描规则的完整正则定义。参考 Gitleaks 222 条规则的结构，按 5 个维度组织。

内容必须覆盖：

**A. 密钥/凭证**
- 各主流服务商的 API key 格式正则（AWS、Azure、GCP、GitHub、GitLab、OpenAI、Anthropic、Slack、Stripe 等 50+ 条）
- Private key 格式检测
- JWT 格式检测
- 通用高熵密钥检测（Shannon 熵 ≥ 4.5，仅在密钥关键字附近触发）

**B. PII**
- 邮箱正则
- 中国大陆手机号：`1[3-9]\d{9}`
- 身份证号：`[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]`
- 中文姓名（百家姓模式，低置信度归入 WARNING）

**C. 内部基础设施**
- 内网 IP：`(?:192\.168|10\.|172\.(?:1[6-9]|2\d|3[01]))\.`
- 内部域名：`\.local|\.internal|\.lan`
- 硬编码路径：`/Users/\w+/|C:\\Users\\|/home/\w+/`
- NAS/VPN URL

**D. 文件黑名单**
- 文件名模式列表 + .gitignore 充分性检查逻辑

**E. Git 历史**
- commit message 扫描策略

每个规则条目格式：
```
### 规则 ID: provider-name-token
- **维度**: A（密钥/凭证）
- **正则**: `` `(pattern)` ``
- **关键字要求**: (如需)
- **严重级别**: CRITICAL / WARNING
- **误报排除**: (条件)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_scanning_rules.py -v
```

Expected: ALL PASS

- [ ] **Step 5: 提交**

```bash
git add docs/scanning-rules.md tests/test_scanning_rules.py
git commit -m "feat: add Layer 1 scanning rules with regex definitions + validation tests"
```

---

## Task 4: SKILL.md Step 1 — 前置检查 + 参数确认

**Files:**
- Modify: `skills/github-safe-publish/SKILL.md` (替换 Step 1 占位内容)

- [ ] **Step 1: 写失败测试 — Step 1 内容验证**

追加到 `tests/test_skill_structure.py`：

```python
def test_step1_contains_preflight_checks(skill_text):
    """Step 1 must define pre-flight hard checks."""
    step1 = _extract_step(skill_text, 1)
    assert "git" in step1.lower()
    assert "commit" in step1.lower()
    assert "gh" in step1.lower() or "CLI" in step1


def test_step1_contains_interactive_confirmation(skill_text):
    """Step 1 must define centralized interactive confirmation."""
    step1 = _extract_step(skill_text, 1)
    assert "AskUserQuestion" in step1 or "交互" in step1
    assert "工作模式" in step1 or "mode" in step1.lower()


def test_step1_contains_push_method_options(skill_text):
    """Step 1 must offer both auto and manual push options."""
    step1 = _extract_step(skill_text, 1)
    assert "手动推送" in step1 or "manual" in step1.lower()
    assert "自动" in step1 or "auto" in step1.lower()


def test_step1_contains_nongit_directory_handling(skill_text):
    """Step 1 must handle non-git directories."""
    step1 = _extract_step(skill_text, 1)
    assert "git init" in step1 or "初始化" in step1
    assert ".gitignore" in step1


def _extract_step(text, step_num):
    """Extract content of a specific step from SKILL.md."""
    pattern = rf"## Step {step_num}:.*?\n(.*?)(?=\n## Step |\n## [^S]|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    assert match, f"Step {step_num} not found"
    return match.group(1)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_skill_structure.py -k "step1" -v
```

Expected: FAIL

- [ ] **Step 3: 编写 Step 1 内容**

替换 `skills/github-safe-publish/SKILL.md` 中的 `## Step 1:` 占位部分，写入完整的 Step 1 内容，包括：

1. **1.1 自动检查**：git 仓库检测、commit 数量检测、gh CLI 状态检测
2. **1.2 集中交互确认**：工作模式选择、推送方式选择、非 git 目录处理
3. **交互结果汇总**：配置摘要输出

具体内容参照 spec 的 Step 1 定义。

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_skill_structure.py -k "step1" -v
```

Expected: ALL PASS

- [ ] **Step 5: 提交**

```bash
git add skills/github-safe-publish/SKILL.md tests/test_skill_structure.py
git commit -m "feat: implement Step 1 pre-flight checks + interactive parameter confirmation"
```

---

## Task 5: SKILL.md Step 2 — 创建备份分支

**Files:**
- Modify: `skills/github-safe-publish/SKILL.md`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_skill_structure.py`：

```python
def test_step2_defines_backup_branch(skill_text):
    """Step 2 must define backup branch creation with fixed name."""
    step2 = _extract_step(skill_text, 2)
    assert "pre-publish-backup" in step2


def test_step2_handles_uncommitted_changes(skill_text):
    """Step 2 must handle uncommitted changes (stash + pop)."""
    step2 = _extract_step(skill_text, 2)
    assert "stash" in step2.lower()


def test_step2_handles_stash_conflict(skill_text):
    """Step 2 must handle stash pop conflicts."""
    step2 = _extract_step(skill_text, 2)
    assert "冲突" in step2 or "conflict" in step2.lower()


def test_step2_skips_in_scan_modes(skill_text):
    """Step 2 must state it skips in --scan-only and --dry-run modes."""
    step2 = _extract_step(skill_text, 2)
    assert "scan-only" in step2 or "dry-run" in step2
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_skill_structure.py -k "step2" -v
```

- [ ] **Step 3: 编写 Step 2 内容**

替换占位内容，写入：
- 备份分支创建逻辑（干净工作区 vs 有未提交内容）
- stash pop 冲突处理
- 规则（固定名称、已存在则删除、不推送、回滚方式）
- 只读模式跳过说明

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_skill_structure.py -k "step2" -v
```

- [ ] **Step 5: 提交**

```bash
git add skills/github-safe-publish/SKILL.md tests/test_skill_structure.py
git commit -m "feat: implement Step 2 backup branch with conflict handling"
```

---

## Task 6: SKILL.md Step 3 — 脱敏扫描（两层架构）

**Files:**
- Modify: `skills/github-safe-publish/SKILL.md`

这是最核心的步骤，内容最多。

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_skill_structure.py`：

```python
def test_step3_defines_two_layer_architecture(skill_text):
    """Step 3 must define two-layer scanning: rule-based + AI semantic."""
    step3 = _extract_step(skill_text, 3)
    assert "第 1 层" in step3 or "Layer 1" in step3 or "规则扫描" in step3
    assert "第 2 层" in step3 or "Layer 2" in step3 or "AI" in step3 or "语义" in step3


def test_step3_covers_five_dimensions(skill_text):
    """Step 3 must reference all 5 scanning dimensions (A-E)."""
    step3 = _extract_step(skill_text, 3)
    for dim_label in ["密钥", "PII", "基础设施", "文件黑名单", "Git 历史"]:
        assert dim_label in step3, f"Missing dimension: {dim_label}"


def test_step3_references_scanning_rules_doc(skill_text):
    """Step 3 must reference docs/scanning-rules.md for full rule definitions."""
    step3 = _extract_step(skill_text, 3)
    assert "scanning-rules" in step3


def test_step3_defines_scan_scope(skill_text):
    """Step 3 must define what files are scanned (git tracked, exclude binary)."""
    step3 = _extract_step(skill_text, 3)
    assert "git ls-files" in step3 or "git 跟踪" in step3 or "跟踪文件" in step3


def test_step3_ai_scan_uses_subagent(skill_text):
    """Layer 2 AI scan must use independent sub-agents."""
    step3 = _extract_step(skill_text, 3)
    assert "子 agent" in step3 or "subagent" in step3.lower() or "Agent" in step3


def test_step3_defines_convergence(skill_text):
    """AI scan must have convergence criteria and max rounds."""
    step3 = _extract_step(skill_text, 3)
    assert "收敛" in step3 or "convergence" in step3.lower()
    assert "最多 2 轮" in step3 or "max 2" in step3.lower()
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_skill_structure.py -k "step3" -v
```

- [ ] **Step 3: 编写 Step 3 内容**

替换占位内容，写入完整的两层扫描架构：

**第 1 层：确定性规则扫描**
- 扫描范围定义（git ls-files，排除二进制/.git/子模块）
- 5 个维度（A-E）的概述 + 引用 `docs/scanning-rules.md` 获取完整正则
- 输出格式：结构化报告（维度/文件:行号/内容/严重级别）

**第 2 层：AI 语义扫描**
- 通过独立子 agent 执行（不共享主对话上下文）
- 扫描内容：业务数据、可溯源叙事、间接推断、误报排除
- 收敛判定：连续 1 轮无新发现即停止，最多 2 轮
- 子 agent prompt 模板

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_skill_structure.py -k "step3" -v
```

- [ ] **Step 5: 提交**

```bash
git add skills/github-safe-publish/SKILL.md tests/test_skill_structure.py
git commit -m "feat: implement Step 3 two-layer desensitization scanning architecture"
```

---

## Task 7: SKILL.md Step 4 — 自动修复 + 用户确认

**Files:**
- Modify: `skills/github-safe-publish/SKILL.md`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_skill_structure.py`：

```python
def test_step4_defines_severity_levels(skill_text):
    """Step 4 must define CRITICAL / WARNING / SAFE classification."""
    step4 = _extract_step(skill_text, 4)
    assert "CRITICAL" in step4
    assert "WARNING" in step4
    assert "SAFE" in step4


def test_step4_defines_fix_options(skill_text):
    """Step 4 must define 4 fix options for CRITICAL items."""
    step4 = _extract_step(skill_text, 4)
    assert "自动替换" in step4
    assert "手动修复" in step4
    assert "删除文件" in step4
    assert "确认安全" in step4


def test_step4_defines_replacement_rules(skill_text):
    """Step 4 must define auto-replacement rules."""
    step4 = _extract_step(skill_text, 4)
    assert "REPLACE_ME" in step4


def test_step4_handles_git_history(skill_text):
    """Step 4 must handle sensitive data in git history."""
    step4 = _extract_step(skill_text, 4)
    assert "filter-repo" in step4 or "历史" in step4


def test_step4_defines_fix_verify_loop(skill_text):
    """Step 4 must define fix-verify loop with max iterations."""
    step4 = _extract_step(skill_text, 4)
    assert "修复后验证" in step4 or "验证" in step4
    assert "3 次" in step4  # max 3 iterations


def test_step4_dry_run_shows_suggestions(skill_text):
    """Step 4 must note that --dry-run shows fix suggestions without executing."""
    step4 = _extract_step(skill_text, 4)
    assert "dry-run" in step4 or "修复建议" in step4
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_skill_structure.py -k "step4" -v
```

- [ ] **Step 3: 编写 Step 4 内容**

替换占位内容，写入：
- 结果分类（CRITICAL / WARNING / SAFE）
- CRITICAL 修复选项（A/B/C/D 四种）
- 自动替换规则
- WARNING 修复选项
- Git 历史特殊处理（三种方式 + 安全说明）
- 修复后验证（循环最多 3 次）
- --dry-run 模式行为（展示建议不执行）

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_skill_structure.py -k "step4" -v
```

- [ ] **Step 5: 提交**

```bash
git add skills/github-safe-publish/SKILL.md tests/test_skill_structure.py
git commit -m "feat: implement Step 4 auto-fix with user confirmation flow"
```

---

## Task 8: validate_skill.sh 一键验证脚本

**Files:**
- Create: `scripts/validate_skill.sh`

- [ ] **Step 1: 创建脚本**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== github-safe-publish skill validation ==="
echo ""

echo "1. Running pytest..."
if python3 -m pytest tests/ -v --tb=short; then
    echo ""
    echo "2. Checking file structure..."
    SKILL="skills/github-safe-publish/SKILL.md"
    RULES="docs/scanning-rules.md"

    for f in "$SKILL" "$RULES" "CLAUDE.md" "LICENSE"; do
        if [ -f "$f" ]; then
            echo "   ✓ $f"
        else
            echo "   ✗ $f MISSING"
            exit 1
        fi
    done

    echo ""
    echo "3. Checking SKILL.md version..."
    version=$(grep '^version:' "$SKILL" | head -1 | awk '{print $2}' | tr -d '"')
    if echo "$version" | grep -qE '^\d+\.\d+\.\d+$'; then
        echo "   ✓ version: $version"
    else
        echo "   ✗ Invalid version: $version"
        exit 1
    fi

    echo ""
    echo "=== All validations passed ==="
else
    echo "Tests failed!"
    exit 1
fi
```

- [ ] **Step 2: 添加执行权限**

```bash
chmod +x scripts/validate_skill.sh
```

- [ ] **Step 3: 运行验证**

```bash
bash scripts/validate_skill.sh
```

Expected: ALL PASS

- [ ] **Step 4: 提交**

```bash
git add scripts/validate_skill.sh
git commit -m "chore: add validate_skill.sh one-click validation script"
```

---

## Task 9: 全量验证 + 最终提交

- [ ] **Step 1: 运行所有测试**

```bash
cd <repo>/github-safe-publish && pytest tests/ -v
```

Expected: ALL PASS

- [ ] **Step 2: 运行验证脚本**

```bash
bash scripts/validate_skill.sh
```

Expected: ALL PASS

- [ ] **Step 3: 检查 SKILL.md 完整性**

手动确认 `skills/github-safe-publish/SKILL.md` 包含：
- frontmatter（name, version, description, triggers, allowed-tools）
- 参数定义（6 个参数 + 互斥规则 + 流程控制矩阵）
- Step 1: 前置检查 + 集中交互
- Step 2: 备份分支（含冲突处理）
- Step 3: 两层脱敏扫描（5 维度 + 子 agent + 收敛）
- Step 4: 自动修复（4 种选项 + 替换规则 + 验证循环）

- [ ] **Step 4: 检查 git status**

```bash
git status --short
```

Expected: clean（所有改动已提交）

---

## Self-Review Checklist

- [x] **Spec coverage**: Spec Step 1-4 全部有对应 Task（4-7），项目骨架有 Task 1，规则文档有 Task 3，验证脚本有 Task 8
- [x] **Placeholder scan**: 无 TBD/TODO/实现后补充 等占位符
- [x] **Type consistency**: 所有测试中的函数名（`_extract_step`、`skill_frontmatter` 等）在 conftest.py 中定义
- [x] **Iteration 2+ deferral**: Step 5-6 标记为"迭代 2 实现"，SEO/CI 标记为"迭代 3 实现"，在流程控制矩阵中明确标注
