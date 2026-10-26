# Codex CLI 加载机制核验（Task 10）

> 目的：以官方文档 + 本机二进制实测为依据，确认 OpenAI Codex CLI 如何发现
> 自定义 skills 与指令文件。本文档是 Task 11/12/13（convert.sh `--codex`、
> install.sh、验收）的**唯一路径与格式依据**；任务书中未经证实的
> `~/.codex/skills/` 假设已按实测修正（该路径真实存在，但并非官方文档
> 作者作用域表中的推荐位置，详见下文）。
>
> 核验环境：macOS 15.7.3 (aarch64)，Codex CLI **codex-cli 0.164.0**，
> 安装方式 `npm install -g @openai/codex`（官方 npm 包，含
> `@openai/codex-darwin-arm64` 原生二进制）。核验日期 2026-10-26。
>
> 证据分级：**[official]** = OpenAI 官方文档明文；**[binary]** = 本机
> 0.164.0 二进制实测行为；**[official+binary]** = 两者一致；**[community]**
> = 官方未记录、仅有社区/生态实践。

## 结论速览（TL;DR）

| 问题 | 答案 | 级别 |
|---|---|---|
| 全局指令文件 | `~/.codex/AGENTS.md`（`AGENTS.override.md` 优先） | official+binary |
| 全局 skills 目录 | `$CODEX_HOME/skills`（默认 `~/.codex/skills`）与 `$HOME/.agents/skills` 都会被扫描 | binary（前者）/ official（后者） |
| 项目级指令文件 | 仓库根到 CWD 逐级 `AGENTS.md`（可用 `project_doc_fallback_filenames` 兼容 `CLAUDE.md`） | official+binary |
| 项目级 skills 目录 | `<repo>/.agents/skills`（CWD 向上到仓库根都扫） | official+binary |
| SKILL.md 直接识别？ | **是**。Codex 原生解析 SKILL.md frontmatter（`name`+`description` 必填），无需 AGENTS.md 包装 | official+binary |
| 推荐安装路径 | 每用户全局：`~/.codex/skills/<skill-name>/`（或跨 agent 共享的 `~/.agents/skills/`） | official+binary |
| 无认证能否运行 | 指令/技能**发现与注入**不需要认证；**模型调用**需要（ChatGPT 登录或 API key），本地模型（ollama/lmstudio）可完全无 OpenAI 认证 | official+binary |

## 1. 全局与项目级加载机制

### 1.1 AGENTS.md 指令链 [official+binary]

官方文档（canonical：`https://learn.chatgpt.com/docs/agent-configuration/agents-md`，
同内容亦在 `https://developers.openai.com/codex/agents-md`）：

1. **全局层**：Codex home（默认 `~/.codex`，可用 `CODEX_HOME` 覆盖）下读
   `AGENTS.override.md`，不存在则读 `AGENTS.md`，取第一个非空文件。
2. **项目层**：从项目根（通常 Git 根）向下走到 CWD，每级目录按
   `AGENTS.override.md` → `AGENTS.md` → `project_doc_fallback_filenames`
   （如 `CLAUDE.md`、`TEAM_GUIDE.md`）顺序取**至多一个**文件。
3. **合并**：自根向下拼接，越靠近 CWD 越后出现、优先级越高；总量上限
   `project_doc_max_bytes`（默认 32 KiB）。

实测（`codex debug prompt-input`，见 §5 实验记录）：全局与项目
AGENTS.md 内容以 `# AGENTS.md instructions for <dir>` 头注入同一条
user 消息，项目内容以 `--- project-doc ---` 分隔附后。

**CLAUDE.md 兼容实测**：Codex 默认**不**读 CLAUDE.md；在
`~/.codex/config.toml` 配置 `project_doc_fallback_filenames = ["CLAUDE.md"]`
后实测注入成功。对本合集的意义：Codex 侧**不需要**为 CLAUDE.md 生成镜像，
但用户可选择加一行 fallback 配置复用同一份指令文件。

### 1.2 Skills 发现（渐进式披露）[official+binary]

官方文档（canonical：`https://learn.chatgpt.com/docs/build-skills`，
同内容在 `https://developers.openai.com/codex/skills`）给出的作者作用域表：

| Scope | 位置 | 说明 |
|---|---|---|
| REPO | `$CWD/.agents/skills`，及 CWD 向上至仓库根的每一级 `.agents/skills` | 团队可入库的仓库级技能 |
| USER | `$HOME/.agents/skills` | 用户个人、跨仓库生效 |
| ADMIN | `/etc/codex/skills` | 机器/容器级 |
| SYSTEM | 随 Codex 打包（实测落盘在 `$CODEX_HOME/skills/.system`，含 skill-creator、skill-installer、openai-docs、imagegen） | 官方内置 |

官方作用域表**未列** `$CODEX_HOME/skills`（即 `~/.codex/skills`），但二进制
实测确认它是扫描根之一（见 §5 r0），且官方内置 `$skill-installer` 的安装
目标就是它（`$CODEX_HOME/skills/<skill-name>`，"Installs into
$CODEX_HOME/skills/<skill-name>, defaults to ~/.codex/skills"）。
**文档与二进制不一致时以二进制为准**（用户跑的是二进制）：两处都可用，
`~/.codex/skills` 是官方安装器的事实目标，`~/.agents/skills` 是官方文档
明示的跨仓库用户位置。

技能清单以 `<skills_instructions>` developer 消息注入：先给"技能根表"
（`r0`/`r1`/… 到绝对路径的映射）+ 每技能一行 `name: description 截断
(file: rN/<name>/SKILL.md)`；模型选中后才读完整 SKILL.md（渐进式披露）。
初始清单预算默认上下文窗口的 2%（未知时 8000 字符），可用
`skills.max_context_tokens` 调整（上限 10000 tokens）。文件系统技能由
模型直接从磁盘读取；`skills.list`/`skills.read` 工具仅用于 orchestrator
类技能。同名技能不合并、都会列出；符号链接目录会被跟随
（"Codex supports symlinked skill folders and follows the symlink target"）。

显式调用：TUI 里 `$skill-name` 提及或 `/skills` 选择器；隐式调用靠
description 匹配（`agents/openai.yaml` 里 `policy.allow_implicit_invocation:
false` 可关闭）。`config.toml` 可按路径禁用单个技能：

```toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

## 2. SKILL.md 格式：直接识别，无需 AGENTS.md 包装 [official+binary]

- 官方：技能 = 目录 + 必含 `SKILL.md`（frontmatter 必填 `name`、
  `description`），可选 `scripts/`、`references/`、`assets/`、
  `agents/openai.yaml`。"Skills build on the open agent skills standard"
  （即 agentskills.io 开放标准）——与 Claude Code 的 SKILL.md 同源同构。
- 二进制：字符串表含 frontmatter 解析与报错
  （`Unexpected key(s) in SKILL.md frontmatter: ... Allowed properties are: ...`）；
  本机既有 Claude 格式技能（`~/.codex/skills/gstack-qa/SKILL.md` 等）被
  原样列出。`codex features list` 中 `skill_search` 为 **stable/true**。
- 结论：**本合集 SKILL.md 可直接被 Codex 使用，零格式转换**。Task 11 的
  `--codex` 产物应为技能目录复制（仿 `_convert_opencode`），而非
  AGENTS.md 拼接。可选增强：`agents/openai.yaml`（UI 元数据/调用策略），
  Claude 侧无此文件不影响。

## 3. 第三方合集的实际安装路径与命令

对 ruyi-skills 这类合集，两条已验证路线（均为复制/链接 SKILL.md 目录，
不需要改写格式）：

### 路线 A：全局安装（每用户，所有仓库可用）[official+binary]

```bash
# 逐技能复制（skill-name = skills/<skill-name>/SKILL.md 的目录名）
mkdir -p ~/.codex/skills
cp -R skills/<skill-name> ~/.codex/skills/<skill-name>

# 或官方安装器（会话内 $skill-installer，等价脚本亦可用于自动化）：
#   scripts/install-skill-from-github.py --repo zwyin/ruyi-skills --path skills/<skill-name>
# （脚本随 $CODEX_HOME/skills/.system/skill-installer 分发；默认源是
#  openai/skills curated，但支持任意 GitHub repo/path）

# 或符号链接（官方明文支持 follow symlink，适合开发期实时跟踪）
ln -s "$PWD/skills/<skill-name>" ~/.codex/skills/<skill-name>

# 跨 agent 共享位（官方 USER scope；本机亦被 vercel-labs/skills 等生态工具使用）
mkdir -p ~/.agents/skills && cp -R skills/<skill-name> ~/.agents/skills/<skill-name>
```

安装后无需重启即被下一轮会话发现（官方："Codex detects skill changes
automatically. If an update doesn't appear, restart Codex."）。

### 路线 B：项目级安装（随仓库分发）[official+binary]

```bash
mkdir -p .agents/skills
cp -R /path/to/ruyi-skills/skills/<skill-name> .agents/skills/<skill-name>
git add .agents/skills && git commit
```

用户克隆仓库后在任意子目录启动 `codex` 即可发现（CWD 向上扫到仓库根）。

### 验证命令（不需要认证）[binary]

```bash
codex debug prompt-input "hi" 2>/dev/null | grep -o '<skill-name>.*'
```

该子命令渲染模型可见输入（含 `<skills_instructions>` 根表与技能清单），
全程不触发模型调用，本任务全部加载实验均以此完成（§5）。

### 分发备注 [official]

官方对"给别人装"的推荐载体是 **plugins**（技能+MCP+连接器的打包格式，
`codex plugin add`，ChatGPT/Codex 共用插件目录），文档原话
"For installable distribution, prefer plugins"。本仓库 v0.10.0 可先交付
skills 目录路线（已验证可用），plugin 化留作后续选项；另注：官方插件
文档含 "Submit a Claude Code plugin" 指南，二进制内亦见
`anthropics/claude-plugins-official` marketplace 兼容痕迹，说明 Claude
Code 插件格式与 Codex 插件生态有官方互通通道，值得后续调研。

## 4. 认证模式（Task 14 验收相关）

[official]（`https://learn.chatgpt.com/docs/auth`）+ [binary]：

- **OpenAI 模型必须认证**，二选一：
  - ChatGPT 订阅登录：`codex login`（浏览器 OAuth，localhost:1455 回调）；
  - API key：`printenv OPENAI_API_KEY | codex login --with-api-key`（CI
    推荐）。凭据缓存于 `~/.codex/auth.json` 或 OS keyring
    （`cli_auth_credentials_store = file|keyring|auto|ephemeral`）。
- **无 OpenAI 认证的运行方式存在**：自定义 model provider 不设
  `requires_openai_auth`/`env_key` 即"无认证，适用于本地模型"；CLI 侧
  `codex --oss --local-provider ollama|lmstudio` 直连本地推理。即
  **发现/注入类验证完全免认证，端到端技能调用验证可用本地模型免 OpenAI
  账号**（代价是模型非 GPT 系列，行为代表性弱）。
- 无头环境：`codex login --device-auth`（设备码，beta）或拷贝
  `auth.json`（官方明示做法，注意该文件等同密码）。
- 本机现状：`codex login status` 报 "Logged in using ChatGPT" 但
  `codex doctor` 报 "stored credentials are incomplete"（auth.json 仅
  2 字节，为 7 月桌面端集成残留）。**端到端模型调用实验待主人执行
  `codex login` 完成浏览器登录**；除此之外的核验已全部完成。

## 5. 实测实验记录（全部免认证，2026-10-26）

工具：`codex debug prompt-input "<prompt>"`（渲染模型可见输入 JSON，
不调用模型）。二进制：codex-cli 0.164.0（npm）。

1. **默认 home 扫描根**（默认 `~/.codex`，项目 `/tmp/x`）：
   `r0=~/.codex/skills`、`r1=~/.agents/skills`、`r2=~/.codex/skills/.system`、
   `r3/r4/r5=~/.codex/plugins/cache/*`（插件技能）。既有 Claude 格式技能
   （gstack-qa、human-writing 等）原样出现在清单。
2. **项目级技能**：项目放 `.agents/skills/task10-probe/SKILL.md` 后，
   根表新增 `r6=/private/tmp/x/.agents/skills`，清单出现
   `task10-probe: Project-level probe skill ... (file: r6/task10-probe/SKILL.md)`。
3. **项目 AGENTS.md**：项目根 `AGENTS.md`（含 marker 字符串）被注入，
   头部 `# AGENTS.md instructions for /private/tmp/x`，全局与项目内容
   同块、`--- project-doc ---` 分隔。
4. **CLAUDE.md**：默认不注入（marker 0 命中）；加
   `-c project_doc_fallback_filenames=["CLAUDE.md"]` 后注入命中。
5. **全新 CODEX_HOME**（`CODEX_HOME=/tmp/fresh`）：首跑自动落盘
   `.system` 内置技能；根表 = `~/.agents/skills` + `$CODEX_HOME/skills/.system`
   + 项目 `.agents/skills` —— 证明 USER 作用域独立于 CODEX_HOME 存在，
   新用户开箱即扫这三个位置。
6. `codex --help` / `features list` / `doctor` / `plugin --help` 输出
   存档于任务报告；无 `codex skills` 子命令（技能管理走会话内
   `$skill-creator`/`$skill-installer` 与文件系统）。

## 6. 对后续任务的直接指令

- **Task 11（convert.sh --codex）**：复制 SKILL.md 目录树到
  `dist/codex/<skill-name>/`，不生成 AGENTS.md 包装；沿用官方目录约定
  （SKILL.md + scripts/ + references/ + assets/，可选 agents/openai.yaml）。
- **Task 12（install.sh）**：默认全局装 `~/.codex/skills/`（官方安装器
  事实目标），可选 `--user-agents` 装 `~/.agents/skills/`（跨 agent 共享）、
  `--project` 装 `<repo>/.agents/skills/`；支持符号链接模式。
- **Task 13（检测标志物）**：agent 检测"`~/.codex` 存在 → codex"仍然
  有效，更稳的是 `command -v codex`；skills 安装位检测
  `~/.codex/skills` 与 `~/.agents/skills` 两处。
- **Task 14（验收）**：免认证用 `codex debug prompt-input` 断言技能在
  清单；端到端调用待主人 `codex login`（或 API key / 本地 ollama）。

## 参考

- Skills（官方，canonical）：https://learn.chatgpt.com/docs/build-skills
  （同内容 https://developers.openai.com/codex/skills）
- AGENTS.md（官方，canonical）：
  https://learn.chatgpt.com/docs/agent-configuration/agents-md
- Authentication（官方）：https://learn.chatgpt.com/docs/auth
- 开放技能标准：https://agentskills.io ；官方技能仓库
  https://github.com/openai/skills （`.curated`/`.experimental`/`.system`）
- 本机实测材料：`codex --version`=codex-cli 0.164.0；
  `$CODEX_HOME/skills/.system/skill-installer/SKILL.md`（安装器行为）；
  `codex debug prompt-input` 六组实验（§5）
