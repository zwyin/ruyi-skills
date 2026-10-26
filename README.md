# ruyi-skills

[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![platform](https://img.shields.io/badge/platform-Claude%20Code-purple)](https://claude.ai/code)

Claude Code skill 合集——化繁为简，如意随心。把复杂的耗时任务变成一条命令。

[English](README.en.md) | 中文

> 如意（Ruyi）：中国传统文化中的吉祥物，意为「如你心意」。这个合集里的每个 skill 都是为了让你心想事成——复杂的事，交给工具。

## Install Skills

### 快捷安装（推荐）

```bash
git clone https://github.com/zwyin/ruyi-skills.git
cd ruyi-skills && bash scripts/install.sh
```

`install.sh` 自动检测本机 agent（存在 `~/.claude` → Claude Code，存在 `~/.codex` → Codex CLI），把全部 skills 复制到对应技能目录，幂等可重跑。常用参数：`--agent claude|codex`、`--skill <name>`、`--list`、`--uninstall`。

### 安装矩阵（多 Agent）

| Agent | 安装 | 验证方法 |
|-------|------|----------|
| Claude Code（GLM 等 Anthropic 兼容端点用户同路径） | 上方快捷安装默认装入 `~/.claude/skills/<name>/`；或用下方 Plugin 方式 | `ls ~/.claude/skills/`，新开会话调用技能命令 |
| Codex CLI | 上方快捷安装自动装入 `~/.codex/skills/<name>/`（可 `--agent codex` 强制）；项目级：`bash scripts/convert.sh --all` 后把 `dist/codex/<name>/` 复制到 `<repo>/.agents/skills/`（SKILL.md 原生识别，无需改格式） | `codex debug prompt-input "hi" 2>/dev/null \| grep <name>`（免登录，见 [docs/portability/codex.md](docs/portability/codex.md)） |
| Cursor（社区路径，未实测加载） | `bash scripts/convert.sh --all` 后复制 `dist/cursor/.cursor/rules/` 到 `~/.cursor/rules/` | 重启 Cursor，Settings → Rules 出现对应条目 |
| Windsurf（社区路径，未实测加载） | `bash scripts/convert.sh --all` 后把 `dist/windsurf/.windsurfrules/` 中文件并入项目根 `.windsurfrules`（或全局 rules） | Windsurf 中 Rules 生效提示 |
| OpenCode（社区路径，未实测加载） | `bash scripts/convert.sh --all` 后复制 `dist/opencode/.opencode/skills/` 到项目 `.opencode/skills/` | `opencode` 启动后技能列表可见 |

> Codex 行的路径与验证命令以官方文档 + 二进制实测为准（`docs/portability/codex.md`）；Cursor / Windsurf / OpenCode 三行为社区通用做法，本合集未实测加载。

### Plugin 方式（Claude Code）

**Via Browse UI**

Select **Browse and install plugins** → Select **ruyi-skills** → Select **Install now**

**Direct Install**

```bash
# 1. Add marketplace
/plugin marketplace add zwyin/ruyi-skills

# 2. Install the plugin
/plugin install ruyi-skills@ruyi-skills

# 3. Reload plugins
/reload-plugins
```

**Ask the Agent**

Simply tell the Agent:

```
Please install Skills from github.com/zwyin/ruyi-skills
```

**Quick Install (npx)**

```bash
npx skills add zwyin/ruyi-skills
```

**ClawHub (coming soon)**

> Not yet published to ClawHub registry. Track progress at [github.com/zwyin/ruyi-skills](https://github.com/zwyin/ruyi-skills).

```bash
clawhub install ruyi-github-safe-publish
clawhub install ruyi-project-walkthrough
```

**Manual Install**

```bash
git clone https://github.com/zwyin/ruyi-skills.git
claude --plugin-dir ./ruyi-skills
```

---

## Skills

### ruyi-github-safe-publish

安全发布到 GitHub——两层脱敏扫描（135 条规则 + AI）、自动修复、备份回滚、端到端发布。

[![version](https://img.shields.io/badge/version-0.7.1-blue)](skills/ruyi-github-safe-publish/skills/ruyi-github-safe-publish/SKILL.md)

**扫描覆盖 6 大维度**：密钥凭证（100 rules）、数据库连接（5 rules）、个人隐私（8 rules）、内部基础设施（6 rules）、文件黑名单（12 rules）、Git 历史（4 rules）。

**竞品对比**：

| 特性 | GitHub Safe Publish | Gitleaks | TruffleHog | git-secrets |
|------|:-:|:-:|:-:|:-:|
| 价格 | **免费 / 开源** | 免费 | 免费 | 免费 |
| 检测方式 | 规则 + AI 两层 | 仅规则 | 仅规则 | 仅规则 |
| 规则数量 | **135 条** | ~120 条 | 800+ 检测器 | ~20 条 |
| 自动修复 | **支持** | 不支持 | 不支持 | 不支持 |
| 发布流程 | **端到端** | 无 | 无 | 无 |
| 备份回滚 | **支持** | 无 | 无 | 无 |
| PII 检测 | **支持（邮箱/手机/身份证）** | 不支持 | 不支持 | 不支持 |
| 内部基础设施 | **支持（内网IP/域名/路径）** | 不支持 | 不支持 | 不支持 |
| AI 语义分析 | **支持** | 不支持 | 不支持 | 不支持 |
| 文件黑名单 | **支持（.env/.pem/.key 等）** | 不支持 | 部分 | 不支持 |
| Git 历史扫描 | **支持** | 支持 | 支持 | 不支持 |
| 平台 | Claude Code | CLI | CLI | CLI |
| SEO 优化 | **支持** | 无 | 无 | 无 |
| CI 生成 | **支持** | 无 | 无 | 无 |

> **定位差异**：Gitleaks/TruffleHog 是纯粹的密钥检测工具，适合 CI 集成。GitHub Safe Publish 是端到端的发布助手——扫描、修复、创建仓库、推送一站完成，AI 补充规则无法覆盖的语义泄露。

```bash
# 完整流程：脱敏扫描 → 修复 → 发布到 GitHub
/ruyi-github-safe-publish

# 核心 + SEO 优化（描述、Topics、Badges）
/ruyi-github-safe-publish --seo

# 核心 + CI 生成（自动检测项目类型，生成 .github/workflows/test.yml）
/ruyi-github-safe-publish --ci

# 全部：核心 + SEO + CI
/ruyi-github-safe-publish --seo --ci

# 只做脱敏扫描，输出报告，不修复不发布
/ruyi-github-safe-publish --scan

# 模拟运行：扫描 + 修复建议，但不做任何实际修改
/ruyi-github-safe-publish --dry-run
```

| 参数 | 说明 | 互斥规则 |
|------|------|----------|
| (无参数) | 核心流程：脱敏 + 发布 | — |
| `--seo` | 附加 SEO 优化（描述、Topics、Badges、README 优化） | 不可与 `--scan` / `--dry-run` 组合 |
| `--ci` | 附加 CI 生成（自动检测项目类型并生成 workflow） | 不可与 `--scan` / `--dry-run` 组合 |
| `--scan` | 只扫描输出报告，不修复不发布 | 不可与 `--seo` / `--ci` / `--dry-run` 组合 |
| `--dry-run` | 模拟运行：扫描 + 修复建议，但不执行 | 不可与 `--seo` / `--ci` / `--scan` 组合 |

[→ 查看完整文档](skills/ruyi-github-safe-publish/docs/README_zh.md)

---

### ruyi-project-walkthrough

项目技术走读——多深度、多受众、多语言，输出 markdown + 交互式 HTML。

[![version](https://img.shields.io/badge/version-1.6.6-blue)](skills/ruyi-project-walkthrough/skills/ruyi-project-walkthrough/SKILL.md)

```bash
# 自动分析当前目录，推荐深度
/ruyi-project-walkthrough

# 指定项目路径
/ruyi-project-walkthrough /path/to/project

# 快速概览（适合小项目或初次了解）
/ruyi-project-walkthrough --depth brief

# 深度走读（适合需要全面了解的项目）
/ruyi-project-walkthrough --depth deep

# 全量走读（包含所有细节，适合大型项目）
/ruyi-project-walkthrough --depth all

# 面向开发者受众
/ruyi-project-walkthrough --audience dev

# 纯中文输出（无英文混排）
/ruyi-project-walkthrough --lang zh-pure

# 双语输出（中英对照）
/ruyi-project-walkthrough --lang bilingual

# 跳过确认，使用推荐默认值（适合自动化流程）
/ruyi-project-walkthrough --no-confirm

# 组合使用：深度走读 + 开发者受众 + 中文输出
/ruyi-project-walkthrough --depth deep --audience dev --lang zh

# 查看版本号
/ruyi-project-walkthrough --version
```

| 参数 | 说明 | 可选值 | 默认 |
|------|------|--------|------|
| `path` | 项目路径 | 任意目录路径 | 当前目录 |
| `--depth` | 走读深度 | `brief` / `medium` / `deep` / `all` | 自动推荐 |
| `--audience` | 目标受众 | `general` / `dev` | `general` |
| `--lang` | 输出语言 | `zh` / `zh-pure` / `en` / `bilingual` | `zh` |
| `--no-confirm` | 跳过确认 | (flag, 无值) | — |
| `--version` | 打印版本号 | (flag, 无值) | — |

[→ 查看完整文档](skills/ruyi-project-walkthrough/README.md)

### ruyi-version-check

版本一致性检查器——发版前体检，核对合集里每一处版本号（frontmatter / manifest / Phase 0 banner / badge / CHANGELOG / dist）是否一致。开发维护工具，非面向终端用户的功能 skill。

[![version](https://img.shields.io/badge/version-0.1.2-blue)](skills/ruyi-version-check/skills/ruyi-version-check/SKILL.md)

```bash
python3 skills/ruyi-version-check/scripts/validate_versions.py --root .
```

---

## Version & Update

### Check Installed Version

Look for the `version` field in the SKILL.md frontmatter:

```bash
# macOS / Linux
cat ~/.claude/plugins/cache/ruyi-skills/*/skills/*/skills/*/SKILL.md | grep version
```

Or ask Claude directly:

```
我安装的 ruyi-skills 是什么版本？
```

### Update to Latest Version

Re-install to get the latest version:

```bash
/plugin install ruyi-skills@ruyi-skills
/reload-plugins
```

Or via npx:

```bash
npx skills add zwyin/ruyi-skills
```

---

## License

[MIT](LICENSE)
