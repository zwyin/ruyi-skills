# ruyi-skills 架构设计

## 目录结构

```
ruyi-skills/
├── .claude-plugin/
│   └── marketplace.json            # 合集级 marketplace，列出所有 skills
├── .github/
│   └── workflows/
│       └── test.yml                # CI: skill 测试 + 结构验证 + 合集脚本检查
├── docs/
│   └── architecture-design.md      # 本文档
├── scripts/
│   ├── check_self_contained.py     # 校验 skill 自包含性
│   ├── convert.sh                  # 多平台转换（输出到根 dist/）
│   └── release.sh                  # 版本 bump + tag + push
├── tests/                          # 合集级测试
├── skills/
│   ├── ruyi-github-safe-publish/
│   │   ├── .claude-plugin/         # skill 级 plugin.json + marketplace.json
│   │   ├── .github/workflows/      # skill 级 CI
│   │   ├── SKILL.md                # skill 唯一事实源
│   │   ├── scripts/                # skill 专属脚本
│   │   ├── tests/                  # skill 专属测试
│   │   ├── docs/                   # skill 参考文档
│   │   └── dist/                   # [gitignored] 平台转换输出
│   └── ruyi-project-walkthrough/
│       ├── .claude-plugin/
│       ├── .github/workflows/
│       ├── SKILL.md
│       ├── scripts/
│       ├── tests/
│       ├── docs/
│       ├── cursor/                 # 平台文件（已 git 跟踪）
│       ├── .windsurf/              # 平台文件（已 git 跟踪）
│       └── .opencode/              # 平台文件（已 git 跟踪）
├── dist/                           # [gitignored] convert.sh 输出
├── Makefile
├── README.md
├── README.en.md
├── CHANGELOG.md
├── CLAUDE.md
└── LICENSE
```

## 设计原则

### P1. Skill 自包含

**做法**：SKILL.md 及 references/ 内的所有链接，不得指向 skill 目录外的文件。每个 skill 必须能被独立提取、安装和使用。

**优势**：skill 可以脱离合集独立运行；合集仓库的改动不会破坏单个 skill 的完整性。

**例外**：仓库根 `scripts/` 只放合集级工具（convert.sh、release.sh、check_self_contained.py），不属于任何 skill。

### P2. 渐进展示

**做法**：SKILL.md 控制在 500 行以内，详细规则、配置说明、模板等内容放在 `docs/` 子目录。

**优势**：SKILL.md 作为入口快速传达核心流程，需要细节时深入 docs/。避免单个文件过长难以维护。

### P3. 单一 marketplace

**做法**：一个 `marketplace.json` 列出所有 skills，用户一次安装即获得全部。

**优势**：用户体验最简——不需要逐个 skill 安装。新增 skill 时只需在 marketplace.json 加一行。

### P4. 双层版本

**做法**：Skill 版本在各自 SKILL.md frontmatter；合集版本在 marketplace.json。release.sh 读取合集版本并 bump。

**优势**：skill 版本独立迭代，合集版本反映整体发布节奏。

### P5. 平台文件管理

**做法**：`scripts/convert.sh` 将 SKILL.md 转换为 Cursor (.mdc)、Windsurf (.windsurfrules)、OpenCode (AGENTS.md) 格式。输出到根 `dist/`（gitignored）。

各 skill 目录内的平台文件策略因 skill 而异：
- **ruyi-project-walkthrough**：cursor/、.windsurf/、.opencode/ 文件已 git 跟踪并提交
- **ruyi-github-safe-publish**：平台文件在 dist/ 下，未被 git 跟踪

**优势**：用户从 marketplace 安装后直接可用（project-walkthrough）；convert.sh 可随时重新生成。

### P6. 质量门禁

CI（`.github/workflows/test.yml`）包含 4 个 job：

| Job | 内容 |
|-----|------|
| test-github-safe-publish | 矩阵 ubuntu+macOS, python 3.10+3.12, 覆盖率 95% |
| test-project-walkthrough | ubuntu, python 3.12 |
| structure-check | marketplace.json 校验 + skill 自包含检查 |
| collection-scripts | 合集级测试 + convert.sh --check |

### P7. 品牌分发

ruyi-skills 是唯一开发仓库。通过外部 [brand-sync-tool](https://github.com/zwyin/brand-sync-tool) 自动生成各品牌仓库（paoding / davinci / doraemon）。

brand-sync-tool 负责：
- 克隆远程品牌仓库（增量）或创建新仓库
- rsync 复制文件并执行品牌替换（SKILL.md name、目录名、marketplace.json、README、CI 路径、测试文件、平台输出文件等）
- 提交并推送到 GitHub

详见 brand-sync-tool 仓库的 README。

### P8. 已归档仓库

`github-safe-publish` 和 `project-walkthrough-skill` 两个独立仓库已 archived。所有代码维护统一在 ruyi-skills 仓库中进行。

## 开发流程

```
修改代码/文档（在 ruyi-skills 仓库中）
    ↓
make test && make check            # 运行测试 + 结构验证
    ↓
make convert                       # 重新生成平台文件（如需）
    ↓
git commit && git push             # 提交推送到 ruyi-skills
    ↓
cd brand-sync-tool && bash sync.sh # 分发到品牌仓库
```

## Makefile 命令

| 命令 | 作用 |
|------|------|
| `make test` | 运行所有 skill 测试 |
| `make ci` | test + check + test-collection |
| `make check` | marketplace.json 校验 + skill 自包含检查 |
| `make convert` | 生成 dist/ 多平台文件 |
| `make release` | 版本 bump + tag + push（传参：`make release ARGS=patch`） |
| `make clean` | 清理 dist/ |
