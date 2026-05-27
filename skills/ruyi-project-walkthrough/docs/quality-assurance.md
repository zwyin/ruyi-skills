# Quality Assurance 质量保障体系

本文档描述 project-walkthrough skill 的完整质量保障机制：做了什么验证、用什么手段、覆盖了哪些维度。

---

## 一、验证分层

质量保障分为 5 层，从静态到运行时逐层加严：

| 层级 | 名称 | 目的 | 执行时机 |
|------|------|------|----------|
| L1 | 静态校验 | Schema 合法性、文件结构、命名规范 | 每次 commit |
| L2 | 单元测试 | 产出文件的格式、内容模式、引用完整性 | CI / 手动 `pytest` |
| L3 | Manifest 验证 | 每个 claim 的源文件存在性、行号范围、内容匹配 | 每次 walkthrough 生成后 |
| L4 | 子 agent 抽检 | 独立 reviewer 逐项验证代码/目录/API/版本/架构 5 维度 | walkthrough 迭代后 |
| L5 | 端到端验证 | 从 `/project-walkthrough` 调用到最终产出的完整流程 | 发版前 |

---

## 二、L1 静态校验

### 2.1 sources-manifest.json Schema

文件：`docs/sources-manifest.schema.json`（JSON Schema draft-07）

校验内容：
- 顶层必填字段：`schema_version`、`source_project`、`generated_at`、`claims`
- `schema_version` 必须为 `"1.0"`
- 每个 claim 的 `id` 格式：`claim-NNN`（3+ 位数字）
- 每个 claim 的 `type` 枚举：9 种合法类型
- `source_lines` 格式：`[start, end]` 或 `null`，start ≤ end，≥ 1
- `unverified` 数组的每项必须有 `id`、`claim_summary`、`reason`

执行方式：
```bash
# jsonschema 库校验
python scripts/verify_sources.py <manifest> --source-dir <source>

# 或自动校验 examples/ 下所有项目
python scripts/verify_sources.py --check-all examples/
```

### 2.2 插件元数据校验

| 文件 | 校验项 |
|------|--------|
| `.claude-plugin/plugin.json` | `name`、`description`、`version`、`author.name`、`skills` 字段存在 |
| `.claude-plugin/marketplace.json` | `name`、`owner.name`、`plugins` 数组，每项含 `name`、`source`、`description` |
| `skills/project-walkthrough/SKILL.md` | YAML frontmatter：`name`、`description`、`argument-hint` |

### 2.3 文件命名规范

- Brief 文档：`docs/NN-kebab-case-title.md`（平铺，无子目录）
- Medium 文档：`docs/medium/NN-kebab-case-title.md`
- Deep 文档：`docs/deep/NN-kebab-case-title.md`
- Manifest：每个深度级别必须有 `docs/sources-manifest.json`（或 `medium/sources-manifest.json`、`deep/sources-manifest.json`）

---

## 三、L2 单元测试

### 3.1 测试规模

| 文件 | 行数 | 测试数 | 覆盖范围 |
|------|------|--------|----------|
| `tests/test_walkthrough_output.py` | 755 | 290 | 产出文件格式、内容模式、manifest 完整性 |
| `tests/test_verify_sources.py` | 611 | ~40 | 验证脚本本身的行为（正常/异常/边界） |
| `tests/test_import_graph.py` | 534 | ~30 | import 依赖图提取逻辑 |

总计 **~360 个测试**。

### 3.2 测试分类

#### TestV1Output — 基础格式验证

- 每个 walkthrough 项目（bat、zod、fastapi、gstack、superpowers）的每个 md 文件：
  - 文件存在
  - 非空
  - 包含标题
  - 包含导航链接（next/previous）

#### TestV2Output — 内容质量验证

- 每个 md 文件：
  - 包含至少一个代码块
  - 代码块有语言标注（如 `typescript`、`rust`）
  - 包含架构图或数据流描述

#### TestSourcesManifest — Manifest 校验

- manifest 文件是合法 JSON
- 包含 `schema_version`、`source_project`、`generated_at`、`claims`
- claim ID 格式正确且唯一
- 每个 manifest 至少有 5 个 claims
- `doc_file` 指向的 md 文件实际存在

#### TestSourceCitation — 引用格式

- 代码块不得使用 `// Source:` 标记（必须用 `// Simplified from:`）
- 所有代码块必须有 `// Simplified from:` 引用
- 引用路径格式：`path/to/file:lineStart-lineEnd`

#### TestManifestSourceIntegrity — 源文件交叉验证

- manifest 中 `source_file` 指向的文件在源项目中存在
- `source_lines` 的 end 行不超过文件总行数
- 代码类型的 claim 必须有对应的 manifest entry

### 3.3 测试数据策略

| 数据 | 位置 | 用途 | 大小 |
|------|------|------|------|
| 金色 fixtures | `tests/fixtures/` | CI 可运行的小型 walkthrough 样本 | ~148K（bat/zod/fastapi） |
| 完整样例 | `examples/`（gitignored） | 本地开发的完整 walkthrough 产出 | ~90M |

测试优先查 `tests/fixtures/`，不存在时 fallback 到 `examples/`。项目列表动态发现，不存在的 fixture 自动 `skipIf`。

### 3.4 执行

```bash
# 运行全部测试
python -m pytest tests/ -v

# 只跑 manifest 相关
python -m pytest tests/ -k "manifest" -v

# 只跑 lang 相关
python -m pytest tests/ -k "lang" -v
```

---

## 四、L3 Manifest 验证脚本

`scripts/verify_sources.py` — 317 行，独立于测试套件的命令行工具。

### 4.1 验证流程

```
读取 manifest JSON
    ↓
Schema 校验（jsonschema 库）
    ↓
基础校验：必填字段、ID 格式、claim type 枚举、行号范围
    ↓
源文件存在性检查：source_file 是否存在于 --source-dir
    ↓
行号范围检查：source_lines end ≤ 文件总行数
    ↓
输出：ERRORS / WARNINGS / PASS
```

### 4.2 两种模式

| 模式 | 用途 | 差异 |
|------|------|------|
| Phase 3A 中间态 | 验证阶段，写内容前 | `doc_file`/`doc_line` 可选 |
| `--strict` 最终态 | 内容写完后 | `doc_file`/`doc_line` 必填 |

### 4.3 示例输出

```
============================================================
Project: bat | Depth: brief
Manifest: examples/bat/docs/sources-manifest.json
============================================================
  ✓ All checks passed

============================================================
Project: zod | Depth: brief
============================================================
ERRORS (1):
  ✗ claims[3]: source_lines [120, 350] exceeds file length (298 lines): src/schemas.ts
  ✓ Passed with 1 warning(s)

Summary: 1 passed, 1 failed, 2 total
```

---

## 五、L4 子 Agent 抽检协议

文件：`docs/accuracy-verification-protocol.md`

这是对 walkthrough 最终产出的 5 维度独立验证，由独立子 agent 执行（不共享主对话上下文）。

### 5.1 五个维度

| 维度 | 检查内容 | 通过标准 |
|------|----------|----------|
| 代码例子存在性 | 每个 `// Simplified from:` 引用 → 源文件存在 + 行号正确 + 内容匹配 | 零 VIOLATION |
| 目录结构准确性 | 描述的目录/文件 → `ls` 源项目对应路径 | 100% 存在 |
| API 签名验证 | 函数签名 → 源项目中搜索定义 → 参数列表、返回类型比对 | 关键参数无差异 |
| 版本号验证 | walkthrough 中所有版本号 → 读源项目 `package.json` 等 | 100% 一致 |
| 架构声明验证 | "X 模块负责 Y"、"使用了库 Z" → 搜索 import / 模块定义 | 90%+ 有源码支撑 |

### 5.2 判定标准

- **PASS**：5 项全部通过
- **PARTIAL PASS**：1-2 项有小问题，无严重编造
- **FAIL**：任何检查发现编造内容（不存在的文件/函数/模块）

### 5.3 历史验证记录

`docs/verification-reports/` 目录下保存了 12 轮验证报告（bat r1-r10、zod r3/r6/r9/r12、fastapi r4/r7/r11）。

关键发现和修复：

| 问题 | 检测轮次 | 修复措施 |
|------|----------|----------|
| 编造 `classic layer` 文件结构 | zod r3 | Manifest 机制标记，SKILL.md 规则禁止 |
| 编造 `jwt.py` 模块 | fastapi r4 | Phase 3A 强制读源文件，未验证的 claim 不写入 |
| 代码例子无来源标注 | bat r1 | `// Source:` → `// Simplified from:` 强制格式 |
| 版本号过时 | bat r5 | Phase 3A 要求从 `package.json` 直接读取，不从 README |
| 目录结构编造 | zod r6 | Phase 3A 要求 `ls` 验证每个描述的路径 |

---

## 六、L5 端到端验证

发版前的完整流程验证：

### 6.1 插件安装验证

```bash
# 1. 添加 marketplace
/plugin marketplace add zwyin/project-walkthrough-skill

# 2. 安装插件
/plugin install project-walkthrough@project-walkthrough-skill

# 3. 验证 skill 可用
/project-walkthrough --help    # 应显示 argument-hint

# 4. 实际生成 walkthrough
/project-walkthrough /path/to/some/project --depth brief

# 5. 检查产出
ls project_study_<name>/docs/
ls project_study_<name>/interactive/
```

### 6.2 参数组合验证

| 参数组合 | 预期 |
|----------|------|
| `--depth brief` | 7-8 个 md + 1 HTML |
| `--depth medium` | 12-15 个 md + 1 HTML |
| `--depth deep` | 8-15 个 md + 1 HTML |
| `--depth all` | 三套完整产出 |
| `--audience general` | 含类比理解卡片 + 代码块中文总结 |
| `--audience dev` | 无类比卡片，直接技术分析 |
| `--lang zh` | 中文正文 + 英文术语 |
| `--lang en` | 纯英文 |

### 6.3 平台兼容性

| 环境 | 状态 |
|------|------|
| Claude Code CLI | 已验证安装流程 |
| Claude Code VS Code 扩展 | 理论兼容（skill 共享机制） |
| Gemini CLI | 需手动复制 SKILL.md（未来支持） |

---

## 七、SKILL.md 内置的质量关卡

SKILL.md 本身定义了生成过程中的强制质量检查点：

### 7.1 Phase 3A → 3B 门控

```
Phase 3A: Verify & Build Manifest
    ↓ （manifest 必须完成且 verified: true）
Phase 3B: Write Chapter Content
    ↓ （只写 manifest 中已验证的 claim）
Phase 3C: Validate Coverage
```

**硬规则：** claim 不在 manifest 中 → 不写入文档。没有 "后面再验证"。

### 7.2 引用格式强制

- 必须用 `// Simplified from: path:lines`
- 禁止用 `// Source:`（因为 walkthrough 代码都是简化的，`Source:` 暗示原文照搬）
- 测试自动扫描所有代码块，违反即 FAIL

### 7.3 不可验证声明处理

- Phase 3A 无法验证的 claim → 放入 `unverified` 数组 → **不写入文档**
- 替换为已验证的 claim，或使用不含具体数字/路径的笼统描述

---

## 八、工具链一览

| 工具 | 文件 | 用途 |
|------|------|------|
| manifest 验证 | `scripts/verify_sources.py` | 校验 sources-manifest.json 合法性 + 源文件存在性 |
| import 图提取 | `scripts/import_graph.py` | 从源码提取实际 import 依赖，用于架构图绘制 |
| 测试套件 | `tests/test_*.py` | ~360 个测试覆盖格式/内容/manifest/引用 |
| JSON Schema | `docs/sources-manifest.schema.json` | Manifest 结构定义，verify_sources.py 内置校验 |
| 抽检协议 | `docs/accuracy-verification-protocol.md` | 子 agent 5 维度验证规范 |
| 验证报告 | `docs/verification-reports/` | 12 轮历史验证记录 |

---

## 九、已知的局限和改进方向

| 局限 | 影响 | 改进计划 |
|------|------|----------|
| L4 抽检依赖手动触发 | 不是每次生成都执行 | 目标：每次 walkthrough 生成后自动触发 |
| 无 CI 管道 | push 后不自动验证 | 计划：GitHub Actions + `claude plugin validate` + `pytest` |
| fixtures 只覆盖 brief | 中深度级别的测试依赖本地 `examples/` | 计划：补充 medium/deep fixtures |
| 无 prompt 回归测试 | SKILL.md 改动可能影响生成质量 | 计划：promptfoo 或 skill-creator eval |
| 插件安装测试手动 | 安装流程仍需人工验证 | 计划：E2E 安装自动化脚本 |
