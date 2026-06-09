# 07 辅助脚本：验证、依赖图、多平台转换

## 概览

project-walkthrough 有 3 个辅助脚本支撑核心 pipeline：

| 脚本 | 行数 | 核心职责 |
|------|------|---------|
| `verify_sources.py` | 315 | Manifest 验证与源文件检查 |
| `import_graph.py` | 239 | 从源码提取模块间依赖关系 |
| `convert.sh` | 272 | 多平台文件生成 |

## verify_sources.py：Manifest 验证器

### 用法

```bash
# 验证单个 manifest
python scripts/verify_sources.py examples/bat docs/sources-manifest.json

# 指定源码目录（检查文件存在性）
python scripts/verify_sources.py examples/bat docs/sources-manifest.json --source-dir ../bat

# 检查所有示例项目
python scripts/verify_sources.py --check-all examples/ --strict

# 限制到某个项目
python scripts/verify_sources.py --check-all examples/ --project bat
```

### 验证流程

```python
// Simplified from: scripts/verify_sources.py:212-234
def validate_manifest(manifest_path, source_dir=None, strict=False):
    result = VerificationResult()
    # 1. 读取并解析 JSON
    manifest = json.load(f)
    # 2. JSON Schema 验证（如果安装了 jsonschema）
    validate_jsonschema(manifest, schema, result)
    # 3. 基本结构验证
    validate_basic(manifest, result, strict=strict)
    # 4. 源文件存在性检查
    validate_source_files(manifest, source_dir, result)
    return result
```

### 验证结果类

```python
// Simplified from: scripts/verify_sources.py:43-73
class VerificationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    @property
    def ok(self):
        return len(self.errors) == 0
```

三类消息：`error`（阻塞）、`warning`（不阻塞但需注意）、`info`（信息）。

### 严格模式 vs 普通模式

| 检查项 | 普通（Phase 3A） | 严格（Phase 3C） |
|--------|-----------------|-----------------|
| 顶层字段 | ✅ | ✅ |
| claim ID 格式 | ✅ | ✅ |
| claim type 枚举 | ✅ | ✅ |
| source_lines 范围 | ✅ | ✅ |
| doc_file / doc_line | ⚠️ 可选 | ✅ 必填 |
| 源文件存在性 | ✅ | ✅ |

## import_graph.py：依赖图提取

### 设计目的

LLM 在画架构图时容易根据目录结构推断模块关系，但**目录嵌套 ≠ 依赖层级**。`import_graph.py` 通过实际分析 import 语句来提取真实的模块依赖。

> 类比理解：这个脚本就像"间谍卫星"——它不看地图上怎么画，而是实际追踪每个模块和谁有通信，画出真实的联络网。

### 支持的语言

| 语言 | 文件扩展名 | 提取方式 |
|------|-----------|---------|
| TypeScript/JavaScript | .ts, .tsx, .js, .jsx | `import ... from`, `require()`, `import()` |
| Python | .py | `from . import`, `from .. import`, 绝对导入 |
| Rust | .rs | `use crate::`, `use super::`, `mod` |

```python
// Simplified from: scripts/import_graph.py:108-110
def build_graph(root: str, lang: str, depth: int = 2) -> tuple[dict, dict]:
    ext_map = {
        "typescript": [".ts", ".tsx", ".js", ".jsx"],
        "python": [".py"],
        "rust": [".rs"],
    }
```

### 自动语言检测

如果 `--lang auto`（默认），按以下规则自动检测：
1. 有 `Cargo.toml` → Rust
2. 有 `pyproject.toml` 或 `setup.py` → Python
3. 有 `package.json` 或 `tsconfig.json` → TypeScript
4. 否则 → 分析所有语言

### 输出格式

脚本输出文本格式的依赖图：

```
# Import Dependency Graph: my-project
# Modules found: 8
# Files scanned: 23

## src/core/
   imports from: src/utils, src/types
   dependency count: 2

# Parallel modules (share a dependency, don't import each other):
   src/utils ← src/core, src/api (parallel siblings)
```

**Parallel siblings** 是一个关键概念：两个模块共享一个依赖但不互相导入。这表示它们可以独立开发。

## convert.sh：多平台文件生成

### 设计目的

project-walkthrough 需要同时在 Cursor、Windsurf、OpenCode、Gemini CLI 上工作。但每个平台的文件格式和大小限制不同。`convert.sh` 从 `SKILL.md`（单一事实源）自动生成所有平台文件。

### 用法

```bash
# 生成所有平台文件
./scripts/convert.sh

# 只生成 Cursor
./scripts/convert.sh cursor

# 检查是否同步
./scripts/convert.sh --check
```

### 三个平台的处理方式

**Cursor**（`cursor/ruyi-project-walkthrough.mdc`）：
- 完整 SKILL.md body + frontmatter 描述

**OpenCode**（`.opencode/skills/ruyi-project-walkthrough/SKILL.md`）：
- 完整 body + SKILL.md frontmatter 元数据

**Windsurf**（`.windsurf/rules/ruyi-project-walkthrough.md`）：
- **精简版**，限制 12,000 字符
- 跳过 Checklist、Documentation Standards 等冗长段落
- 跳过 Phase 3A/3B/3C 的详细验证步骤

```bash
# Simplified from: scripts/convert.sh:20-21
SKILL="$ROOT/skills/ruyi-project-walkthrough/SKILL.md"
MAX_WINDSURF_CHARS=12000
```

### 同步检查

`--check` 模式比较目标文件 body 与 SKILL.md body 是否一致，输出 SYNC 或 OUT_OF_SYNC。

[← 上一章](06-converter.md) | [下一章 →](08-release-automation.md)
