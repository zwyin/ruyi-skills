# Sources Manifest — Schema & Enforcement Design

## 目的

sources-manifest.json 是 walkthrough 生成的强制产出物。它记录 walkthrough 中每个事实声明的来源，
使准确性可以被外部验证。

## 设计原则

1. **不可跳过** — 没有 manifest 的 walkthrough 等于未完成
2. **机器可验证** — 脚本可以自动检查每个 entry 是否指向真实存在的源码
3. **人类可审计** — 每个声明对应一个 md 文件的具体位置
4. **分阶段产出** — Phase 3A 产出验证态（无 doc_file/doc_line），Phase 3B 丰富为追溯态

## Manifest 生命周期

| 阶段 | 状态 | doc_file | doc_line | 验证方式 |
|------|------|----------|----------|---------|
| Phase 3A | 验证态 | 可选 | 可选 | schema 基本验证 |
| Phase 3B | 追溯态 | 必填 | 必填 | --strict 模式 |
| Phase 3C | 校验态 | 必填 | 必填 | --strict + 源文件检查 |

## JSON Schema

权威 schema 定义在 `docs/sources-manifest.schema.json`。以下为关键字段说明。

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| schema_version | string | 是 | 固定 "1.0" |
| source_project | object | 是 | 见下表 |
| generated_at | string (ISO 8601) | 是 | 生成时间戳 |
| depth | string | 否 | "brief" / "medium" / "deep" |
| audience | string | 否 | "general" / "dev" |
| lang | string | 否 | "zh" / "en" |
| claims | array | 是 | 已验证声明列表 |
| unverified | array | 否 | 无法验证的声明列表 |

### source_project 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 项目名称 |
| repo_url | string | 否 | Git 仓库 URL |
| commit_or_tag | string | 否 | Git commit hash 或 tag |
| local_path | string | 否 | 本地路径（用于验证） |

### claims 条目字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (claim-NNN) | 是 | 唯一标识，格式 `claim-` + 3位以上数字 |
| type | string (enum) | 是 | 见下方类型表 |
| claim_summary | string | 是 | 一句话概述声明内容 |
| source_file | string | 是 | 源项目中的文件路径 |
| source_lines | array[int, int] or null | 否 | 行号范围 [start, end]，directory_structure 类型可为 null |
| verified | boolean | 是 | 是否已验证 |
| verification_note | string | 否 | 验证细节 |
| doc_file | string | Phase 3B 起 | walkthrough 中的 md 文件名 |
| doc_line | integer | Phase 3B 起 | 声明在 md 文件中的行号（1-based） |

### unverified 条目字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (claim-NNN) | 是 | 唯一标识 |
| claim_summary | string | 是 | 声明内容概述 |
| reason | string | 是 | 无法验证的原因 |

## Claim 类型说明

| type | 何时使用 | source_file | source_lines |
|------|---------|-------------|-------------|
| `code_example` | md 文件中的代码块 | 代码块来源的源文件 | 代码块对应的行号范围 |
| `directory_structure` | 描述目录/文件树 | 被描述的目录路径本身 | 可为 null |
| `api_signature` | 函数/方法签名 | 函数定义所在的源文件 | 函数定义的行号范围 |
| `version_number` | 版本号声明 | package.json/Cargo.toml 等 | 版本号所在行 |
| `architecture_claim` | "X 模块负责 Y" 类声明 | 支撑此声明的源文件 | 相关代码行号范围 |
| `dependency_claim` | "使用了库 X" | import/require 语句所在文件 | import 语句行号 |
| `config_claim` | 配置选项/参数描述 | 配置定义所在文件 | 配置代码行号范围 |
| `feature_claim` | 功能特性描述 | 功能实现所在文件 | 核心实现行号范围 |
| `performance_claim` | 性能数据/基准 | bench 测试文件或相关实现 | 数据来源行号范围 |

## 验证脚本行为

验证脚本（`scripts/verify_sources.py`）对 manifest 执行以下检查：

1. **Schema 验证** — manifest 是否符合 JSON schema
2. **基本结构验证** — 必填字段、claim ID 格式、类型枚举
3. **文件存在性** — `source_file` 指向的文件是否存在
4. **行号有效性** — `source_lines` 是否在文件行数范围内
5. **严格模式** (`--strict`) — 要求 doc_file/doc_line 必填（最终态验证）

## 输出位置

```
project_study_<name>/
├── docs/
│   ├── 01-overview.md
│   ├── ...
│   ├── sources-manifest.json    ← brief 级别 manifest
│   ├── medium/
│   │   ├── ...
│   │   └── sources-manifest.json  ← medium 级别独立 manifest
│   └── deep/
│       ├── ...
│       └── sources-manifest.json  ← deep 级别独立 manifest
└── interactive/
```

每个深度级别有独立的 manifest。Brief 的 manifest 放在 `docs/` 根目录。
