# ruyi-skills 架构设计

## 目录结构

```
ruyi-skills/
├── .claude-plugin/
│   └── marketplace.json            # 单一 plugin，列所有 skills，用户一次安装
├── .github/
│   ├── workflows/
│   │   └── test.yml                # CI: 各 skill 测试 + 结构验证
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                           # 仓库级文档
│   └── architecture-design.md
├── scripts/                        # 合集级工具
│   ├── sync-all.sh                 # 推送到 4 个 remote（品牌差异化）
│   ├── release.sh                  # 版本 bump + 同步 + tag
│   └── convert.sh                  # 多平台转换（输出到 dist/）
├── skills/                         # 各 skill（git subtree 管理）
│   ├── github-safe-publish/
│   │   ├── SKILL.md                # skill 唯一事实源
│   │   ├── references/             # 渐进展示，保持 SKILL.md 精简
│   │   ├── scripts/                # skill 专属脚本
│   │   └── tests/                  # skill 专属测试
│   └── project-walkthrough/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── tests/
├── dist/                           # gitignored，convert.sh 输出
├── Makefile
├── README.md                       # 中文版（ruyi/paoding）
├── README.en.md                    # 英文版（davinci/doraemon）
├── CHANGELOG.md
├── CLAUDE.md
└── LICENSE
```

## 设计原则

### P1. Skill 自包含

**做法**：SKILL.md 及 references/ 内的所有链接，不得指向 skill 目录外的文件。每个 skill 必须能被独立提取、安装和使用。

**优势**：skill 可以脱离合集独立运行；合集仓库的改动不会破坏单个 skill 的完整性。

**例外**：仓库根 `scripts/` 只放合集级工具（sync-all.sh、release.sh、convert.sh），不属于任何 skill。

### P2. 渐进展示

**做法**：SKILL.md 控制在 500 行以内，详细规则、配置说明、模板等内容放在 `references/` 子目录。

**优势**：SKILL.md 作为入口快速传达核心流程，需要细节时深入 references/。避免单个文件过长难以维护。

### P3. 单一 marketplace

**做法**：一个 `marketplace.json` 列出所有 skills，用户一次安装即获得全部。

**优势**：用户体验最简——不需要逐个 skill 安装。新增 skill 时只需在 marketplace.json 加一行。

### P4. Subtree 双向同步

**做法**：各 skill 有独立仓库用于日常迭代，合集仓库通过 `git subtree` 导入，保持双向同步。

**优势**：独立仓库有独立的 CI、测试、版本管理；合集仓库专注 marketplace 管理和多品牌推送。开发者可以选择在独立仓库或合集仓库中工作。

```bash
# 拉取更新
git subtree pull --prefix=skills/github-safe-publish \
  https://github.com/zwyin/github-safe-publish.git master --squash

# 推回独立仓库
git subtree push --prefix=skills/github-safe-publish \
  https://github.com/zwyin/github-safe-publish.git master
```

### P5. 双层版本

**做法**：Skill 版本在各自 SKILL.md frontmatter（随 subtree 同步）；合集版本在 marketplace.json。

**优势**：skill 版本独立迭代，合集版本反映整体发布节奏。release.sh 读取各 skill 版本，合集版本基于最高 skill 版本。

### P6. 多品牌推送

**做法**：一个本地仓库，四个 GitHub remote。sync-all.sh 自动替换 marketplace.json 的 name/description 和 README 版本后推送。

| Remote | 受众 | README |
|--------|------|--------|
| ruyi | 中文用户 | 中文默认 + 英文链接 |
| paoding | 中文用户 | 中文默认 + 英文链接 |
| davinci | 海外用户 | 英文默认 + 中文链接 |
| doraemon | 海外用户 | 英文默认 + 中文链接 |

**优势**：一个代码库，四个入口，各自积累 star。用户从任何一个品牌名找到我们都能用。

### P7. 生成文件隔离

**做法**：平台转换文件（Cursor .mdc、Windsurf .windsurfrules、OpenCode AGENTS.md）输出到 gitignored 的 `dist/`。

**优势**：仓库干净，不污染 git history。用户需要时运行 `make convert` 生成。

### P8. 质量门禁

**做法**：CI 中包含测试数量下限 + 覆盖率门禁 + 结构验证。

**优势**：防止测试被意外删除、覆盖率无声下降、结构漂移。每次变更都有量化保障。

## 开发流程

```
日常迭代 → 独立仓库（github-safe-publish / project-walkthrough-skill）
    ↓ 完成版本
subtree pull → 合集仓库（ruyi-skills）
    ↓ 更新 marketplace / README / CHANGELOG
sync-all.sh → 推送到 4 个 GitHub remote
```

## Makefile 命令

| 命令 | 作用 |
|------|------|
| `make test` | 运行所有 skill 测试 |
| `make ci` | test + 结构验证 + 覆盖率门禁 |
| `make release` | 版本 bump + 同步 + tag + push |
| `make sync` | subtree pull 所有 skill |
| `make convert` | 生成 dist/ 多平台文件 |
| `make clean` | 清理 dist/ |
