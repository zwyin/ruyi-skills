# architecture-design.md 问题清单（两轮评审整合）

优先级排序原则：
- P0 = 事实错误/代码 bug，不修会误导或报错
- P1 = 设计原则与实际严重脱节，影响新贡献者理解
- P2 = 描述不够精确，但不影响理解大方向
- P3 = 补充说明，锦上添花

---

## P0 — 事实错误 / 代码 bug

### #1 release.sh 调用不存在的 sync-all.sh
- **位置**: scripts/release.sh 末尾
- **问题**: `bash scripts/sync-all.sh` — 文件不存在，`make release` 执行到此处必报错
- **修改方案**: 删除该行，或替换为提示用户手动运行 brand-sync-tool
- **风险**: 低 — 只改脚本，不影响 skill 功能

### #2 Makefile `make sync` 指向 archived 仓库
- **位置**: Makefile sync 目标
- **问题**: `git subtree pull --prefix=skills/github-safe-publish https://github.com/zwyin/github-safe-publish.git` — 源仓库已 archived
- **修改方案**: 删除 sync 目标
- **风险**: 低 — 删除不可用命令

---

## P1 — 设计原则与实际严重脱节

### #3 P4 Subtree 双向同步 — 整节已废弃
- **位置**: 文档 P4（原第 66-78 行）
- **问题**: subtree 从未成功建立，源仓库已 archived，整个章节误导读者
- **修改方案**: 删除整节
- **风险**: 无 — 纯文档删除

### #4 P6 多品牌推送 — 职责归属错误
- **位置**: 文档 P6（原第 88-97 行）
- **问题**: 多品牌策略应在 brand-sync-tool 文档中，不应在 skill 仓库
- **修改方案**: 删除整节，替换为一段话指向 brand-sync-tool，概述替换范围（SKILL.md name、目录名、marketplace、README、CI、测试、平台文件）
- **风险**: 无 — 纯文档修改

### #5 开发流程仍引用 subtree 和 sync-all.sh
- **位置**: 文档开发流程图（原第 112-119 行）
- **问题**: `日常迭代 → 独立仓库 → subtree pull → sync-all.sh`，全部已废弃
- **修改方案**: 替换为 `直接在 ruyi-skills 开发 → convert.sh → git commit → brand-sync-tool 分发`
- **风险**: 无 — 纯文档修改

### #6 目录结构 skill 名错误
- **位置**: 文档目录结构（原第 24-27 行）
- **问题**: 写的是 `github-safe-publish/`、`project-walkthrough/`，实际是 `ruyi-github-safe-publish/`、`ruyi-project-walkthrough/`
- **修改方案**: 更新为实际目录名
- **风险**: 无 — 纯文档修改

### #7 P5 双层版本引用 subtree
- **位置**: 文档 P5（原第 82-84 行）
- **问题**: "随 subtree 同步" 措辞已过时
- **修改方案**: 改为"直接在 ruyi-skills 仓库中维护"
- **风险**: 无 — 纯文档措辞修改

---

## P2 — 描述不够精确

### #8 P7 生成文件隔离与实际不符
- **位置**: 文档 P7（原第 99-103 行）
- **问题**: 文档说平台文件输出到 gitignored 的 dist/，实际 ruyi-project-walkthrough 的平台文件（cursor/.windsurf/.opencode）已 git 跟踪并提交在 skill 目录内；ruyi-github-safe-publish 的平台文件在 dist/ 下未被跟踪。两个 skill 策略不一致
- **修改方案**: 分述两个 skill 的实际策略。说明 convert.sh 输出到根 dist/（gitignored），各 skill 内的平台文件是生成后手动提交的
- **风险**: 低 — 纯文档修改

### #9 目录结构缺少实际存在的文件
- **位置**: 文档目录结构
- **问题**: 缺少 .claude-plugin/、根 tests/、scripts/check_self_contained.py、各 skill 内的 .claude-plugin/（含 plugin.json）、.github/ 等
- **修改方案**: 补充实际存在的文件和目录
- **风险**: 无 — 纯文档补充

### #10 Makefile 命令表过时
- **位置**: 文档 Makefile 命令表（原第 121-130 行）
- **问题**: 列出了不可用的命令（sync），缺少实际可用的命令（check）
- **修改方案**: 删除 sync，标注 release 需修复，补充 check
- **风险**: 无 — 纯文档修改

### #11 P8 质量门禁描述笼统
- **位置**: 文档 P8（原第 105-109 行）
- **问题**: 只概括性描述，未列出实际 CI 的 4 个 job
- **修改方案**: 列出 4 个 job 及其配置概要
- **风险**: 无 — 纯文档补充

---

## P3 — 补充说明

### #12 新增：品牌分发章节
- **修改方案**: 在文档中加一段简要说明品牌分发机制，指向 brand-sync-tool
- **风险**: 无

### #13 新增：已归档仓库章节
- **修改方案**: 说明 github-safe-publish 和 project-walkthrough-skill 已 archived，代码统一维护在 ruyi-skills
- **风险**: 无

### #14 brand-sync-tool README 补充
- **修改方案**: 补充多品牌策略表格、brand-config.json 说明、转换覆盖范围清单、sync.sh 注释修正
- **风险**: 低 — 只改 sync.sh 注释和 README

---

## 风险评估总结

| 优先级 | 数量 | 改动类型 | 引入 bug 风险 |
|--------|------|---------|--------------|
| P0 | 2 | 修代码 bug（release.sh、Makefile） | 低 — 删除死代码 |
| P1 | 5 | 纯文档修改 | 无 |
| P2 | 4 | 纯文档修改 | 无 |
| P3 | 3 | 文档 + sync.sh 注释 | 低 |

所有修改**不涉及 skill 功能代码**，只涉及：
- 文档（architecture-design.md、README.md）
- 死代码清理（release.sh 末尾一行、Makefile sync 目标）
- 注释修正（sync.sh 头部注释）
