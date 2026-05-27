# Accuracy Enforcement — Final Report

## 终止条件

连续 3 轮零问题，跨 3 个项目类型（CLI Tool / Web App / Library）。

## 验证循环记录

| Round | Project | Type | Result | Issues | Streak |
|-------|---------|------|--------|--------|--------|
| 1 | bat (旧) | CLI | FAIL | 6 个严重问题（虚构代码、版本过时、零 citation） | 0 |
| 2 | bat-r2 | CLI | PASS | 0 | 1 |
| 3 | zod-r3 | Library | PARTIAL PASS | 3（类型计数错、架构图错、Source 标注错） | 0 |
| 4 | fastapi-r4 | Web App | PARTIAL PASS | 2（SSE 标注错、行范围错） | 0 |
| 5 | bat-r5 | CLI | PASS (14 自修复) | 14 Source→Simplified 修正 | 0 |
| 6 | zod-r6 | Library | PASS | 0 | 1 |
| 7 | fastapi-r7 | Web App | PASS (3 自修复) | 3 行范围/标注修正 | 2 |
| 8 | bat-r8 | CLI | PASS (21 自修复) | 21 修正 | 0 |
| 9 | zod-r9 | Library | PASS (8 自修复) | 8 修正 | 0 |
| 10 | bat-r10 | CLI | **ZERO ISSUES** | 0 | **1** |
| 11 | fastapi-r11 | Web App | **ZERO ISSUES** | 0 | **2** |
| 12 | zod-r12 | Library | **ZERO ISSUES** | 0 | **3** |

## Skill 机制演进

### Round 1 → 3: 基础准确性规则

- 添加 Phase 3 Accuracy Rules (6 条)
- 添加 Sources Manifest 强制产出
- 添加验证脚本 `scripts/verify_sources.py`
- 添加测试套件 TestSourcesManifest

### Round 3 → 4: Manifest-first 重构

- **核心改动**: Phase 3 从"边写边记录"改为"先验证再写"
- Phase 3A: 验证声明 → 建 manifest → 3B: 只用已验证的声明写内容
- Manifest 成为写作许可证，不是审计日志

### Round 4 → 8: 细化验证指令

- 枚举/变体列表必须读实际定义
- 架构图箭头必须验证实际 import
- 优先级链必须读实现代码
- 计数声明必须实际数
- Phase 3C 增加 Source/Simplified 审计和行范围审计

### Round 8 → 10: 根治 Source 标注问题

- **禁用 `// Source:` 标签**，全部使用 `// Simplified from:`
- 消除了最频繁的问题类别（占所有问题的 50%+）
- 行范围规则改为"宁缩勿扩"

## 最终 Skill 规则摘要

1. **Manifest-first**: 先验证所有声明并写入 manifest，然后只写已验证的内容
2. **全部 Simplified from:**: 禁用 Source: 标签
3. **行范围保守**: end line <= file length，宁缩勿扩
4. **版本从配置文件**: package.json / Cargo.toml / __init__.py，不从 README
5. **目录结构从 ls**: 不猜测
6. **计数必须实际数**: 或用模糊语言
7. **架构图验证 import**: 箭头必须有源码支撑
8. **不确定就不写**: 用模糊语言替代猜测

## 文件清单

- `SKILL.md` — 主技能定义（含完整规则）
- `docs/sources-manifest-schema.md` — Manifest 设计文档
- `docs/sources-manifest.schema.json` — JSON Schema
- `docs/exploration-protocol.md` — 探索协议（含 Step 6 验证）
- `docs/accuracy-verification-protocol.md` — 验证协议
- `scripts/verify_sources.py` — 自动验证脚本
- `tests/test_walkthrough_output.py` — 157 个测试（含 11 个 manifest 测试）
- `docs/verification-reports/round-N-*.md` — 12 轮验证报告
