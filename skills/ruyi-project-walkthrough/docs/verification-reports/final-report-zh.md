# 准确性强制执行 — 最终报告

## 终止条件

连续 3 轮零问题，覆盖 3 种项目类型（CLI 工具 / Web 应用 / 库）。

## 验证循环完整记录

| 轮次 | 项目 | 类型 | 结果 | 问题数 | 连续 |
|------|------|------|------|--------|------|
| 1 | bat（旧产物） | CLI | 失败 | 6（虚构代码、版本过时、零 citation） | 0 |
| 2 | bat-r2 | CLI | 通过 | 0 | 1 |
| 3 | zod-r3 | 库 | 部分通过 | 3（类型计数错、架构图错、Source 标注错） | 0 |
| 4 | fastapi-r4 | Web 应用 | 部分通过 | 2（SSE 标注错、行范围错） | 0 |
| 5 | bat-r5 | CLI | 通过（14 自修复） | 14 Source→Simplified 修正 | 0 |
| 6 | zod-r6 | 库 | 通过 | 0 | 1 |
| 7 | fastapi-r7 | Web 应用 | 通过（3 自修复） | 3 行范围/标注修正 | 2 |
| 8 | bat-r8 | CLI | 通过（21 自修复） | 21 修正 | 0 |
| 9 | zod-r9 | 库 | 通过（8 自修复） | 8 修正 | 0 |
| 10 | bat-r10 | CLI | **零问题** | 0 | **1** |
| 11 | fastapi-r11 | Web 应用 | **零问题** | 0 | **2** |
| 12 | zod-r12 | 库 | **零问题** | 0 | **3** |

## 核心问题与解决过程

### 问题一：内容编造

**表现：** Walkthrough 中出现源码里不存在的文件、函数、目录结构。例如 zod 的 classic layer 被描述为 16 个独立类型文件（string.ts、number.ts 等），实际是 schemas.ts + checks.ts 两个合并文件。FastAPI 被描述为有 jwt.py 安全模块，实际不存在。

**根因：** Skill 没有强制要求"写之前先验证"。生成者凭记忆或 README 推断内容，没有读实际源码。

**解决：** Phase 3 重构为 manifest-first —— 先验证所有声明并写入 manifest，然后只写已验证的内容。Manifest 成为"写作许可证"，不是审计日志。

### 问题二：Source 标注错误

**表现：** 代码块标注为 `// Source:`（声称逐字复制）但实际做了简化、省略、重排。这是最频繁的问题，占所有问题的一半以上。

**根因：** 生成者倾向于默认使用 `// Source:`，只在被抓住时才改为 `// Simplified from:`。这是一种"乐观标注"——认为自己写了精确代码，但实际总有细微差异。

**解决：** 禁用 `// Source:` 标签。所有代码块统一使用 `// Simplified from: path:lines`。理由：walkthrough 中的代码总有某种程度的简化（缩进调整、注释省略、上下文裁剪），`Simplified from:` 永远诚实，`Source:` 需要逐字符验证且在多轮测试中从未可靠执行。

### 问题三：行范围差一

**表现：** manifest 中声明的行范围超出文件长度，或者不覆盖引用的注释/注解行。

**根因：** 生成者凭记忆指定行号，或从代码内容推断行号，没有实际读文件验证。

**解决：** 规则改为"宁缩勿扩"——行范围的 end line 必须 <= 文件总行数。Phase 3C 要求重新读每个引用的源文件确认行范围。

### 问题四：架构图关系错误

**表现：** Zod 的 classic/mini/core 被画成串联层级（classic → mini → core），实际是 classic 和 mini 并列地包装 core。

**根因：** 从目录结构推断依赖关系，没有验证实际 import 语句。

**解决：** 架构图中的每个箭头必须通过验证实际 import 语句来确认。如果 A 和 B 都 import C 但不互相 import，必须画为并列，不能画为链式。

## Skill 机制的演进

### 第一阶段（Round 1-3）：基础规则

- 添加 6 条准确性规则
- 添加 sources-manifest.json 强制产出
- 添加自动验证脚本 `scripts/verify_sources.py`
- 添加 11 个 manifest 测试

### 第二阶段（Round 3-4）：Manifest-first 重构

- Phase 3 从"边写边记录"改为"先验证再写"
- 3A 验证 → 3B 写作 → 3C 校验的三段式流程
- 这是整个机制最关键的一次改动

### 第三阶段（Round 4-8）：细化验证指令

- 枚举/变体列表必须读实际定义
- 架构图箭头必须验证实际 import
- 优先级链必须读实现代码
- 计数声明必须实际数（不能用估算）
- Phase 3C 增加 Source/Simplified 审计和行范围审计

### 第四阶段（Round 8-10）：根治标注问题

- 禁用 `// Source:` 标签
- 行范围规则改为"宁缩勿扩"
- Phase 3C 简化（去掉 Source/Simplified 审计步骤，因为不再有 Source 标签）

## 最终规则总结

| 规则 | 内容 |
|------|------|
| Manifest-first | 先验证所有声明写入 manifest，然后只写已验证内容 |
| 统一 Simplified from: | 禁用 Source: 标签 |
| 行范围保守 | end line <= file length，宁缩勿扩 |
| 版本从配置文件 | package.json / Cargo.toml / \_\_init\_\_.py，不从 README |
| 目录从 ls | 不猜测，实际 ls 验证 |
| 计数必须实际数 | 或用"多个"/"数十个"等模糊语言 |
| 架构图验证 import | 箭头必须有源码 import 支撑 |
| 不确定就不写 | 用模糊语言替代猜测 |

## 产出文件

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 主技能定义（含完整规则和 Phase 3 三段式流程） |
| `docs/sources-manifest-schema.md` | Manifest 设计文档 |
| `docs/sources-manifest.schema.json` | JSON Schema 定义 |
| `docs/exploration-protocol.md` | 探索协议（含 Step 6 交叉验证） |
| `docs/accuracy-verification-protocol.md` | 准确性验证协议 |
| `scripts/verify_sources.py` | 自动验证脚本 |
| `tests/test_walkthrough_output.py` | 157 个测试（含 11 个 manifest 测试） |
| `docs/verification-reports/round-N-*.md` | 12 轮验证报告 |
