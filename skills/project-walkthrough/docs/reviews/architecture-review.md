# 架构评审：project-walkthrough skill

**日期：** 2026-05-08
**范围：** SKILL.md + 5 份引用文档 + 脚本 + 测试 + 示例

## 发现摘要

| 严重程度 | 数量 | 关键问题 |
|----------|------|----------|
| 严重 | 2 | P1（schema 无效的中间 manifest），D1（manifest 双重身份） |
| 主要 | 12 | C1, C3, P2-P5, R1-R2, D3, E1, E3, S1-S2 |
| 次要 | 9 | C2, C4-C6, P6, R3-R4, D2, D5, E2, E5 |
| 挑剔 | 3 | D4, E4, S3 |

## 严重问题

### P1. Phase 3A 生成 schema 无效的 manifest

SKILL.md 第 192 行：`doc_file` 和 `doc_line` "will be filled in Phase 3B"。但 JSON schema 将两者都标记为 `required`。Phase 3A 的输出定义上不符合 schema，无法在 3A 和 3B 之间运行验证脚本。

**修复：** 在 schema 中将 `doc_file` 和 `doc_line` 设为可选，或添加 `phase` 字段区分两种状态。

### D1. Manifest 概念双重身份

SKILL.md 第 162 行声明 "manifest is a write permit, not an audit log"。但 schema 包含 `generated_at` 时间戳、后期填入的 `doc_line`、事后验证——这些是审计日志特征。当前设计是混合体，导致 P1 的 schema 验证问题。

**修复：** 明确承认双重性质：Phase 3A 生成 verification manifest（无文档位置），Phase 3B 丰富为 traceability manifest（添加文档位置）。

## 主要问题

### C1. SKILL.md 内部 Source: vs Simplified from: 矛盾
- 第 188、214 行：禁用 `// Source:`
- 第 308 行：仍将 `// Source:` 显示为有效格式
- **修复：** 删除第 308 行的 `// Source:` 示例

### C3. accuracy-verification-protocol.md 未被 SKILL.md 引用
- 包含子代理验证协议，但 SKILL.md Phase 5 有自己的验证清单，未引用此协议
- **修复：** 从 Phase 5 引用

### R1. 准确性规则在 SKILL.md 中出现三次
- Phase 3A（167-200行）、Accuracy Rules（241-268行）、Documentation Standards（312-320行）
- "Read actual source" 出现在 174、259、318 行
- **修复：** 保留 Phase 3A 为权威版本，其他改为交叉引用

### E3. Deep 模板规范 vs 实际差距 2.5x
- 规范：15-20 章节，实际 gstack/deep 8 文件，测试接受 >= 8
- **修复：** 将模板调低或提高测试门槛

### S1. SKILL.md 407 行过长
- Phase 3 密集规则 106 行，LLM 难以在单上下文中可靠遵循
- **修复：** 拆分：SKILL.md（流程 ~150 行）+ 验证规则文档 + 文档标准

### S2. 测试覆盖结构但不覆盖准确性
- 44 个结构测试，0 个准确性测试（引用存在性、行范围、版本号）
- **修复：** 添加 3 个自动化准确性测试

## 前 5 修复优先级

1. **解决 Source: 矛盾**（C1, R2）— 5 分钟
2. **修复 schema 支持 Phase 3A 中间状态**（P1, D1）— 30 分钟
3. **整合准确性规则**（R1, R2, R4）— 减少 ~60 行 — 1 小时
4. **添加准确性测试**（S2）— 2-3 小时
5. **协调深度模板与实际**（E3）— 30 分钟
