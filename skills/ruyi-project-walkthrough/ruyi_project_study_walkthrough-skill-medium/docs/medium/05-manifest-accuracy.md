# 05 Phase 3：Manifest-First 准确性保证

## 核心原则：Verify Before Write

project-walkthrough 最核心的设计决策是 **manifest-first**——先验证所有声明，再写内容。这不是一个审计日志，而是一个**写入许可证**。

> 类比理解：manifest 就像新闻编辑的"事实核查表"——每一条报道必须在核查表上打勾后才能发稿。没有打勾的，写得再好也不能发。

## Manifest 生命周期

manifest 文件 `sources-manifest.json` 经历三个阶段：

| 阶段 | 状态 | doc_file | doc_line |
|------|------|----------|----------|
| Phase 3A（验证态） | claims 有 source_file + verified | 可选 | 可选 |
| Phase 3B（追溯态） | claims 增加 doc_file + doc_line | 必填 | 必填 |
| Phase 3C（校验态） | 全部字段完整 + 源文件检查通过 | 必填 | 必填 |

## 9 种声明类型

每种事实声明都有对应的验证方式：

| type | 何时使用 | 验证方式 |
|------|---------|---------|
| `code_example` | md 文件中的代码块 | 读取源文件，复制精确行 |
| `directory_structure` | 目录/文件树描述 | `ls` 实际目录 |
| `api_signature` | 函数/方法签名 | 读取函数定义（不是调用点） |
| `version_number` | 版本号声明 | 读取 package.json/Cargo.toml |
| `architecture_claim` | "X 模块负责 Y" | 找到支撑源文件 |
| `dependency_claim` | "使用了库 X" | 找到 import 语句 |
| `config_claim` | 配置选项描述 | 读取配置定义 |
| `feature_claim` | 功能特性描述 | 读取实现代码 |
| `performance_claim` | 性能数据 | 读取 bench 测试文件 |

## Manifest JSON 结构

每个 claim 条目的核心字段：

```json
// Simplified from: docs/sources-manifest-schema.md:52-62
{
  "id": "claim-001",
  "type": "code_example",
  "source_file": "src/main.py",
  "source_lines": [10, 25],
  "claim_summary": "Main entry point with argument parsing",
  "verified": true,
  "verification_note": "exact match from source",
  "doc_file": "docs/03-core.md",
  "doc_line": 42
}
```

关键规则：
- **id 格式**：`claim-` + 3 位以上数字（如 `claim-001`、`claim-042`）
- **source_lines**：`[start, end]` 行号范围，1-based
- **verified**：必须是 `true` 才能在 Phase 3B 中使用
- **unverified 数组**：无法验证的声明放入此数组，附带原因

## 验证脚本

`scripts/verify_sources.py`（315 行）对 manifest 执行 5 类检查：

```python
// Simplified from: scripts/verify_sources.py:87-101
def validate_basic(manifest, result, strict=False):
    for key in REQUIRED_TOP_KEYS:
        if key not in manifest:
            result.error(f"Missing required top-level key: {key}")
    # ... 验证 claims 数组、ID 格式、类型枚举
```

检查项：
1. **Schema 验证** — JSON 结构合法性
2. **基本结构** — 必填字段、ID 格式、类型枚举
3. **文件存在性** — source_file 指向的文件是否存在
4. **行号有效性** — source_lines 不超过文件行数
5. **严格模式** (`--strict`) — 要求 doc_file/doc_line 必填

## 引用格式规则

每个代码块必须使用 `// Simplified from: path:lines`：

```
// Simplified from: scripts/md_to_html.py:129-130
def convert_md_to_html(md_text, nav_skip_re=None):
    ...
```

**禁止** 使用 `// Source:`。原因：walkthrough 中的代码总是被简化的（缩进改变、注释省略、上下文移除），`Simplified from:` 更诚实。

## 12 轮迭代验证

manifest-first 系统是通过 12 轮验证迭代建立的：

- Round 1-9：逐步发现和修复准确性问题
- Round 10-12：连续零问题，系统达到稳定状态
- 最终：185 个测试覆盖结构、manifest、引用和源文件完整性

[← 上一章](04-exploration-planning.md) | [下一章 →](06-converter.md)
