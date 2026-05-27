# github-safe-publish v2 设计文档

日期：2026-05-25
状态：Final (v0.6.1 delivered)

## 1. 项目定位

一个 Claude Code skill，帮助用户安全地将本地 Git 项目发布到 GitHub 公开仓库。

核心价值：**多维度脱敏扫描**（规则 + AI 两层架构）+ 端到端发布流程。

## 2. 一期范围

- 平台：Claude Code（plugin 结构），架构预留多平台扩展
- 发布：marketplace 安装 + 手动安装双模式
- 测试：专项验证脚本（结构 + 内容检查）

## 3. Skill 命名与参数

Skill 名称：`github-safe-publish`

```
/github-safe-publish                    # 核心流程（脱敏+发布）
/github-safe-publish --seo              # 核心 + SEO 优化
/github-safe-publish --ci               # 核心 + CI 生成
/github-safe-publish --seo --ci         # 全部
/github-safe-publish --scan-only        # 只做脱敏扫描，输出报告，不修复不发布
/github-safe-publish --dry-run          # 模拟完整流程：扫描+模拟修复建议，但不做任何实际修改
```

**参数互斥与冲突处理**：
- `--scan-only` 和 `--dry-run` 不能与 `--seo` / `--ci` 组合（SEO 和 CI 只对已推送的仓库有意义，扫描模式不推送）
- `--seo` 和 `--ci` 可以同时使用（完整功能模式）
- 无效组合直接报错并退出，例如：`"--scan-only 不能与 --seo 组合，请使用完整流程模式"`
- `--dry-run` 与 `--scan-only` 的区别：`--scan-only` 只输出扫描报告；`--dry-run` 在报告基础上还会展示每个发现项的推荐修复方案（但不执行修复）

**流程控制矩阵**：

| 步骤 | 完整流程 | --scan-only | --dry-run |
|------|---------|-------------|-----------|
| Step 1: 前置检查+参数确认 | 执行 | 执行 | 执行 |
| Step 2: 创建备份分支 | 执行 | 跳过 | 跳过 |
| Step 3: 脱敏扫描 | 执行 | 执行 | 执行 |
| Step 4: 自动修复+用户确认 | 执行 | 跳过 | 输出修复建议但不执行 |
| Step 5: 仓库决策+推送 | 执行 | 跳过 | 跳过 |
| Step 6: 验证+报告 | 执行 | 仅扫描报告 | 仅扫描报告+修复建议 |

## 4. 核心流程（6 步）

```
Step 1: 前置检查 + 参数确认（集中交互 #1）
Step 2: 创建备份分支
Step 3: 脱敏扫描（两层架构）
Step 4: 自动修复 + 用户确认
Step 5: 仓库决策确认 + 创建推送（集中交互 #2）
Step 6: 验证 + 输出报告
```

交互设计原则：两个集中交互环节，用户每次只专注一类决策。
- 交互 #1（Step 1）："我要做什么、怎么做"——确认参数和工作模式
- 交互 #2（Step 5）："我要发布到哪里、叫什么"——确认仓库属性

### Step 1: 前置检查 + 参数确认（集中交互 #1）

所有前置检查和参数决策集中在一次交互中完成。任何一项不满足则停在当前步骤。

#### 1.1 自动检查（无交互）

```
检查项：
1. 当前目录是 git 仓库？
   ├── 是 → 继续
   └── 否 → 进入 1.2 交互询问

2. git 仓库至少有 1 个 commit？
   ├── 是 → 继续
   └── 否 → 阻断：需要至少一次 commit 才能备份和回滚

3. gh CLI 是否可用（gh auth status）？
   → 记录结果，用于 1.2 的推送方式选项
```

#### 1.2 集中交互确认

将以下决策合并为一次 AskUserQuestion（最多 4 个问题）：

**问题 1：工作模式**
```
skill 被调用时可能带了参数（--seo/--ci/--scan-only/--dry-run），
也可能是无参调用。需要确认最终的工作模式：

AskUserQuestion: 确认工作模式
  A) 完整流程：脱敏扫描 → 发布到 GitHub
  B) 仅扫描：只做脱敏检查，不发布（--scan-only）
  C) 模拟运行：扫描出报告，不做任何修改（--dry-run）

  如果带了 --seo 或 --ci：
  D) 完整流程 + SEO 优化
  E) 完整流程 + CI 生成
  F) 完整流程 + SEO + CI
```

**问题 2：推送方式**（仅完整流程模式显示）
```
AskUserQuestion: 推送方式
  情况 A（gh CLI 可用）：
    A) 使用 gh CLI 自动创建仓库并推送（推荐）
    B) 我自己手动推送，只帮我做好脱敏和本地准备
  情况 B（gh CLI 不可用）：
    A) 我自己手动推送（gh CLI 未安装）
    B) 我先去安装 gh CLI，等会再来
```

**问题 3：非 git 目录的处理**（仅当前目录不是 git 仓库时显示）
```
AskUserQuestion: 当前目录不是 Git 仓库
  A) 帮我初始化（git init + 生成标准 .gitignore + 首次 commit）后继续
  B) 我先自己备份和初始化，回来再用
```

**交互结果汇总**：
确认完成后，输出一份配置摘要让用户最终确认：
```
工作模式：完整流程
推送方式：gh CLI 自动推送
附加模块：SEO + CI
目标仓库：待扫描后确认
```

用户确认后，正式开始工作。

### Step 2: 创建备份分支

在任何修改之前创建回滚点。仅在完整流程模式下执行（`--scan-only` 和 `--dry-run` 跳过此步骤，因为这两种模式设计为纯只读操作，子 agent 不被授予写入工具权限）。

```bash
# 处理未提交内容
if git diff --quiet HEAD && git diff --quiet --cached; then
    # 工作区干净，直接创建分支
    git branch pre-publish-backup HEAD
else
    # 有未提交内容，先 stash 再创建分支
    git stash push -m "pre-publish-stash" --include-untracked
    git branch pre-publish-backup HEAD
    git stash pop || {
      echo "WARNING: stash pop 产生冲突。保留 stash，使用 HEAD 状态创建备份分支。"
      echo "用户可手动执行 git stash pop 恢复工作区。"
      git stash drop
    }
fi
```

规则：
- 备份分支名固定为 `pre-publish-backup`
- 如果该分支已存在，先删除再创建（注意：重新运行会覆盖上次的备份点，这是预期行为——备份的是"最近一次发布前的状态"）
- 备份分支不推送到远程
- 推送完成后告知用户可以删除该分支
- 回滚方式：`git reset --hard pre-publish-backup`（硬回滚到备份点）

### Step 3: 脱敏扫描（两层架构）

#### 第 1 层：确定性规则扫描

借鉴 Gitleaks（222 条规则）和 Microsoft Presidio 的结构化思路，用确定性规则逐项检查。

**扫描范围**：
- 所有 git 跟踪文件（`git ls-files`）
- 排除：二进制文件（图片、视频、编译输出、字体）
- 排除：`.git` 目录内部
- 排除：子模块（由用户自行处理）
- 可选警告：`.gitignore` 中列出但仍存在于工作区的敏感文件

**A. 密钥/凭证（正则 + 熵值）**

50+ 常见 API key 格式，覆盖主要服务商：
- 云服务：AWS、Azure、GCP、Alibaba
- 代码平台：GitHub PAT、GitLab Token
- AI 服务：OpenAI、Anthropic、HuggingFace
- 通信：Slack、Twilio、SendGrid
- 支付：Stripe、PayPal
- 通用：Private Key、JWT、generic-api-key（高熵字符串 + 关键字）

熵值检测：字符串长度 ≥ 20 且 Shannon 熵 ≥ 4.5 的可疑字符串。注意：熵值检测仅在已知密钥关键字附近触发（与 Gitleaks 的 generic-api-key 规则一致），不全局扫描所有字符串，以避免 Base64、哈希值等误报。

**B. PII（正则）**

- 邮箱：非 GitHub 公开邮箱的个人邮箱
- 手机号：中国大陆手机号（1[3-9]\d{9}）
- 身份证号：18 位身份证号格式
- 中文姓名：百家姓 + 常见名模式（低置信度，归入 WARNING）

**C. 内部基础设施（正则，本项目独有）**

- 内网 IP：192.168.x.x、10.x.x.x、172.16-31.x.x
- 内部域名：非标准 TLD 的域名、.local、.internal
- 硬编码本地路径：/Users/xxx/、C:\Users\、/home/xxx/
- NAS/内网服务路径：包含 nas、vpn、internal 关键字的 URL

**D. 文件黑名单**

- .env、*.pem、*.key、*.db、*.sqlite、credentials.*
- .gitignore 充分性检查：是否有这些扩展名的忽略规则

**E. Git 历史扫描**

- commit message 中的内部系统名、同事姓名、内部链接
- 已删除文件中残留的敏感信息

规则扫描输出：结构化报告，每项包含 维度 / 文件:行号 / 内容 / 严重级别。

#### 第 2 层：AI 语义扫描（1-2 轮，独立子 agent 执行）

通过独立子 agent 执行（不共享主对话上下文，隔离敏感信息），补充规则无法覆盖的语义泄露：

- 业务数据泄露（内部项目代号、真实用户数据、订单号）
- 可溯源叙事（可通过搜索引擎定位到个人/组织的描述）
- 间接推断（文件路径推断内部结构、时间戳推断工作节奏）
- 规则扫描误报排除（降低 WARNING 项的误报率）

收敛判定：连续 1 轮无新发现即停止，最多 2 轮。

**关于 v1 的 5 轮扫描**：v1 采用 5 轮纯 AI 自由扫描，v2 改为"规则确定性扫描 + 1-2 轮 AI 语义补充"两层架构。理由：规则扫描可复现、覆盖率高，AI 只负责规则无法覆盖的语义部分，因此不需要 5 轮。竞品对比矩阵中的"多轮扫描"优势改为"两层扫描（规则+AI）"定位。

### Step 4: 自动修复 + 用户确认

结果分类：

- **CRITICAL**：真实密钥、凭证、个人信息 → 必须处理，阻塞推送
- **WARNING**：可能敏感但不确定 → 列出给用户判断
- **SAFE**：示例占位符（your_xxx、REPLACE_ME）、README 通用描述

**CRITICAL 修复选项**（逐项询问用户）：

- A) **自动替换** — agent 将敏感内容替换为泛化占位符
- B) **手动修复** — 用户自己在编辑器里改，改完后 agent 重新扫描验证
- C) **删除文件** — 从 git 中移除整个文件（git rm）
- D) **确认安全** — 用户确认该内容实际不敏感（需输入理由）

自动替换规则：
- 真实密钥/token → `REPLACE_ME_<类型>`（如 `REPLACE_ME_API_KEY`）
- 个人邮箱 → `user@example.com` 或 GitHub 公开邮箱
- 内部 IP/域名 → `192.168.x.x` / `internal.example.com`
- 真实姓名 → `FIRST_NAME` / `LAST_NAME`
- 手机号 → `1XX-XXXX-XXXX`
- 可溯源叙事 → 泛化为通用描述

**WARNING 修复选项**：
- A) 同上处理
- B) 接受风险，标记为已知，继续

**Git 历史中的敏感信息**（特殊情况）：
1. 评估影响范围：`git log --all -S "敏感字符串" --oneline`
2. 处理方式：
   - A) 重写历史（git filter-repo，仅限未推送的 commit）。执行前已有 Step 2 的 `pre-publish-backup` 分支保护原始历史。
   - B) 新建干净仓库（将当前工作区复制到新目录后 init，保留原仓库完整不动）。明确：不删除原 `.git`，而是 `cp -r` 工作区到新目录再 `git init`。
   - C) 接受风险

**修复后验证**：重新运行第 1 层规则扫描 + 1 轮 AI 抽检，确认修复完成。修复-验证循环最多 3 次，超过 3 次仍有失败项则阻塞推送，输出失败项清单供用户手动处理。

### Step 5: 仓库决策确认 + 创建推送（集中交互 #2）

脱敏通过后，在推送之前集中确认仓库属性。这些决策不可逆或难以逆转。

#### 5.1 集中交互确认（仅完整流程模式）

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
  仓库：zwyin/project-name
  可见性：Public
  描述：A Claude Code skill for safely publishing...
  分支：master
  Commits：12
  脱敏状态：passed（5 items reviewed, 3 auto-fixed）

  备份分支：pre-publish-backup（如需回滚：git reset --hard pre-publish-backup）

确认推送？
```

用户确认后，执行推送。

#### 5.2 执行推送

**A. 自动推送（gh CLI 可用且用户选择自动）**：

1. 扫描并替换占位链接（yourname/ → 实际用户名）
2. 如有改动则提交
3. `gh repo create` 创建仓库（使用确认的名称和可见性）
4. 如果 `gh repo create` 返回名称冲突（HTTP 422）：
   ```
   AskUserQuestion: 仓库 USERNAME/REPO_NAME 已存在
     A) 推送到现有仓库（仅添加 remote）
     B) 换一个名称
     C) 取消
   ```
5. 添加 remote（命名 github，保留 origin）
6. `git push github CURRENT_BRANCH`

**B. 手动推送**：

1. 扫描并替换占位链接（yourname/ → 实际用户名）
2. 如有改动则提交
3. 输出推送指引：
   ```
   脱敏检查已通过。接下来请手动操作：

   1. 在 GitHub 上创建仓库：REPO_NAME（Public/Private）
      https://github.com/new
   2. 添加 remote：
      git remote add github https://github.com/USERNAME/REPO_NAME.git
   3. 推送：
      git push github CURRENT_BRANCH
   ```

### Step 6: 验证 + 输出报告

**自动推送模式**：

```bash
gh repo view --json url,visibility
```

**手动推送模式**：

输出检查清单，由用户确认推送结果。

**输出总结**：
```
Published to GitHub:
  URL: https://github.com/USERNAME/REPO
  Branch: BRANCH
  Commits: N
  Visibility: public/private
  Desensitization: passed/warnings (N items reviewed)
  Backup branch: pre-publish-backup
```

## 5. 可选模块

### 5.1 `--seo` 模块

推送成功后执行：

1. **Description**（gh repo edit --description）
   - 120 字符以内，主关键词开头
   - 包含核心技术关键词

2. **Topics**（gh repo edit --add-topic）
   - 6-20 个标签
   - 用途 / 技术栈 / 领域三类均衡
   - 不用项目主语言做标签

3. **Badges**（shields.io 静态 badge）
   - License、Tests、Coverage、Platform、Python/Node
   - 手动 URL，不依赖 CI

4. **截图/GIF**
   - README 首屏放应用截图
   - 存放 docs/images/screenshot.png
   - 静态展示用 PNG，交互流程用 GIF

5. **README 优化**
   - 关键词自然分布在正文和标题中
   - 不写 Keywords 段落
   - 结构：是什么 → 给谁用 → 优势 → 怎么用 → 技术栈

6. **中英双语**（可选）
   - 英文 README.md（根目录，SEO 入口）
   - 中文 docs/README_zh.md
   - 顶部互相链接

**SEO 模块产生的文件修改**（badges、README、截图）需要单独提交并推送：
```bash
git add README.md docs/ docs/images/
git commit -m "docs: SEO optimization for GitHub visibility"
git push github CURRENT_BRANCH
```

### 5.2 `--ci` 模块

推送成功后执行：

1. 检测项目类型（Python / bash / Node.js / 混合）
2. 检测测试框架（pytest / unittest / jest / 无）
3. 检测系统依赖（grep 代码中的 tmux / selenium 等）
4. 选择平台矩阵 + 生成 .github/workflows/test.yml
5. 可选：master 分支保护规则

平台选择决策树：
- bash/tmux 项目 → Ubuntu + macOS
- 跨平台 GUI → Ubuntu + macOS + Windows
- 纯 Python 无系统依赖 → 三平台（但先验证路径/编码处理）

## 6. 项目结构

对齐 project-walkthrough-skill 的成熟模式：

```
github-safe-publish/
├── .claude-plugin/
│   ├── plugin.json                 # Claude Code 插件元数据
│   └── marketplace.json            # Marketplace 注册信息
├── skills/
│   └── github-safe-publish/
│       └── SKILL.md                # Skill 定义（唯一事实源）
├── docs/
│   ├── scanning-rules.md           # 脱敏扫描规则参考（第 1 层规则的完整正则定义，迭代 1 交付物）
│   ├── ci-actions-learnings.md     # CI 经验（已有）
│   ├── competitive-research.md     # 竞品调研（已有）
│   └── superpowers/specs/          # 设计文档
├── scripts/
│   ├── validate_skill.sh           # Skill 结构验证
│   ├── release.sh                  # 版本发布自动化
│   └── convert.sh                  # 多平台格式转换
├── tests/
│   ├── test_skill_structure.py     # SKILL.md 结构检查
│   ├── test_scanning_rules.py      # 扫描规则完整性验证
│   ├── test_detection.py           # 134/135 规则端到端检测测试
│   ├── test_entropy.py             # Shannon 熵值计算验证
│   ├── test_convert.py             # convert.sh 多平台输出验证
│   ├── test_plugin_metadata.py     # plugin.json / marketplace.json + 版本同步验证
│   └── test_conftest.py            # conftest 辅助函数边界测试
├── README.md
├── CHANGELOG.md
├── CLAUDE.md                       # 项目内部规则
├── LICENSE
└── .github/workflows/test.yml      # CI
```

### 版本管理

和 project-walkthrough-skill 对齐——SKILL.md frontmatter 的 version 字段为唯一版本源，release.sh 同步到 6 个位置。

### 测试策略

专项验证脚本 + pytest 测试套件（235 tests, 99% coverage），覆盖：

1. **SKILL.md 结构检查**：frontmatter 完整性、步骤编号连续性、参数定义一致性
2. **扫描规则验证**：规则数量（135 guard）、正则有效性、维度覆盖完整性
3. **规则检测测试**：134/135 规则端到端验证（从 scanning-rules.md 提取正则，验证能匹配目标模式）
4. **熵值计算验证**：Shannon entropy 阈值 4.5 与示例 key 校准
5. **多平台转换验证**：convert.sh 输出的 Cursor/Windsurf/OpenCode 格式
6. **插件元数据验证**：plugin.json / marketplace.json 格式和字段完整性
7. **版本同步验证**：5/6 处版本号一致性（SKILL.md、plugin.json、marketplace.json、README badge、CHANGELOG header）

## 7. 不做的事（一期）

- 规则外部配置文件（类似 Gitleaks TOML）—— 一期规则内嵌在 SKILL.md 中
- AI 模型切换/调优 —— 使用 Claude Code 默认模型
- 国际化（skill 本身的 i18n）—— 一期中英混合文档

## 8. 迭代节奏

1. **迭代 1：脱敏扫描核心** ✅ —— 两层扫描架构 + 修复流程 + 验证脚本
2. **迭代 2：发布流程** ✅ —— 仓库创建 + 推送 + 备份机制
3. **迭代 3：可选模块** ✅ —— SEO + CI 生成
4. **迭代 4：项目工程化** ✅ —— plugin 结构、CI、README、marketplace
5. **迭代 5：多平台适配** ✅ —— convert.sh + Cursor/Windsurf/OpenCode 文件
6. **5 轮独立 review** ✅ —— 规则计数、正则修复、流程逻辑、跨文件一致性、工程文件
7. **Dogfooding + 发布** ✅ —— 用 skill 自身发布到 GitHub，SEO 优化，Release 创建
