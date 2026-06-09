# 10 测试体系与 CI

## 测试套件概览

project-walkthrough 有 8 个测试文件，250 个测试函数，覆盖所有主要组件：

| 测试文件 | 行数 | 测试函数数 | 测试目标 |
|---------|------|-----------|---------|
| `test_walkthrough_output.py` | 861 | 55 | 输出结构验证（目录、manifest、HTML） |
| `test_verify_sources.py` | 611 | 59 | Manifest 验证脚本 |
| `test_import_graph.py` | 534 | 46 | 依赖图提取 |
| `test_adaptive_scope.py` | 284 | 37 | 自适应范围系统 |
| `test_lang_output.py` | 170 | 16 | 多语言输出 |
| `test_convert.py` | 152 | 20 | 平台文件转换 |
| `test_watermark.py` | 121 | 12 | Watermark/promo 页面 |
| `test_release_sh.py` | 45 | 5 | 发布脚本 |
| **总计** | **2778** | **250** | |

## 运行测试

```bash
# 完整测试套件（详细输出）
pytest tests/ -v --tb=short

# 快速模式
pytest tests/ -q --tb=line

# CI 模式（测试 + 平台同步检查）
make ci

# Manifest 验证
python scripts/verify_sources.py --check-all examples/ --strict
```

## 测试 Fixture 项目

`tests/fixtures/` 包含 3 个预生成的 walkthrough 项目，用于测试产出物结构：

| 项目 | 用途 |
|------|------|
| **bat** (CLI tool) | 测试 CLI 工具类型的 walkthrough |
| **fastapi** (Library) | 测试库类型的 walkthrough |
| **zod** (Library) | 测试另一个库，不同的 schema 特征 |

每个 fixture 包含完整的产出物结构：

```
tests/fixtures/bat/
├── docs/
│   ├── 01-overview.md
│   ├── 02-input-and-config.md
│   ├── 03-syntax-highlighting.md
│   ├── 04-git-and-paging.md
│   ├── 05-innovation-summary.md
│   └── sources-manifest.json
└── interactive/
    └── walkthrough.html
```

## 关键测试类

### TestDirectoryStructure

验证产出物目录结构是否符合 SKILL.md 规范：

```python
// Simplified from: tests/test_walkthrough_output.py:32-55
class TestDirectoryStructure:
    def test_has_docs_dir(self, all_project_dir):
        assert (all_project_dir / "docs").is_dir()

    def test_has_interactive_dir(self, all_project_dir):
        assert (all_project_dir / "interactive").is_dir()

    def test_brief_docs_in_docs_flat(self, all_project_dir):
        """Brief 级别的 md 文件应直接在 docs/ 下"""
```

### Manifest 验证测试

覆盖 VerificationResult、validate_basic（严格/非严格）、validate_source_files、find_manifests 等核心函数：

```python
// Simplified from: tests/test_verify_sources.py:36-56
def _make_minimal_manifest(**overrides):
    manifest = {
        "schema_version": "1.0",
        "source_project": {"name": "test-project"},
        "generated_at": "2025-01-01T00:00:00Z",
        "claims": [{
            "id": "claim-001",
            "type": "code_example",
            "source_file": "src/main.py",
            "claim_summary": "A claim.",
            "verified": True,
        }],
    }
```

## CI 配置

```yaml
// Simplified from: .github/workflows/test.yml:1-24
name: Tests
on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pytest jsonschema pyyaml
      - run: make ci
```

CI 触发条件：
- **push to master/develop** — 合并到主分支或开发分支时
- **PR to master** — 创建或更新 PR 时

CI 执行 `make ci`，等价于 `pytest tests/ -v --tb=short && ./scripts/convert.sh --check`。

## Makefile 目标

```makefile
# Simplified from: Makefile:1-20
test:       python -m pytest tests/ -v --tb=short
test-quick: python -m pytest tests/ -q --tb=line
check:      ./scripts/convert.sh --check
generate:   ./scripts/convert.sh
verify:     python scripts/verify_sources.py --check-all examples/ --strict
ci: test check
release:    ./scripts/release.sh $(VERSION)
clean:      # 清理 __pycache__ 和 .pytest_cache
```

关键组合：
- `make ci` — CI 完整检查（测试 + 平台同步）
- `make verify` — 额外的 manifest 严格验证（CI 中不默认运行）

[← 上一章](09-multi-platform.md) | [下一章 →](11-design-philosophy.md)
