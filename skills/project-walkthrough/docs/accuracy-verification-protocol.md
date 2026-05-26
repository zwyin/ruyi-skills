# Accuracy Verification Protocol

准确性验证协议：用于检验 walkthrough 生成是否遵循准确性规则。

## 发现问题的方法

### 阶段 1：生成 walkthrough

对目标项目运行 skill，生成 brief 级别的 walkthrough。

源项目存放位置：`examples/_src_<project>/`（shallow clone）。

### 阶段 2：子 agent 抽检

分派一个独立的子 agent（code-reviewer 类型），执行以下检查：

#### 检查 1：代码例子存在性

从生成的 md 文件中提取所有代码块。对每个代码块：
1. 查找其 source citation（`// Simplified from:` 注释）
2. 如果有 citation，去源项目中验证文件和行号是否存在
3. 如果没有 citation，标记为 VIOLATION

**判定标准：** 零 VIOLATION 通过。

#### 检查 2：目录结构准确性

从生成的 md 文件中提取所有描述目录结构的段落（通常包含 `src/`、`lib/` 等路径树）。
对每个描述的目录/文件：
1. 去 `ls` 源项目的对应路径
2. 记录哪些存在、哪些不存在

**判定标准：** 描述的路径 100% 存在则通过。不存在的路径 = 编造。

#### 检查 3：API 签名验证

从生成的 md 文件中提取所有函数签名描述。对每个：
1. 在源项目中搜索该函数名
2. 比较参数列表、返回类型是否一致
3. 记录差异

**判定标准：** 关键参数无差异通过。可选参数顺序差异可接受。

#### 检查 4：版本号验证

提取 walkthrough 中提到的所有版本号。对每个：
1. 读取源项目的 `package.json` / `Cargo.toml` / `pyproject.toml`
2. 比对是否一致

**判定标准：** 100% 一致通过。

#### 检查 5：架构声明验证

提取 walkthrough 中的架构声明（"X 模块负责 Y"、"使用了库 Z 进行 W"）。
对每个声明：
1. 在源项目中搜索相关 import / 模块定义
2. 确认声明有源码支撑

**判定标准：** 90%+ 有源码支撑通过。

### 阶段 3：生成报告

子 agent 输出结构化报告：

```
## Verification Report: <project>

### Check 1: Code Examples
- Total code blocks: N
- With source citation: N
- Verified against source: N
- VIOLATIONS: [list]
- PASS/FAIL

### Check 2: Directory Structure
- Paths described: N
- Paths verified: N
- FABRICATED: [list]
- PASS/FAIL

### Check 3: API Signatures
- Signatures checked: N
- Exact matches: N
- Minor diffs: [list]
- MAJOR FABRICATIONS: [list]
- PASS/FAIL

### Check 4: Version Numbers
- Versions stated: N
- Verified: N
- STALE: [list]
- PASS/FAIL

### Check 5: Architecture Claims
- Claims checked: N
- Source-backed: N
- UNVERIFIABLE: [list]
- PASS/FAIL

### Overall: PASS / PARTIAL PASS / FAIL
```

### 判定标准

- **PASS：** 所有 5 项检查通过
- **PARTIAL PASS：** 1-2 项检查有小问题，无严重编造
- **FAIL：** 任何检查发现编造内容（不存在的文件/函数/模块）

## 上次验证结果（2026-05-07）

### 项目：zod（Library）
- FAIL：编造了 `classic layer` 文件结构（源码中不存在）
- FAIL：代码例子未标注来源文件

### 项目：fastapi（Web App）
- FAIL：编造了 `jwt.py` 模块（源码中不存在）
- FAIL：代码例子未标注来源文件

### 项目：bat（CLI Tool）
- 部分代码例子有合理的简化标注
- 目录结构描述基本准确

## 重测结果（2026-05-07，manifest 机制实施后）

### 方法
为 bat/zod/fastapi 的 walkthrough 生成 sources-manifest.json，然后用独立子 agent 按协议逐项验证。

### 结果

#### bat（CLI Tool）— PARTIAL PASS
- 代码例子：3 个抽查全部 PASS（源文件存在，内容匹配）
- 目录结构：PASS（所有描述路径均存在）
- 版本号：FAIL（walkthrough 说 0.25.x，Cargo.toml 实际为 0.26.1）
- 架构声明：PASS（controller.rs、paging.rs、diff.rs 均验证通过）

#### zod（Library）— FAIL
- 代码例子：2/3 PASS，1 个部分匹配（$ZodIssue 声称有 received 字段但源码中不存在）
- 目录结构：FAIL（classic layer 声称 16 个独立类型文件如 string.ts、number.ts，实际是 schemas.ts + checks.ts 合并结构）
- 版本号：PASS（walkthrough 用 "4.x" 范围，实际 4.4.3）
- 架构声明：PASS

#### fastapi（Web App）— FAIL
- 代码例子：3 个抽查全部 PASS
- 目录结构：FAIL（声称存在 jwt.py 安全模块，实际不存在）
- 版本号：FAIL（walkthrough 说 0.115.x，实际 0.136.1）
- 架构声明：PASS

### 机制有效性评估

| 指标 | 实施前 | 实施后 |
|------|-------|-------|
| 编造内容是否被检测 | 无机制，靠人工 | manifest 标记了所有已知问题 |
| 代码例子来源可追溯 | 否 | 是（每个 claim 有 source_file + source_lines） |
| 验证脚本自动化 | 无 | `scripts/verify_sources.py` 可自动检查 |
| 测试覆盖 | 0 个准确性测试 | 11 个 manifest 测试 + 验证脚本 |

### 结论

1. **Manifest 机制成功捕获了所有已知的准确性问题**（3 个版本过时、2 个编造路径/模块、1 个字段不准确）
2. **现有 walkthrough 仍然有准确性问题** — 这些是 manifest 实施前的旧产物。需要按新规则重新生成才能修复
3. **强制执行机制已就绪**：SKILL.md 规则 + manifest schema + 验证脚本 + 测试套件形成了完整链路
4. **下一步**：用新规则重新生成 walkthrough（zod/fastapi/bat），目标是全部达到 PASS
