# 模块一致性评审 -- project-walkthrough skill

**日期：** 2026-05-08
**范围：** 所有模块的交叉引用一致性、完整性和正确性

## 发现摘要

| 严重程度 | 数量 |
|----------|------|
| 严重 | 1 |
| 主要 | 7 |
| 次要 | 10 |

## 严重问题

### 5.1 SKILL.md 指向 schema.md 而非 schema.json

SKILL.md 第 194 行引用 `docs/sources-manifest-schema.md`（人类可读），但未引用 `docs/sources-manifest.schema.json`（机器可读）。LLM 跟随 SKILL.md 会读到 `.md` 文件，而 `.md` 已与 `.json` 产生偏差（见下）。`verify_sources.py` 正确引用 `.json`。

## 主要问题

### 1.1 source_project 必填字段：schema.md vs schema.json 不一致
- schema.md：required = `["name", "repo_url", "commit_or_tag"]`
- schema.json：required = `["name"]`
- verify_sources.py 只检查 name，与 schema.json 一致但与 schema.md 不一致

### 1.2 claim_summary 不是 required 但应该考虑
- SKILL.md 描述为标准字段，schema.json/verify_sources.py 不强制
- 缺少 claim_summary 的 manifest 人工审阅困难

### 2.1 测试未覆盖 manifest-first 工作流
- 核心准确性承诺（代码来自实际源码）无自动化测试
- `Simplified from:` 引用验证、manifest 行范围验证均缺失

### 2.2 MANIFEST_PROJECTS 硬编码排除 gstack/superpowers
- 最完整的两个示例跳过 manifest 验证

### 4.1 SKILL.md 第 308 行 Source: 矛盾（与架构评审 C1 重复）
### 4.2 accuracy-verification-protocol.md 仍引用 // Source: 格式
### 4.3 README.md 未提及 manifest 系统、验证脚本
### 4.4 TODO.md 多项已过时或已完成

## 次要问题

- source_lines null 在 schema.md 未文档化
- claim ID pattern 未在 validate_basic() 中验证
- verify_sources.py 行计数文件句柄泄漏
- import_graph.py --depth 参数接受但未使用
- test_html_no_innerhtml 用 skip 而非 xfail
- deep 文件计数阈值 >= 8 vs 规范 15-20
- verify_sources.py 和 import_graph.py 无单元测试

## 前 3 优先级

1. **修复 SKILL.md Source: 矛盾 + accuracy-verification-protocol.md**
2. **对齐 schema.md 与 schema.json 的 source_project required 字段**
3. **添加准确性回归测试**
