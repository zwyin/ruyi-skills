# 文档修改大纲

分两部分：ruyi-skills 和 brand-sync-tool 各自要改什么。

---

## 一、ruyi-skills/docs/architecture-design.md

### A. 删除

| # | 原章节 | 原因 |
|---|--------|------|
| 1 | P4 Subtree 双向同步（整节含命令示例） | subtree 从未成功建立，源仓库已 archived |
| 2 | P6 多品牌推送（整节含品牌表格） | 多品牌策略是 brand-sync-tool 的职责，不属于 skill 仓库文档 |
| 3 | 目录结构中的根级 `dist/` | 被 .gitignore 排除，不应出现在正式目录结构中 |
| 4 | 目录结构中的 `scripts/sync-all.sh` | 文件不存在 |
| 5 | Makefile 命令表中的 `make sync` | 依赖 subtree pull，源仓库已 archived，不可用 |

### B. 修改

| # | 原章节 | 修改内容 |
|---|--------|---------|
| 1 | 目录结构 | skill 名从 `github-safe-publish/` 改为 `ruyi-github-safe-publish/`（已发生的重命名，文档需跟上）；`project-walkthrough/` 改为 `ruyi-project-walkthrough/`；删除不存在的文件；补充实际存在的 `.claude-plugin/`、根 `tests/`、`scripts/convert.sh`、`scripts/release.sh`、`scripts/check_self_contained.py` |
| 2 | P5 双层版本 | 去掉原文中"随 subtree 同步"的措辞，改为"直接在 ruyi-skills 仓库中维护" |
| 3 | P7 生成文件隔离 → 改为 P5 平台文件管理 | 两个 skill 的平台文件策略不同，需分述：ruyi-project-walkthrough 的 cursor/.windsurf/.opencode 文件已 git 跟踪并提交在 skill 目录内；ruyi-github-safe-publish 的平台文件在 dist/ 下但未被 git 跟踪。convert.sh 输出到根 dist/（gitignored），各 skill 目录内的平台文件是 convert.sh 或 brand-sync-tool 生成后手动提交的 |
| 4 | P8 质量门禁 | 更新为实际 CI 内容：4 个 job — test-github-safe-publish（矩阵 ubuntu+macOS, python 3.10+3.12, 覆盖率 95%）、test-project-walkthrough（ubuntu, python 3.12）、structure-check（marketplace.json 校验 + skill 自包含检查）、collection-scripts |
| 5 | 开发流程 | 简化为：所有开发在 ruyi-skills 完成，不再有 subtree 流程 |
| 6 | Makefile 命令表 | 保留可用命令（test/ci/check/convert/clean）。`make release` 调用的 release.sh 末尾引用不存在的 sync-all.sh，属于 bug，需修复后保留或删除该 make 目标 |
| 7 | 目录结构中的 `scripts/release.sh` | 保留（文件存在），但需标注 release.sh 末尾调用不存在的 sync-all.sh，需修复 |

### C. 保留

| # | 原章节 | 说明 |
|---|--------|------|
| 1 | P1 Skill 自包含 | 不变 |
| 2 | P2 渐进展示 | 不变 |
| 3 | P3 单一 marketplace | 不变 |
| 4 | `.claude-plugin/` 目录 | 确认结构不变（marketplace.json），目录结构中保留 |

### D. 新增

| # | 新章节 | 内容 |
|---|--------|------|
| 1 | 品牌分发（P7） | 一段话说明：通过外部 brand-sync-tool 分发到 paoding/davinci/doraemon 品牌仓库，详见 brand-sync-tool 仓库 |
| 2 | 已归档仓库（P8） | 一段话说明：github-safe-publish 和 project-walkthrough-skill 已 archived，代码统一维护在 ruyi-skills |

### 修改后文档结构

```
# ruyi-skills 架构设计

## 目录结构
（更新为实际结构：skill 名 ruyi-xxx，保留 .claude-plugin/、tests/、scripts/ 下实际存在的文件，去掉不存在的文件）

## 设计原则
### P1. Skill 自包含（不变）
### P2. 渐进展示（不变）
### P3. 单一 marketplace（不变）
### P4. 双层版本（原 P5，去掉 subtree 措辞）
### P5. 平台文件管理（替换原 P7，分述两个 skill 的实际策略）
### P6. 质量门禁（原 P8，列出实际 CI 4 个 job）
### P7. 品牌分发（新增，简要说明 + 指向 brand-sync-tool）
### P8. 已归档仓库（新增）

## 开发流程
（简化：直接在 ruyi-skills 开发 → convert.sh 生成平台文件 → 手动提交 → brand-sync-tool 分发）

## Makefile 命令
（保留可用的 test/ci/check/convert/clean，标注 release 需修复）
```

---

## 二、brand-sync-tool/README.md

当前 README 刚刚重写过，已包含：
- 工作流程图（4 步）
- Q&A（推送机制、output/ 目录、是否需要手动 clone）
- 用法（sync/verify/dry-run）
- 目录结构
- 日常使用场景
- 注意事项

### 需要补充的内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | 多品牌策略表格 | 从 ruyi-skills 原文档的 P6 搬过来，放在 README 的"目录结构"章节之后。格式：品牌 | GitHub 仓库 | 受众 | README 语言。注意 ruyi 自身不在此表格中（ruyi-skills 是源仓库，不是 sync 目标） |
| 2 | brand-config.json 说明 | 各字段含义（repo_url、前缀、描述等） |
| 3 | brands/ 目录维护说明 | 品牌专用 README 如何维护、什么时候需要更新 |
| 4 | 转换覆盖范围清单 | sync.sh 实际替换了哪些内容（SKILL.md name、目录名、marketplace、README、CI、测试、平台文件等） |
| 5 | sync.sh 注释修正 | sync.sh 开头注释仍写着 "single orphan commit"，需更新为 "clone + incremental commit" |

---

## 三、不需要改的

| 文件 | 原因 |
|------|------|
| github-safe-publish（已 archived） | 只读，不再维护 |
| project-walkthrough-skill（已 archived） | 只读，不再维护 |
| 3 个品牌仓库（paoding/davinci/doraemon） | 由 sync.sh 自动生成，手动改会被覆盖 |
| brand-sync-tool/verify-sync.sh | 工具脚本，不需要文档 |
| ruyi-skills 的 README.md / CLAUDE.md / CHANGELOG.md | 不在本次 architecture-design.md 修改范围内 |
