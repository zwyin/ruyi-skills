---
name: ruyi-version-check
version: "0.1.1"
description: |
  版本一致性检查器（ruyi-version-check，也叫版本检查 / 版本一致性检查）：核对 skill 合集里每一处版本号是否与 canonical（SKILL.md frontmatter）一致，发版前体检或版本错乱排查时用。覆盖合集层（marketplace.json vs CHANGELOG）和每个 skill 的 frontmatter / plugin.json / marketplace.json / Phase 0 banner / --version 文档 / README badge / CHANGELOG / dist 平台副本 / 测试里的硬编码字面量。产出 PASS/WARN/FAIL 报告，每条带 file:line + 期望值 + 修复提示，纯只读不改文件。触发场景：发版前体检、版本号对不上、badge 跟实际版本不一致、CHANGELOG 落后于 marketplace、dist 漂移、用户报告显示旧版本、接入新 skill 后核对。不要用于：升级依赖版本（npm/pip）、git log 查 commit 历史、bump 版本号这个发版动作本身、Python/Node 运行时版本、node_modules 版本冲突。
argument-hint: "[--root <path>] [--skill <name>] [--format text|json] [--strict]"
---

# ruyi-version-check — 版本一致性检查器

只读核对一个 skill 合集里所有版本号是否一致。不 bump、不改文件、不联网——读每一处版本声明，与 canonical（SKILL.md frontmatter）比对，不一致就报出来。

## 何时跑

- **发版前**：bump 完版本号、跑 release.sh 之后、commit/push 之前
- **怀疑版本错乱**：用户报告"显示旧版本""badge 不对""CHANGELOG 跟不上"
- **CI**：每次 push 跑一次，版本漂移直接红灯
- **接入新 skill 后**：确认新 skill 的版本各处都挂上了

## 何时**不**跑（近邻误触发）

- 升级依赖版本（npm install / pip install）→ 这是包管理，不是版本一致性
- `git log` / 看 commit 历史 → 那是 git 的事
- "帮我 bump 一下版本号" → 那是 release.sh 的动作，本 skill 只读不写
- Python/Node 运行时版本、node_modules 版本冲突 → 与 skill 版本无关

## 怎么跑

```bash
# 检查整个合集（默认当前目录）
python3 skills/ruyi-version-check/scripts/validate_versions.py --root .

# 只查单个 skill
python3 skills/ruyi-version-check/scripts/validate_versions.py --root . --skill ruyi-project-walkthrough

# JSON 输出（给 CI / 其他工具消费）
python3 skills/ruyi-version-check/scripts/validate_versions.py --root . --format json

# 严格模式（发版前建议）：WARN 也算不通过
python3 skills/ruyi-version-check/scripts/validate_versions.py --root . --strict
```

退出码：`2` 有 FAIL；默认模式只有 WARN 时 `0`（WARN 不阻塞 CI）；加 `--strict` 时只有 WARN → `1`（发版前体检用）。

## 报告解读

```
=== ruyi-version-check ===
root: /path/to/ruyi-skills
collection version: 0.9.4

[FAIL] CHANGELOG.md:3
      collection CHANGELOG latest: expected 0.9.4, found 0.9.0
      -> release.sh only rewrites existing entries; insert the missing version block

[WARN] dist/opencode/.opencode/skills/ruyi-project-walkthrough/SKILL.md:3
      dist/opencode frontmatter: expected 1.6.5, found 1.6.4
      -> dist drift; rerun `bash scripts/convert.sh --all`

Summary: 1 FAIL, 5 WARN, 11 PASS (exit 2)
```

每条 finding 含：
- **级别**：`FAIL`（必须修，发版阻塞）/ `WARN`（可能要修，人工判断）/ `PASS`（默认不显示）
- **位置**：`file:line`
- **期望/实际**：canonical 应是多少，实际找到多少
- **修复提示**：一句话告诉你怎么修

## 检查项清单

**合集层：**
- `.claude-plugin/marketplace.json` 的 collection version（semver 格式）
- `CHANGELOG.md` 最新 `## [X.Y.Z]` 条目 == collection version

**每个 skill**（canonical = SKILL.md frontmatter `version`）：
- `.claude-plugin/plugin.json` `"version"`
- `.claude-plugin/marketplace.json` `"version"`
- skill 自己的 `CHANGELOG.md` 最新条目
- skill 自己的 `README.md` version badge
- 合集 `README.md` / `README.en.md` 里该 skill 的 badge 存在且版本对
- SKILL.md 正文里的 Phase 0 banner（`> **Version X.Y.Z**`）
- SKILL.md 正文里的 `--version` 文档字符串
- SKILL.md 正文里的启动版本串（如 `Project Walkthrough vX.Y.Z`，无 `--version` 前缀的形式）

**dist 平台副本**（WARN，不阻塞但提示）：
- `dist/opencode`、`dist/cursor`、`dist/windsurf` 里对应 skill 的 frontmatter + banner
- 不一致 → 提示 `rerun bash scripts/convert.sh --all`（dist 是生成物，重跑就修复，**不要手改**）

**测试字面量**（WARN）：
- `tests/*.py` 里硬编码的版本字面量与 canonical 不符
- 可能是过期断言（要改），也可能是测试 fixture 的假数据（忽略）—— hint 会提示区分

## 常见问题修复指引

| 报错 | 根因 | 修法 |
|---|---|---|
| Phase 0 banner != frontmatter | release.sh 的 sed 模式匹配不到 `> **Version X.Y.Z**` 格式 | 手动改 SKILL.md banner，或扩展 release.sh 加这个模式 |
| collection CHANGELOG 滞后 | release.sh 只能改写已存在的 `## [X.Y.Z]` 标题，不会 insert | 手动补 CHANGELOG 条目 |
| README badge != frontmatter | 手改版本号时忘了 badge | 手动改 badge URL，或让 release.sh 覆盖 |
| dist 副本漂移 | 改了 SKILL.md 但没重跑 convert.sh | `bash scripts/convert.sh --all` |
| 测试字面量过期 | release.sh 改了版本但测试里的硬编码没动 | 判断是断言还是 fixture 数据，分别处理 |

## 范围边界（不做什么）

- **不 bump 版本**：只读检查，不修改任何文件
- **不检查 description 文本一致性**：SKILL.md / plugin.json / marketplace.json 三处 description 措辞不同是已知问题，留给"触发契约优化"那步
- **不管 frontmatter schema**：字段规约（triggers / allowed-tools 该有什么）留给"skill 编写规范"
- **不管自包含 / 进度披露**：那是 check_self_contained.py 和独立任务的职责
- **不通用化**（pilot 阶段）：当前聚焦 ruyi-skills 自己的结构，参数化已预留但未充分测试外部合集

## 与现有工具的关系

- **`skills/ruyi-github-safe-publish/scripts/validate_skill.sh`**：只覆盖 1 个 skill 的 4 处，本 skill 是它的泛化 + 扩展（合集层 + dist + banner + test 字面量）。两者可共存，本 skill 不替换它。
- **`scripts/check_self_contained.py`**：检查 SKILL.md/references 不外链，与本 skill 正交。
- **`hooks/session-start` + `check_update.sh`**：运行时通知用户远端有新版，与本 skill（静态校验本地一致性）正交。
