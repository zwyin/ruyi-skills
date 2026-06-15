# GitHub Safe Publish

[![version](https://img.shields.io/badge/version-0.7.0-blue)](../skills/ruyi-github-safe-publish/SKILL.md) [![license](https://img.shields.io/badge/license-MIT-green)](../LICENSE) [![tests](https://img.shields.io/badge/tests-235%20passing-brightgreen)](../tests/) [![platform](https://img.shields.io/badge/platform-Claude%20Code-purple)](https://claude.ai/code)

[English](../README.md) · [← 返回 ruyi-skills 合集](https://github.com/zwyin/ruyi-skills#readme)

安全地将本地 Git 项目发布到 GitHub 公开仓库——两层脱敏扫描（135 条确定性规则 + AI 语义分析）、自动修复、备份回滚、端到端发布流程。

一个 [Claude Code](https://claude.ai/code) skill / 插件。

## 为什么需要这个工具

把本地项目推到 GitHub 公开仓库，容易泄露密钥、个人信息、内部基础设施等敏感数据。Gitleaks、TruffleHog 等工具能检测密钥，但不负责修复，也不处理完整的发布流程。

GitHub Safe Publish 用 **确定性规则扫描**（135 条正则，覆盖 6 个维度）加 **AI 语义分析**（补充规则无法覆盖的语义泄露），找到问题后引导你修复、创建仓库、推送——一条命令搞定。

## 竞品对比

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

## 功能特点

### 两层扫描

- **第一层：135 条确定性规则** — 覆盖 6 个维度，结果可复现
- **第二层：AI 语义扫描** — 独立子 agent 执行（隔离敏感信息），1-2 轮收敛
- **Shannon 熵值辅助** — 通用密钥检测（`generic-api-key`）用熵值阈值 4.5 区分真实密钥和占位符

### 6 个扫描维度

| 维度 | 规则数 | 检测内容 |
|------|--------|----------|
| A. 密钥/凭证 | 100 | AWS、Azure、GCP、GitHub、GitLab、OpenAI、Stripe、Slack 等 90+ 服务商 |
| A2. 数据库连接字符串 | 5 | PostgreSQL、MySQL、MongoDB、Redis、JDBC 连接串中的密码 |
| B. 个人身份信息 | 8 | 邮箱、手机号、身份证号、银行卡号、信用卡号 |
| C. 内部基础设施 | 6 | 内网 IP、内部域名、本地文件路径、NAS/VPN 地址 |
| D. 文件黑名单 | 12 | .env、.pem、.key、.db、credentials.* 等不应公开的文件 |
| E. Git 历史 | 4 | commit message 中的敏感信息、已删除文件中的残留 |

完整正则参考见 [docs/scanning-rules.md](scanning-rules.md)。

### 自动修复

发现敏感数据后，提供 4 种处理方式：

- **自动替换** — 密钥替换为 `REPLACE_ME_<类型>`，邮箱替换为 `user@example.com` 等
- **手动修复** — 用户自己在编辑器里改，改完后重新扫描验证
- **删除文件** — 从 git 中移除整个文件
- **确认安全** — 用户确认该内容实际不敏感

### 发布流程

- **备份分支** — 修改前创建 `pre-publish-backup` 分支，可随时回滚
- **仓库创建** — 通过 `gh` CLI 交互式创建，确认可见性/名称/描述
- **SEO 优化**（可选）— GitHub 描述优化、topic 标签、shields.io badge
- **CI 生成**（可选）— 自动检测项目类型，生成 `.github/workflows/test.yml`

## 使用方法

```
/ruyi-github-safe-publish               # 完整流程：扫描 → 修复 → 发布
/ruyi-github-safe-publish --scan-only   # 只做脱敏扫描，输出报告，不修复不发布
/ruyi-github-safe-publish --dry-run     # 扫描 + 展示修复建议，不做任何实际修改
/ruyi-github-safe-publish --seo         # 完整流程 + SEO 优化
/ruyi-github-safe-publish --ci          # 完整流程 + CI 工作流生成
/ruyi-github-safe-publish --seo --ci    # 全部功能
```

### 流程控制

| 步骤 | 完整流程 | --scan-only | --dry-run |
|------|---------|-------------|-----------|
| 1. 前置检查 | 执行 | 执行 | 执行 |
| 2. 创建备份分支 | 执行 | 跳过 | 跳过 |
| 3. 两层脱敏扫描 | 执行 | 执行 | 执行 |
| 4. 自动修复 + 确认 | 执行 | 跳过 | 仅展示建议 |
| 5. 仓库创建 + 推送 | 执行 | 跳过 | 跳过 |
| 6. 验证 + 报告 | 执行 | 扫描报告 | 报告 + 建议 |

## 架构

```
Step 1: 前置检查 + 参数确认（集中交互）
Step 2: 创建备份分支（pre-publish-backup）
Step 3: 两层脱敏扫描
  第一层：135 条确定性正则规则（6 个维度）
  第二层：AI 语义扫描（1-2 轮，独立子 agent）
Step 4: 自动修复 + 用户确认（CRITICAL / WARNING / SAFE）
Step 5: 仓库决策 + 推送（集中交互，通过 gh CLI）
Step 6: 验证 + 输出报告
```

## 关于 135 条规则

你可能会问：Gitleaks 有约 120 条规则，TruffleHog 有 873+ 检测器——为什么我们只有 135？

**不同维度的比较。** TruffleHog 的 873 个检测器是单维度的（仅限 API 密钥），大部分覆盖长尾 SaaS 服务。我们的 135 条规则横跨 **6 个维度**——密钥/凭证（100）、数据库连接字符串（5）、个人身份信息（8）、内部基础设施（6）、文件黑名单（12）、Git 历史（4）。我们与 TruffleHog 在约 50 个主流服务商上有重叠（AWS、Azure、GCP、GitHub、Stripe 等），同时也覆盖了他们不检测的 15 个服务商（npm、DigitalOcean、Cloudflare、Telegram、Discord 等）。

真正的差异不在规则数量——而在检测**之后**发生的事：AI 语义分析捕获正则无法覆盖的语义泄露，自动修复将密钥替换为占位符，端到端流程处理仓库创建和推送。没有其他工具提供这个完整流水线。

## 安装

### 方式 1：Browse UI

选择 **Browse and install plugins** → 选择 **ruyi-skills** → 选择 **Install now**

### 方式 2：Marketplace 安装

```bash
# 1. 添加 marketplace
/plugin marketplace add zwyin/ruyi-skills

# 2. 安装插件
/plugin install ruyi-skills@ruyi-skills
```

### 方式 3：让 Agent 安装

```
Please install ruyi-skills from github.com/zwyin/ruyi-skills
```

### 方式 4：npx 快速安装

```bash
npx skills add zwyin/ruyi-skills
```

### 方式 5：ClawHub

```bash
clawhub install ruyi-skills
```

### 方式 6：手动安装

```bash
git clone https://github.com/zwyin/ruyi-skills.git
claude --plugin-dir ./ruyi-skills
```

或将 `skills/ruyi-github-safe-publish/SKILL.md` 复制到你的项目 skill 目录。

### 其他平台

| 平台 | 安装方式 |
|------|---------|
| **Cursor** | 复制 `dist/cursor/*.mdc` 到项目的 `.cursor/rules/` 目录 |
| **Windsurf** | 复制 `dist/windsurf/.windsurfrules` 到项目的 `.windsurf/rules/` 目录 |
| **OpenCode** | 复制 `dist/opencode/AGENTS.md` 到项目的 `.opencode/skills/` 目录 |

## 测试

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

或使用验证脚本：

```bash
bash scripts/validate_skill.sh
```

### 测试覆盖

| 文件 | 覆盖率 | 说明 |
|------|--------|------|
| test_skill_structure | 100% | SKILL.md 结构验证 |
| test_scanning_rules | 97% | 规则数量守卫、正则有效性 |
| test_detection | 100% | 134/135 规则端到端检测 |
| test_entropy | 100% | Shannon 熵值计算 + 阈值校准 |
| test_convert | 100% | 多平台格式转换验证 |
| test_plugin_metadata | 100% | 插件元数据 + 版本同步（5/6 位置） |
| test_conftest | 100% | 辅助函数边界测试 |
| **总计** | **99%** | **235 个测试** |

## 项目结构

```
ruyi-github-safe-publish/
├── .claude-plugin/          # 插件元数据
├── skills/                  # Skill 定义
│   └── ruyi-github-safe-publish/
│       └── SKILL.md         # 唯一事实源
├── docs/
│   ├── README_zh.md         # 中文文档
│   ├── scanning-rules.md    # 完整正则参考（135 条规则）
│   └── superpowers/specs/   # 设计文档
├── scripts/
│   ├── convert.sh           # 多平台格式转换
│   ├── release.sh           # 版本发布自动化
│   └── validate_skill.sh    # 一键验证
├── tests/                   # 235 个测试
├── CHANGELOG.md
├── CLAUDE.md
└── LICENSE
```

## 许可证

[MIT](../LICENSE)
