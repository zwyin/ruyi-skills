# 代码评审：project-walkthrough 脚本和测试

**日期：** 2026-05-08
**范围：** verify_sources.py, import_graph.py, test_walkthrough_output.py

## 发现摘要

| 严重程度 | 数量 |
|----------|------|
| 主要 | 11 |
| 次要 | 12 |
| 挑剔 | 5 |

## verify_sources.py

### [主要] Claim ID 模式未验证
schema 要求 `^claim-\d{3,}$`，validate_basic() 仅检查重复，不验证格式。ID 为 "foo" 可通过基本验证。

### [主要] source_lines 空列表错误信息误导
null 跳过正确，但空列表 `[]` 的错误信息 "必须恰好有 2 个元素" 不如 "必须是 array 或 null" 清晰。

### [主要] 行计数文件句柄泄漏（第 188 行）
`sum(1 for _ in open(...))` 未显式关闭。需改用 `with` 语句。

### [次要] additionalProperties:false 仅 jsonschema 强制
validate_basic() 不检查额外字段，jsonschema 缺失时无法捕获拼写错误。

### [次要] depth/audience 枚举未在 validate_basic() 中验证
### [次要] info 消息从不显示
### [次要] 无单元测试覆盖

## import_graph.py

### [主要] Python from . import X 未处理
正则 `\.[a-zA-Z0-9_.]*` 要求点后至少一个字母数字，遗漏 `from . import X`、`from .. import X`。

### [主要] Python 项目内绝对导入被忽略
只提取相对导入，绝对导入 `from mypackage.sub import X` 完全遗漏。

### [主要] Rust mod 声明未解析
只处理 `use crate::` 和 `use super::`，遗漏最基本的 `mod submodule;`。

### [主要] TS 动态导入和 re-export 遗漏
遗漏 `import('./module')`、`export { X } from './module'`、`export * from './module'`。

### [次要] --depth 参数接受但未使用
### [次要] 未处理符号链接或循环符号链接
### [次要] Python 多行导入（反斜杠续行）未处理

## test_walkthrough_output.py

### [主要] HTML 自包含测试逻辑缺陷
`assert "A" not in content or "B" not in content or "C" not in content` — 任一条件为 false 即通过，允许外部 CSS 链接。

### [主要] test_html_no_innerhtml 用 skip 而非 xfail
已知问题被静默跳过，从不捕获回归。

### [主要] MANIFEST_PROJECTS 硬编码
排除 gstack/superpowers，最完整的示例跳过验证。

### [主要] VALID_CLAIM_TYPES 重复定义
verify_sources.py 和 test_walkthrough_output.py 各自定义，添加类型需同步更新两处。

### [次要] JS 语法验证用 node -e 执行而非 --check
### [次要] V1/V2 项目列表硬编码
### [次要] 导航检查依赖中文（←、下一章），英文输出会失败
### [次要] unverified claim 验证无测试

## 前 5 修复

1. **import_graph.py Python 相对导入解析** — `from . import X`、`from .. import X`
2. **import_graph.py Rust mod 声明**
3. **verify_sources.py Claim ID 模式验证**
4. **重复验证常量提取到共享模块**
5. **HTML 自包含测试逻辑修正**
