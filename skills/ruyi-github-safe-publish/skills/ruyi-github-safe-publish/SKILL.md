---
name: ruyi-github-safe-publish
version: "0.7.0"
description: |
  将本地 Git 项目安全地发布到 GitHub 公开仓库。包含两层脱敏扫描
  （确定性规则 + AI 语义）、自动修复、备份回滚、仓库创建、SEO 优化。
  Use when: "push to github", "publish to github", "开源", "推送到 GitHub",
  "create github repo", "发布到 github"。
argument-hint: "[--scan] [--dry-run] [--seo] [--ci]"
triggers:
  - push to github
  - publish to github
  - create github repo
  - 开源发布
  - 推送到 GitHub
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Agent
---

# GitHub Safe Publish

将本地 Git 项目安全地发布到 GitHub 公开仓库。

## 参数

```
/ruyi-github-safe-publish                    # 核心流程（脱敏+发布）
/ruyi-github-safe-publish --seo              # 核心 + SEO 优化
/ruyi-github-safe-publish --ci               # 核心 + CI 生成
/ruyi-github-safe-publish --seo --ci         # 全部
/ruyi-github-safe-publish --scan        # 只做脱敏扫描，输出报告，不修复不发布
/ruyi-github-safe-publish --dry-run          # 模拟完整流程：扫描+模拟修复建议，但不做任何实际修改
```

**参数互斥与冲突处理**：
- `--scan` 和 `--dry-run` 不能与 `--seo` / `--ci` 组合（SEO 和 CI 只对已推送的仓库有意义，扫描模式不推送）
- `--scan` 和 `--dry-run` 不能同时使用
- `--seo` 和 `--ci` 可以同时使用（完整功能模式）
- 无效组合直接报错并退出
- **`--scan` 与 `--dry-run` 的区别**：
  - `--scan`：**只告诉你有什么问题**。输出扫描报告（命中规则、文件位置、严重等级），不提修复方案。
  - `--dry-run`：**告诉你有什么问题 + 打算怎么修**。在扫描报告基础上，为每个发现项展示推荐修复方案（如"将此密钥替换为 `REPLACE_ME_AWS`"），但不执行任何修改。

**流程控制矩阵**：

| 步骤 | 完整流程 | --scan | --dry-run |
|------|---------|--------|-----------|
| Step 1: 前置检查+参数确认 | 执行 | 执行 | 执行 |
| Step 2: 创建备份分支 | 执行 | 跳过 | 跳过 |
| Step 3: 脱敏扫描 | 执行 | 执行 | 执行 |
| Step 4: 自动修复+用户确认 | 执行 | 跳过 | 输出修复建议但不执行 |
| Step 5: 仓库决策+推送 | （迭代 2） | 跳过 | 跳过 |
| Step 6: 验证+报告 | （迭代 2） | 仅扫描报告 | 仅扫描报告+修复建议 |

## 前提

- 当前目录是 Git 仓库，至少有一个 commit
- `gh` CLI 已安装并登录（可选，支持手动推送）
- 用户确认项目可以公开（已过脱敏）

## Step 1: 前置检查 + 参数确认（集中交互 #1）

所有前置检查和参数决策集中在一次交互中完成。任何一项阻断条件不满足则停在当前步骤。

### 1.1 自动检查（无交互）

按顺序执行以下检查，仅记录结果，不做交互：

```
检查项：

1. 当前目录是 git 仓库？
   命令：git rev-parse --is-inside-work-tree
   ├── 成功 → is_git_repo = true，继续
   └── 失败 → is_git_repo = false，标记"需要在 1.2 中询问初始化"

2. git 仓库至少有 1 个 commit？
   命令：git rev-parse HEAD
   ├── 成功 → has_commit = true，继续
   └── 失败 → 阻断：输出"仓库没有任何 commit，需要至少一次 commit 才能创建备份分支和回滚"，停止流程

3. gh CLI 是否可用？
   命令：gh auth status 2>&1
   ├── 成功 → gh_available = true，提取用户名（gh api user --jq .login）
   └── 失败 → gh_available = false，记录原因（未安装 / 未登录）
   注意：gh CLI 可用不是必须条件，用户可以选择手动推送
```

自动检查结果汇总格式：
```
前置检查结果：
  Git 仓库：✓
  至少 1 个 commit：✓（42 commits on master）
  gh CLI：✓（已登录 as zwyin）
  或
  gh CLI：✗（未安装。可选：手动推送模式）
```

**参数冲突校验**（在进入任何交互前先执行，冲突直接报错退出）：

```
无效组合检测：
  --scan + --seo  → 报错："--scan 不能与 --seo 组合。SEO 优化只对已推送的仓库有意义，扫描模式不推送。请使用完整流程模式。"
  --scan + --ci   → 报错："--scan 不能与 --ci 组合。CI 生成只对已推送的仓库有意义，扫描模式不推送。请使用完整流程模式。"
  --dry-run + --seo    → 报错："--dry-run 不能与 --seo 组合。SEO 优化需要实际推送，模拟模式不做推送。请使用完整流程模式。"
  --dry-run + --ci     → 报错："--dry-run 不能与 --ci 组合。CI 生成需要实际推送，模拟模式不做推送。请使用完整流程模式。"
  --scan + --dry-run → 报错："--scan 和 --dry-run 不能同时使用。--scan 只输出扫描报告；--dry-run 在报告基础上还展示推荐修复方案。"
```

### 1.2 集中交互确认

将以下决策合并为一次或连续的 AskUserQuestion 调用。问题数量根据上下文动态调整（最多 3 个问题）。

**问题 1：工作模式**（必问）

```
AskUserQuestion: 请确认工作模式

  A) 完整流程：脱敏扫描 → 自动修复 → 发布到 GitHub
     （适合准备公开发布的项目）
  B) 仅扫描：只做脱敏检查，输出扫描报告，不修复不发布（--scan）
     （适合先了解项目中哪些内容需要处理）
  C) 模拟运行：扫描出报告，展示推荐修复方案，但不做任何实际修改（--dry-run）
     （适合预览完整流程，确认修复策略）
```

如果用户在问题 1 选择了完整流程（选项 A），且调用时带了 `--seo` 或 `--ci` 参数，追加确认：

```
AskUserQuestion: 附加模块确认

  检测到参数：--seo --ci

  A) 完整流程 + SEO 优化（README 优化、topics、badges）
  B) 完整流程 + CI 生成（自动检测并生成 .github/workflows/test.yml）
  C) 完整流程 + SEO + CI（全部功能）
  D) 仅完整流程，不加附加模块
```

**问题 2：推送方式**（仅完整流程模式下显示）

情况 A — gh CLI 可用：
```
AskUserQuestion: 推送方式

  A) 使用 gh CLI 自动创建仓库并推送（推荐）
     自动完成：创建仓库 → 添加 remote → git push
  B) 我自己手动推送，只帮我做好脱敏和本地准备
     完成脱敏后输出手动推送指引，不执行任何推送操作
```

情况 B — gh CLI 不可用：
```
AskUserQuestion: 推送方式（gh CLI 不可用：未安装/未登录）

  A) 我自己手动推送
     完成脱敏后输出手动推送指引
  B) 我先去安装/登录 gh CLI，等会再来
     中止当前流程，提示安装命令：
       macOS: brew install gh && gh auth login
       Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
```

**问题 3：非 git 目录的处理**（仅在 is_git_repo = false 时显示）

```
AskUserQuestion: 当前目录不是 Git 仓库

  A) 帮我初始化后继续
     执行：git init → 生成标准 .gitignore（覆盖 Python/Node/macOS/IDE 常见忽略项）→ git add . → git commit -m "init: initial commit"
  B) 我先自己备份和初始化，回来再用
     中止当前流程，提示用户准备好后重新调用
```

标准 .gitignore 模板（选项 A 时生成）：
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
*.egg

# Node
node_modules/

# macOS
.DS_Store
.AppleDouble
.LSOverride

# IDE
.vscode/
.idea/
*.swp
*.swo

# 环境变量和密钥
.env
.env.*
!.env.example
*.pem
*.key

# 数据库
*.db
*.sqlite
*.sqlite3
```

### 1.3 交互结果汇总

所有问题确认完成后，输出配置摘要：

```
━━━ 配置确认 ━━━
工作模式：完整流程
推送方式：gh CLI 自动推送（zwyin）
附加模块：SEO + CI
───────────────
目标仓库：待扫描后确认（Step 5）
备份分支：pre-publish-backup（Step 2 创建）
报告文件：safe-publish-report-YYYYMMDD-HHMM.md（项目根目录）
━━━━━━━━━━━━━━━

⚠️ 报告文件包含扫描到的敏感信息摘要，请勿提交到公开仓库。
   建议扫描完成后删除，或确认 .gitignore 已包含 safe-publish-report-*.md。

确认以上配置，开始执行？
```

用户确认后进入 Step 2。用户否定则回到 1.2 重新选择。

## Step 2: 创建备份分支

在任何修改之前创建回滚点。**仅在完整流程模式下执行**（`--scan` 和 `--dry-run` 跳过此步骤）。

跳过原因：`--scan` 和 `--dry-run` 设计为纯只读操作，不修改任何源文件或分支，子 agent 不被授予写入工具权限，因此无需备份。唯一例外：Step 6.3 的报告文件写入（输出到项目根目录）和 `.gitignore` 追加，不涉及源代码变更。

### 2.1 创建流程

```bash
# 删除已有的同名备份分支（重新运行会覆盖上次备份，这是预期行为）
git branch -D pre-publish-backup 2>/dev/null || true

# 检查工作区是否有未提交内容
if git diff --quiet HEAD && git diff --quiet --cached; then
    # 工作区干净，直接在 HEAD 上创建备份分支
    git branch pre-publish-backup HEAD
else
    # 有未提交内容，先 stash 再创建分支
    git stash push -m "pre-publish-stash-$(date +%Y%m%d%H%M%S)" --include-untracked
    git branch pre-publish-backup HEAD
    # 恢复工作区
    git stash pop || {
        echo "WARNING: stash pop 产生冲突，无法自动恢复工作区。"
        echo "冲突文件已保留在 stash 中（git stash list 查看）。"
        echo ""
        echo "备份分支 pre-publish-backup 已基于 HEAD 创建（不含未提交内容）。"
        echo "请手动处理冲突："
        echo "  1. 解决冲突文件后 git add . && git stash drop"
        echo "  2. 或放弃未提交改动：git checkout -- . && git stash drop"
        echo ""
        echo "处理完毕后继续后续步骤。"
        # 不自动丢弃 stash，等待用户手动处理
        return 1
    }
fi
```

### 2.2 验证

```bash
# 确认备份分支存在且指向正确的 commit
git rev-parse --verify pre-publish-backup
echo "备份分支 pre-publish-backup 指向: $(git log -1 --oneline pre-publish-backup)"
```

### 2.3 规则

- **分支名固定**：`pre-publish-backup`，不可自定义
- **删除后重建**：如果该分支已存在（上次运行的残留），先删除再创建
- **不推送**：备份分支仅存在于本地，不推送到任何远程仓库
- **覆盖提醒**：重新运行会覆盖上次的备份点。备份的是"最近一次发布前的状态"，非累积
- **回滚方式**：`git reset --hard pre-publish-backup`（硬回滚到备份点的完整状态）
- **清理时机**：推送完成并验证后（Step 6），告知用户可以安全删除该分支

### 2.4 输出

```
备份分支已创建：pre-publish-backup → <commit-hash> <commit-message>
如需回滚：git reset --hard pre-publish-backup
```

## Step 3: 脱敏扫描（两层架构）

采用两层架构：第 1 层确定性规则扫描覆盖已知模式，第 2 层 AI 语义扫描补充规则无法覆盖的语义泄露。
两层独立运行，结果合并后输出统一报告。

### 第 1 层：确定性规则扫描

**扫描范围**：

```bash
# 获取所有 git 跟踪文件
git ls-files

# 排除规则：
# 1. 二进制文件（图片/视频/编译输出/字体）— 无法以 UTF-8 解码的文件跳过
# 2. .git 目录内部
# 3. 子模块（由用户自行处理）
# 4. 单文件 > 10MB 跳过（避免性能问题）

# 可选警告：检查 .gitignore 中列出但仍存在于工作区的敏感文件
git ls-files --others --ignored --exclude-standard | grep -iE '\.env$|\.pem$|\.key$|\.db$|credentials'
```

**六个扫描维度**：

| 维度 | 代号 | 说明 | 规则数 |
|------|------|------|--------|
| A. 密钥/凭证 | KEY | API Key、Token、Secret 等确定性模式 + 熵值辅助 | 100 |
| A2. 数据库连接字符串 | DB | 含密码的数据库连接字符串 | 5 |
| B. PII（个人身份信息） | PII | 邮箱、手机号、身份证号、银行卡号等 | 8 |
| C. 内部基础设施 | INF | 内网 IP、内部域名、本地文件路径、VPN 配置 | 6 |
| D. 文件黑名单 | FILE | .env、.pem、.key、.db 等不应公开的文件类型 | 12 |
| E. Git 历史 | GIT | 历史中的敏感文件残留、大文件、author email 泄露 | 4 |

> 完整正则定义见 `docs/scanning-rules.md`。以下为各维度概要。

**A. 密钥/凭证（正则 + 熵值）**

覆盖 100 条规则，主要服务商包括：

- 云服务：AWS（access token / secret key / Bedrock）、Azure（AD client secret）、GCP（API key / Service Account）、DigitalOcean、Cloudflare（API / Global / Origin CA）
- 代码平台：GitHub（PAT / App Token / Fine-grained PAT / OAuth / Refresh Token）、GitLab（PAT / Deploy / Runner / CI Job / Feed / K8s Agent）、Bitbucket（Client ID / Secret）
- AI 服务：OpenAI、Anthropic、HuggingFace、Cohere、Perplexity、Google Gemini、DeepSeek、xAI、Replicate
- 通信：Slack（Bot / User / Webhook）、Twilio、SendGrid、Telegram、Discord、Sendinblue、Mattermost、MS Teams
- 支付：Stripe、Square、Plaid、Flutterwave、Shopify（Access / Shared Secret）
- 运维：Datadog、Sentry（Access / DSN）、New Relic、Grafana、Snyk、Databricks、Dynatrace、Pulumi、Artifactory、HashiCorp（Terraform / Vault）
- 部署平台：Vercel、Netlify、Supabase、Fly.io、Deno、PlanetScale
- 其他：npm、PyPI、RubyGems、Heroku、Postman、Notion、Atlassian（Jira/Confluence）、Linear、Mailchimp、Okta、Mailgun、Algolia、Facebook、Dropbox、Confluent、Fastly、LaunchDarkly、Codecov、Doppler、ClickHouse、Contentful、Scaleway、ngrok

熵值检测（Shannon entropy）：阈值 4.5，仅在已知密钥关键字附近触发，不全局扫描所有字符串以避免 Base64/哈希值误报。`generic-api-key` 规则匹配后，熵值 >= 4.5 升级为 CRITICAL，< 4.5 降为 WARNING。

**A2. 数据库连接字符串（正则）**

覆盖 5 条规则：PostgreSQL、MySQL、MongoDB、Redis、JDBC 通用格式。检测连接字符串中嵌入的密码。本地开发连接（localhost + 无密码）降为 WARNING。

**B. PII（正则）**

- 邮箱：非 GitHub noreply / placeholder 的个人邮箱
- 中国大陆手机号：`1[3-9]\d{9}`
- 身份证号：18 位格式（CRITICAL）
- 银行卡号：中国银行卡号前缀（CRITICAL）
- 美国社保号 SSN（CRITICAL）
- 信用卡号：含 Luhn 校验（CRITICAL）
- IPv4 地址：公网 IP 检测（内网 IP 由 C 维度的 internal-ip-address 覆盖）（WARNING）
- 硬编码密码：password/passwd/pwd 赋值语句（WARNING）

**C. 内部基础设施（正则）**

- 内网 IP：`10.x.x.x`、`172.16-31.x.x`、`192.168.x.x`
- 内部域名：`.local`、`.internal`、`.lan`、`.corp`、`.intra`、`.office`、`.home`、`.nas` 后缀
- 硬编码本地路径：`/Users/xxx/`、`C:\Users\xxx\`、`/home/xxx/`
- 内部服务 URL：含 nas/vpn/internal 关键字的 URL
- VPN/Proxy 配置

**D. 文件黑名单**

按文件路径匹配，包含：
- 凭证文件：`.env`、`.pem`、`.key`、`.p12`、`.pfx`、`.jks`、credentials.*、`.netrc`、`.pypirc`
- 数据文件：`.sql`、`.db`、`.sqlite`、`.dump`
- IDE 配置：`.idea/`、`.vscode/settings.json`
- 系统文件：`.DS_Store`、`Thumbs.db`
- 日志/缓存：`.log`、`__pycache__/`、`node_modules/`
- Terraform 状态：`.tfstate`

同时检查 `.gitignore` 充分性：对黑名单中的文件类型检查是否有对应忽略规则。

**E. Git 历史扫描**

- Author email 泄露：`git log --all --format='%ae' | sort -u`，排除 GitHub noreply 地址
- 历史中添加过的敏感文件：`git log --all --diff-filter=A --summary` 搜索 `.env`、`.pem`、`.key` 等
- 已删除的敏感文件残留：`git log --all --diff-filter=D --summary`，内容仍可通过 git 历史恢复
- 大文件：`git rev-list --objects --all | git cat-file --batch-check` 筛选 > 1MB 的 blob

**规则扫描执行命令**：

```bash
# 获取扫描文件列表（排除常见二进制扩展名）
files=$(git ls-files | grep -v -E '\.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|mp4|mp3|zip|tar|gz|exe|dll|so|dylib|pdf)$')

# 对每个文件逐行应用规则扫描（伪代码，实际由 agent 读取文件内容后用正则匹配）
for file in $files; do
  # 检查文件大小
  size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
  if [ "$size" -gt 10485760 ]; then
    echo "SKIP: $file (> 10MB)"
    continue
  fi
  # 应用维度 A-D 的规则扫描
done

# Git 历史扫描（维度 E）
git log --all --format='%ae' | sort -u
git log --all --diff-filter=A --summary
git log --all --diff-filter=D --summary
```

**输出格式**：

结构化报告，每项包含：

```
[维度] 文件:行号 | 严重级别 | 规则名 | 匹配内容（脱敏显示）
示例：
[KEY] src/config.py:42 | CRITICAL | github-pat | ghp_****************************
[PII] README.md:15 | WARNING | email-address | zhang***@company.com
[INF] deploy.sh:8 | WARNING | internal-ip-address | 192.168.1.***
[FILE] .env | CRITICAL | env-files | .env 文件存在
[GIT] (历史) | WARNING | author-email-leak | zhangwei@internal.corp
```

### 第 2 层：AI 语义扫描（1-2 轮，独立子 agent 执行）

通过独立子 agent 执行（不共享主对话上下文，隔离敏感信息），补充规则无法覆盖的语义泄露。

**扫描内容**（规则扫描无法覆盖的语义维度）：

- 业务数据泄露：内部项目代号、真实用户数据、订单号、财务数据
- 可溯源叙事：可通过搜索引擎定位到个人/组织的描述（如"在 XX 公司的 YY 项目中"）
- 间接推断：文件路径推断内部组织结构、时间戳推断工作节奏、注释推断技术栈
- 规则扫描误报排除：对第 1 层 WARNING 项进行二次判断，降低误报率

**执行方式**：

使用 `Agent` 工具启动独立子 agent，每个子 agent 接收自包含的扫描 prompt（不依赖主对话上下文）。子 agent 仅被授予 `Read`、`Grep`、`Glob`、`Bash`（只读命令）权限，不可修改任何文件。

**子 agent Prompt 模板**：

```
你是一个代码安全审计 agent。你的任务是扫描一个即将公开的 Git 项目，
找出可能泄露敏感信息的语义内容。这是纯只读任务，不要修改任何文件。

=== 项目路径 ===
{PROJECT_PATH}

=== 你的任务 ===

1. 用 Glob 和 Read 工具浏览项目文件结构
2. 重点阅读以下文件类型：
   - README、CHANGELOG、CONTRIBUTING 等文档
   - 配置文件（YAML/TOML/JSON/INI）
   - 注释密集的源代码文件
   - Git commit message（运行 git log --oneline -50）
3. 识别以下类别的语义泄露：
   A. 内部项目代号或内部系统名称
   B. 真实用户数据（姓名、订单号、交易记录）
   C. 可溯源叙事（能通过搜索引擎定位到具体个人/组织的描述）
   D. 文件路径中暴露的内部组织结构
   E. 注释中的内部链接、内部同事姓名
   F. 时间模式暴露的工作节奏信息

=== 输出格式 ===

每项发现一行，格式：
[FINDING] 类别 | 文件:行号 | 严重级别(CRITICAL/WARNING) | 内容摘要 | 推荐处理方式

=== 已知排除项（第 1 层已覆盖，你不需要重复检查）===
- API Key / Token / Secret 的格式化模式
- 邮箱 / 手机号 / 身份证号等 PII 的标准格式
- .env / .pem 等文件黑名单
- 内网 IP / 内部域名等基础设施模式

=== 注意 ===
- 只报告你确信有泄露风险的内容，宁可漏报不要误报
- 如果某个内容你觉得可能是敏感的但不确定，标为 WARNING
- 如果没有发现任何问题，输出：[CLEAN] 未发现语义层面的敏感信息泄露
```

**收敛判定**：

- 第 1 轮扫描后，将发现项与第 1 层结果合并去重
- 如果第 1 轮发现新问题，启动第 2 轮（使用不同的子 agent 实例，聚焦第 1 轮发现项的关联区域）
- 第 2 轮无新发现，或已完成 2 轮，停止扫描
- 最多 2 轮 AI 扫描

**v1 → v2 架构变更说明**：

v1 采用 5 轮纯 AI 自由扫描，存在两个问题：(1) 每轮 AI 扫描结果不可复现；(2) 规则可覆盖的模式（如 API Key 格式）不应由 AI 判断。v2 改为"规则确定性扫描 + 1-2 轮 AI 语义补充"两层架构，规则层可复现且覆盖率高（100 条密钥规则 + 5 条数据库连接字符串 + 8 条 PII 规则），AI 只负责规则无法覆盖的语义部分，因此收敛更快，最多 2 轮即可。

**两层结果合并**：

```
扫描完成。合并第 1 层 + 第 2 层结果：

第 1 层（规则扫描）：
  CRITICAL: N 项
  WARNING:  M 项

第 2 层（AI 语义扫描）：
  新增 CRITICAL: X 项
  新增 WARNING:  Y 项
  误报排除（WARNING → SAFE）: Z 项

合并后总计：
  CRITICAL: N+X 项
  WARNING:  M+Y-Z 项

详细报告见上方输出。
准备进入 Step 4 处理。
```

## Step 4: 自动修复 + 用户确认

根据 Step 3 扫描结果分类处理。`--scan` 模式跳过此步骤；`--dry-run` 模式输出修复建议但不执行任何修改。

### 结果分类

| 级别 | 含义 | 默认动作 |
|------|------|----------|
| **CRITICAL** | 真实密钥、凭证、敏感 PII（身份证、银行卡） | 必须处理，阻塞推送 |
| **WARNING** | 可能敏感但不确定（内部 IP、个人邮箱、硬编码路径） | 列出给用户判断 |
| **SAFE** | 示例占位符（`your_xxx`、`REPLACE_ME`）、README 通用描述、`example.com` | 无需处理 |

SAFE 项自动跳过，不进入修复流程。

### CRITICAL 修复选项

对每个 CRITICAL 项，使用 `AskUserQuestion` 逐项询问用户：

```
AskUserQuestion: 发现 CRITICAL 敏感内容

  [KEY] src/config.py:42 | github-pat | ghp_****************************

  修复方式：
  A) 自动替换 — 将敏感内容替换为泛化占位符
  B) 手动修复 — 你自己在编辑器里改，改完后我会重新扫描验证
  C) 删除文件 — 从 git 中移除整个文件（git rm）
  D) 确认安全 — 确认该内容实际不敏感（需输入理由）
```

用户选择处理方式后，执行对应操作。

### 自动替换规则

用户选择 A（自动替换）时，按以下规则替换：

| 原始内容类型 | 替换为 | 示例 |
|-------------|--------|------|
| 真实密钥/Token | `REPLACE_ME_<类型>` | `REPLACE_ME_API_KEY`、`REPLACE_ME_GITHUB_TOKEN` |
| 个人邮箱 | `user@example.com` | 或用户指定的 GitHub 公开邮箱 |
| 内部 IP | `192.168.x.x` | 保持格式一致性 |
| 内部域名 | `internal.example.com` | — |
| 真实姓名 | `FIRST_NAME` / `LAST_NAME` | — |
| 手机号 | `1XX-XXXX-XXXX` | — |
| 可溯源叙事 | 泛化为通用描述 | "在 XX 公司的 YY 项目中" → "在某个项目中" |
| 本地文件路径 | 泛化路径 | `/Users/zhangsan/project` → `/path/to/project` |

替换后自动使用 `Edit` 工具修改文件内容。

### WARNING 修复选项

对 WARNING 项，批量展示后由用户统一决策：

```
AskUserQuestion: 发现 WARNING 级别内容

  以下 N 项内容可能敏感，请选择处理方式：

  1. [INF] deploy.sh:8 | internal-ip-address | 192.168.1.100
  2. [PII] README.md:15 | email-address | dev@company.com
  3. ...

  对每一项：
  A) 按自动替换规则处理（同 CRITICAL 选项 A 的替换规则）
  B) 接受风险 — 标记为已知，继续（不修改）
```

### Git 历史中的敏感信息（特殊处理）

Git 历史中的敏感信息无法通过简单的文件编辑修复，需要特殊处理。

**Step 1：评估影响范围**

```bash
# 查找包含敏感字符串的所有 commit
git log --all -S "敏感字符串" --oneline

# 查看特定文件的历史变更
git log --all --follow -- "path/to/sensitive/file"

# 统计影响的 commit 数量
git log --all -S "敏感字符串" --oneline | wc -l
```

**Step 2：处理方式选择**

```
AskUserQuestion: Git 历史中发现敏感信息

  以下内容存在于 Git 历史中（即使当前文件已删除/修改）：

  [GIT] commit abc1234 | .env 文件曾被提交后删除
  [GIT] commit def5678 | config.yml 包含真实 API key

  影响范围：3 个 commit 包含敏感内容

  处理方式：
  A) 重写历史 — 使用 git filter-repo 清除敏感内容（推荐，仅限未推送到公共远程的仓库）
     执行前已有 Step 2 的 pre-publish-backup 分支保护原始历史
  B) 新建干净仓库 — 将当前工作区复制到新目录后 git init，保留原仓库完整不动
     注意：不删除原 .git 目录，而是 cp -r 工作区文件到新目录再 git init
  C) 接受风险 — 历史中的敏感内容将通过 git 历史公开
```

**Option A 详细步骤（重写历史）**：

```bash
# 确认 git-filter-repo 可用
pip install git-filter-repo 2>/dev/null || pip3 install git-filter-repo

# 对每个敏感字符串执行替换
git filter-repo --invert-paths --path .env --force
git filter-repo --replace-text <(echo 'REAL_API_KEY==>REPLACE_ME_API_KEY') --force

# 重写后重新检查
git log --all -S "敏感字符串" --oneline  # 应该无结果
```

**Option B 详细步骤（新建干净仓库）**：

```bash
# 1. 创建临时目录
CLEAN_DIR=$(mktemp -d)/$(basename "$(pwd)")
mkdir -p "$CLEAN_DIR"

# 2. 复制工作区文件（排除 .git）
# 注意：不删除原 .git 目录，原仓库保持不动
rsync -av --exclude='.git' ./ "$CLEAN_DIR/"

# 3. 在新目录初始化
cd "$CLEAN_DIR"
git init
git add -A
git commit -m "Initial commit: clean history for public publish"

echo "原仓库未受影响，仍在：$(pwd)"
echo "新干净仓库位于：$CLEAN_DIR"
```

**Option B 的安全说明**：

- 明确：不删除原 `.git` 目录，原仓库保持完整
- Step 2 创建的 `pre-publish-backup` 分支保护了原始历史，即使选择 Option A 也可以通过该分支恢复
- 新建干净仓库后，后续的 Step 5 推送操作在干净仓库目录中执行

### 修复后验证循环（Fix-Verify Loop）

每轮修复完成后，重新运行验证：

```bash
# 重新运行第 1 层规则扫描（完整扫描，非增量）
# 对所有 CRITICAL 和 WARNING 修复过的文件重新检查
# 同时运行 1 轮 AI 抽检（仅扫描修复过的文件及其关联文件），确认修复没有引入新问题
```

**循环规则**：

- 修复后重新扫描确认
- 如果仍有未通过的项，进入下一轮修复
- 最多 3 次（3 轮）修复-验证循环
- 超过 3 次仍有失败项 → 阻塞推送，输出失败项清单供用户手动处理

```
修复验证第 N/3 轮：

已修复：X 项
仍有问题：Y 项
  - [KEY] src/config.py:42 | CRITICAL | github-pat（第 2 次出现）

[Y = 0] → 全部通过，进入 Step 5
[Y > 0 且 N < 3] → 继续下一轮修复
[N = 3 且 Y > 0] → 阻塞推送

阻塞输出：
  以下 Y 项经 3 轮修复仍存在，请手动处理后重新运行：
  1. [KEY] src/config.py:42 | github-pat
  2. ...
```

### `--dry-run` 模式行为

`--dry-run` 模式下，Step 4 不执行任何实际修改，仅输出修复建议：

```
[DRY-RUN] 以下为建议修复方案，未执行任何修改：

CRITICAL 项（N 项，必须处理）：
  1. [KEY] src/config.py:42 | github-pat
     建议操作：自动替换为 REPLACE_ME_GITHUB_TOKEN
  2. [FILE] .env | env-files
     建议操作：删除文件并添加到 .gitignore

WARNING 项（M 项，建议处理）：
  1. [INF] deploy.sh:8 | internal-ip-address | 192.168.1.100
     建议操作：替换为 192.168.x.x
  2. ...

Git 历史问题（K 项）：
  1. [GIT] commit abc1234 | .env 曾被提交
     建议操作：git filter-repo --invert-paths --path .env

要执行这些修复，请使用完整流程模式（不带 --dry-run）。
```

## Step 5: 仓库决策确认 + 创建推送（集中交互 #2）

> 仅完整流程模式执行。`--scan` / `--dry-run` 跳过此步骤。

脱敏通过后，在推送之前集中确认仓库属性。这些决策不可逆或难以逆转。

### 5.1 集中交互确认

**问题 1：仓库可见性**（不可逆——公开后搜索引擎会索引）

```
AskUserQuestion: 仓库可见性
  A) Public — 任何人可见，搜索引擎可索引
     ⚠️ 推送后无法完全撤回，搜索引擎会保留快照
  B) Private — 仅自己和协作者可见
```

**问题 2：仓库名称**（重命名会破坏所有链接）

```
AskUserQuestion: 仓库名称
  A) project-name（当前目录名）
     推送后重命名会导致 clone URL、badge、引用全部失效
  B) 自定义名称：________
```

**问题 3：仓库描述**（可选）

```
AskUserQuestion: 仓库描述（显示在 GitHub About 区域）
  A) 使用 README 第一段自动提取
  B) 自定义描述：________
  C) 暂不设置
```

**交互结果汇总**：

```
即将发布到 GitHub：
  仓库：USERNAME/REPO_NAME
  可见性：Public / Private
  描述：...
  分支：CURRENT_BRANCH
  Commits：N
  脱敏状态：passed（N items reviewed, N auto-fixed）

  备份分支：pre-publish-backup（如需回滚：git reset --hard pre-publish-backup）

确认推送？
```

用户确认后，执行推送。

### 5.2 占位链接替换

推送前扫描代码中的占位用户名/链接，替换为实际 GitHub 用户名：

```bash
# 获取当前 GitHub 用户名
gh api user --jq '.login'
```

扫描以下模式并替换（仅限 README.md 和 Markdown 文件）：
- `yourname/` → `USERNAME/`
- `your-username/` → `USERNAME/`
- `YOUR_GITHUB_USERNAME/` → `USERNAME/`
- `https://github.com/yourname/` → `https://github.com/USERNAME/`

替换后如有改动，提交：
```bash
git add -A
git commit -m "chore: replace placeholder URLs with actual GitHub username"
```

### 5.3 执行推送

#### A. 自动推送（gh CLI 可用且用户选择自动）

1. `gh repo create` 创建仓库（使用确认的名称和可见性）
2. 如果 `gh repo create` 返回名称冲突（HTTP 422）：

```
AskUserQuestion: 仓库 USERNAME/REPO_NAME 已存在
  A) 推送到现有仓库（仅添加 remote）
  B) 换一个名称
  C) 取消
```

3. 添加 remote（命名 `github`，保留 `origin`）：`git remote add github URL 2>/dev/null || git remote set-url github URL`
4. `git push github CURRENT_BRANCH`
5. 设置默认 remote：`git config branch.CURRENT_BRANCH.remote github`

#### B. 手动推送

1. 已完成占位链接替换和提交
2. 输出推送指引：

```
脱敏检查已通过。接下来请手动操作：

1. 在 GitHub 上创建仓库：REPO_NAME（Public/Private）
   https://github.com/new
2. 添加 remote：
   git remote add github https://github.com/USERNAME/REPO_NAME.git
3. 推送：
   git push github CURRENT_BRANCH

完成后建议：
   git config branch.CURRENT_BRANCH.remote github
```

## Step 6: 验证 + 输出报告

> 完整流程模式：验证仓库 + 完整报告。
> `--scan`：仅扫描报告。
> `--dry-run`：扫描报告 + 修复建议。

### 6.1 仓库验证（仅自动推送模式）

```bash
# 验证仓库可访问
gh repo view --json url,visibility,defaultBranchRef

# 验证远程分支与本地一致
git fetch github
git log github/CURRENT_BRANCH --oneline -1
```

如验证失败，输出排查指引，不自动重试。

### 6.2 输出报告

**完整流程报告**：

```
=== GitHub Safe Publish Report ===

Published to GitHub:
  URL: https://github.com/USERNAME/REPO
  Branch: BRANCH
  Commits: N
  Visibility: public / private
  Description: ...

Desensitization:
  Status: passed
  Items reviewed: N
  Auto-fixed: N
  Manual confirmed: N
  AI semantic scan rounds: 1-2

Backup:
  Branch: pre-publish-backup
  Rollback: git reset --hard pre-publish-backup
  Cleanup: git branch -d pre-publish-backup (when ready)

Next steps:
  - Verify repository at the URL above
  - Set up branch protection (Settings → Branches)
  - Add collaborators if needed
  - Consider enabling GitHub Actions for CI
  - Delete pre-publish-backup branch when confident
```

**--scan 报告**：

```
=== Scan Report ===

Repository: LOCAL_PATH
Branch: BRANCH
Files scanned: N

Layer 1 (Rule-based):
  CRITICAL: N items
  WARNING: N items

Layer 2 (AI Semantic):
  Additional findings: N items

Detailed findings:
  [CRITICAL] file:line | rule-name | ghp...xyz (前后各显示3字符，中间用...替代)
  [WARNING]  file:line | rule-name | ghp...xyz (前后各显示3字符，中间用...替代)
  ...

Recommendation: Fix CRITICAL items before publishing. Run without --scan to auto-fix.
```

**--dry-run 报告**：

在 --scan 报告基础上，追加每个发现项的建议修复方案：

```
Suggested fixes:
  [CRITICAL] file:line | rule-name
    → Auto-replace with REPLACE_ME
    → Or remove the file from tracking
  [WARNING]  file:line | rule-name
    → Confirm as safe (no action needed)
    → Or replace with placeholder
```

### 6.3 报告文件

将上述报告内容写入文件。每次运行生成独立文件，不覆盖历史报告。

**文件路径**: `safe-publish-report-YYYYMMDD-HHMM.md`（项目根目录，与 `.git` 同级）

**多轮扫描不覆盖**：文件名包含精确到分钟的时间戳，重复运行生成新文件。同一分钟内再次运行会覆盖上次报告（此时第二次结果更完整，属预期行为）。

**报告内容按模式区分**：
- 完整流程：扫描结果 + 修复记录（每项：原内容 → 替换内容）+ 仓库 URL + 备份回滚指引
- `--scan`：扫描结果 + 发现列表（CRITICAL / WARNING 分类，含文件路径和行号）
- `--dry-run`：扫描结果 + 发现列表 + 每项推荐修复方案

**自动更新 .gitignore**：

```bash
if ! grep -q "safe-publish-report-" .gitignore 2>/dev/null; then
    echo "safe-publish-report-*.md" >> .gitignore
fi
```

仅在 `.gitignore` 不包含该模式时追加，避免重复。

**写入失败降级**：如果报告文件写入失败（磁盘满/权限不足），输出警告但不阻塞流程，将报告内容直接打印到终端作为降级方案。

```
📄 报告已保存至 safe-publish-report-20260526-1430.md
⚠️ 此文件包含敏感信息摘要，请勿提交到公开仓库。
```

## 可选模块

### --seo 模块

> 推送成功后执行。不可与 `--scan` / `--dry-run` 组合。

#### SEO-1: Description 优化

通过 `gh repo edit --description` 设置仓库描述：
- 120 字符以内，主关键词开头
- 包含核心技术关键词（如 Python、Claude Code skill、secret scanning）
- 从 README 第一段提取，人工确认后应用

```
AskUserQuestion: 仓库描述
  A) {自动提取的 description}
  B) 自定义：________
```

#### SEO-2: Topics 标签

通过 `gh repo edit --add-topic` 添加标签：
- 6-20 个标签
- 三类均衡分布：用途（what）/ 技术栈（how）/ 领域（domain）
- 不用项目主语言做标签（GitHub 自动检测语言）
- 推荐标签：根据项目内容自动推断，人工确认后应用

#### SEO-3: Badges（shields.io 静态 badge）

在 README.md 顶部添加静态 badge（不依赖 CI）：

```
![Version](https://img.shields.io/badge/version-X.Y.Z-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Claude%20Code-purple)
```

Badge 规则：
- License badge：从 LICENSE 文件检测
- Version badge：从 SKILL.md frontmatter 读取
- Platform badge：固定为 Claude Code
- Tests badge：如果 tests/ 存在则添加
- 手动 URL，不依赖 CI 状态 API

#### SEO-4: README 结构检查

检查 README.md 是否包含以下结构，缺少则建议补充：
- **是什么**：一句话描述项目功能
- **给谁用**：目标用户和使用场景
- **怎么用**：安装和使用步骤
- **技术栈**：关键技术说明

关键词自然分布在正文和标题中，不写 Keywords 段落。

#### SEO-5: 提交并推送

```bash
git add README.md docs/images/ 2>/dev/null
git commit -m "docs: SEO optimization for GitHub visibility"
git push github CURRENT_BRANCH
```

### --ci 模块

> 推送成功后执行。不可与 `--scan` / `--dry-run` 组合。

#### CI-1: 项目类型检测

自动检测项目类型和测试框架：

```bash
# 检测语言
ls *.py setup.py pyproject.toml requirements*.txt 2>/dev/null  # Python
ls package.json tsconfig.json 2>/dev/null                      # Node.js
find . -name "*.sh" -not -path "./.git/*" | head -5            # Bash

# 检测测试框架
grep -rl "pytest\|unittest" tests/ 2>/dev/null                 # Python test
grep -rl "jest\|mocha\|vitest" . --include="*.json" 2>/dev/null # JS test

# 检测系统依赖
grep -rl "tmux\|selenium\|chromium" . --include="*.py" --include="*.sh" --include="*.js" 2>/dev/null
```

#### CI-2: 平台矩阵决策

| 项目类型 | 系统依赖 | 平台矩阵 |
|----------|---------|----------|
| Bash/tmux 项目 | tmux 等 | `ubuntu-latest` + `macos-latest` |
| 纯 Python | 无 | 三平台（注意 `PYTHONUTF8: "1"`） |
| 纯 Python | tmux/selenium | 按依赖选平台 |
| Node.js | 无 | 三平台 |
| 跨平台 GUI | — | `ubuntu-latest` + `macos-latest` + `windows-latest` |

#### CI-3: 生成 .github/workflows/test.yml

根据检测结果生成 CI 配置。模板包含：

**Python 项目模板**：
```yaml
name: Tests
on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]  # 按检测结果调整
        python-version: ['3.10', '3.12']
    runs-on: ${{ matrix.os }}
    env:
      PYTHONUTF8: "1"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ -v --tb=short
```

**Bash 项目模板**：
```yaml
name: Tests
on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: bash scripts/run_tests.sh
```

#### CI-4: 确认并推送

```
AskUserQuestion: CI 配置已生成
  A) 直接推送
  B) 我先看看再决定
  C) 不需要 CI
```

确认后：
```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions test workflow"
git push github CURRENT_BRANCH
```

## 注意事项

- 不删除 `origin` remote（通常是内部 NAS Git）
- 不改变当前分支名
- 不 force push
- 脱敏发现的真实密钥必须处理，不能跳过
- 备份分支 `pre-publish-backup` 不推送到远程
- SEO 模块只修改 README.md 和 metadata，不修改源代码
- CI 模块检测已有 `.github/workflows/` 下文件，已存在时不覆盖，改为询问用户
