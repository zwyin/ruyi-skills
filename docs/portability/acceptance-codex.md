# Codex CLI 真实验收记录（Task 14）

> 验收对象：ruyi-skills v0.10.0 候选（feat/portability-p1 @ e345b7b + 本文档 commit）
> 的 Codex 分发通道（install.sh `--agent codex`）。
> 环境：macOS 15.7.3 (aarch64)，codex-cli 0.164.0（npm 全局），
> 默认 `CODEX_HOME=~/.codex`。验收日期：2026-10-26。
> 路径与格式依据：[codex.md](codex.md)（Task 10 核验）。

## 结论速览

| 步骤 | 结果 | 认证需求 |
|---|---|---|
| 1. 安装（install.sh --agent codex） | ✅ 三技能全部装入 `~/.codex/skills/` | 无 |
| 2. 技能发现（skills_instructions 注入） | ✅ 三技能全部在清单，英文 description 生效 | 无 |
| 3. 端到端模型调用（safe-publish dry-run） | ⏸ **pending-auth**：ChatGPT 凭据为空壳，需主人交互式 `codex login` | 需要 |

## 1. 安装（install.sh --agent codex）✅

命令与完整输出：

```console
$ bash scripts/install.sh --agent codex
installed: codex/ruyi-github-safe-publish
cp: .../skills/ruyi-project-walkthrough/.codegraph/daemon.sock is a socket (not copied).
installed: codex/ruyi-project-walkthrough
installed: codex/ruyi-version-check
```

- 三技能全部 `installed:`（幂等重跑应得 `skip (up-to-date):`，marker 文件
  `.ruyi-install` 随目录写入）。
- `daemon.sock` 警告来自源目录中一个活跃的 CodeGraph 守护进程 socket：
  `cp -R` 自身跳过 socket 文件后继续，且 `.codegraph/` 在排除清单中，
  最终安装产物验证无任何 `.codegraph` 残留（见下）。**非缺陷**，但
  install.sh 后续可在复制前 prune 以消除该噪音行（记录，不在本次范围）。

安装产物抽查（`ls ~/.codex/skills/ruyi-*`）：

```
/Users/zhiweiyin/.codex/skills/ruyi-github-safe-publish/{SKILL.md,skills/,scripts/,docs/,LICENSE,CHANGELOG.md,...,.ruyi-install}
/Users/zhiweiyin/.codex/skills/ruyi-project-walkthrough/{SKILL.md,skills/,scripts/,docs/,...,.ruyi-install}
/Users/zhiweiyin/.codex/skills/ruyi-version-check/{SKILL.md,skills/,scripts/,...,.ruyi-install}
$ find ~/.codex/skills -name ".codegraph" -o -name "daemon.sock"   # 零命中
```

## 2. 技能发现（免认证）✅

验证命令（Task 10 核验的免认证通道，渲染模型可见输入、不调用模型）：

```console
$ codex debug prompt-input "hi" 2>/dev/null | grep -c ruyi-
2   # 整个 <skills_instructions> 块在 JSON 单行内，行数≠技能数；逐技能断言见下
```

`<skills_instructions>` 中三技能全部在列（skills 根表 `r0` = `/Users/zhiweiyin/.codex/skills`，
即 install.sh 的目标路径；`r1` = `~/.agents/skills` 为本机既有的旧版手工安装，
description 仍是中文旧版——正好形成对照，证明本次 r0 注入的是新版英文行）：

```text
- ruyi-github-safe-publish:ruyi-github-safe-publish: Safely publish a local Git project to a p (file: r0/ruyi-github-safe-publish/skills/ruyi-github-safe-publish/SKILL.md)
- ruyi-project-walkthrough:ruyi-project-walkthrough: Generate a structured walkthrough of any  (file: r0/ruyi-project-walkthrough/skills/ruyi-project-walkthrough/SKILL.md)
- ruyi-version-check:ruyi-version-check: Check version consistency across a skill  (file: r0/ruyi-version-check/skills/ruyi-version-check/SKILL.md)
```

要点：

- **Phase 1 的英文 Use-when 触发行在 Codex 发现清单中生效**（r0 行均为英文
  description 截断；r1 旧拷贝仍是中文，同屏对照）。
- Codex 对合集布局取的是**嵌套内层** `skills/<name>/skills/<name>/SKILL.md`
  （marketplace 布局的内层副本），install.sh 保留嵌套结构的决定被验证正确。

## 3. 端到端模型调用（safe-publish dry-run）⏸ pending-auth

测试仓库（已按计划植入假 AWS key）：

```console
$ cd /tmp/ruyi-codex-accept
$ echo "aws_access_key_id = AKIAIOSFODNN7EXAMPLE" > creds.txt   # AWS 官方文档示例 key
$ git init && git add -A && git commit -m init                   # 5041d63
```

两次非交互尝试（沙箱 read-only，直连与代理环境各一次）：

```console
$ codex exec --sandbox read-only "Use the ruyi-github-safe-publish skill to run a dry-run ..."
ERROR: Reconnecting... 1/5 ... 5/5
warning: Falling back from WebSockets to HTTPS transport. plan type is required for chatgpt authentication
ERROR: plan type is required for chatgpt authentication
# 代理环境下另有决定性证据：
ERROR codex_models_manager::manager: failed to refresh available models:
  unexpected status 401 Unauthorized: {"detail":"Unauthorized"},
  url: https://chatgpt.com/backend-api/codex/models?client_version=0.164.0
```

归因（网络 vs 认证）：

- 网络侧排除：代理开启时请求可达 ChatGPT 后端并得到明确 `401 Unauthorized`
  （cf-ray 在案）；`chatgpt.com` 经 `127.0.0.1:7897` 可达（HEAD 得
  Cloudflare 403 应答）。连接抖动只影响重连节奏，不是失败根因。
- 认证侧实锤：`~/.codex/auth.json` 仅 2 字节（`{}` 空壳，7 月桌面端集成残留，
  见 codex.md §4）；`codex login status` 报 "Logged in using ChatGPT" 属
  **误报**（不校验凭据完整性）。`codex doctor` 的
  "stored credentials are incomplete" 才是真实状态。

### 主人需执行的解锁命令（交互式，不可代办）

```bash
codex login          # 浏览器 OAuth（localhost:1455 回调），需主人本人点击授权
```

备选（无浏览器环境）：`codex login --device-auth`（设备码，beta）；
CI/脚本化：`printenv OPENAI_API_KEY | codex login --with-api-key`。

登录完成后重跑本节命令即可补齐端到端证据；预期路径：Codex 按
skills_instructions 选中 ruyi-github-safe-publish → 读取
`r0/ruyi-github-safe-publish/skills/ruyi-github-safe-publish/SKILL.md` →
执行确定性扫描 → 报告 `creds.txt` 命中 AWS Access Key（规则
`aws-access-key-id`）。该补验不阻塞 v0.10.0 发版：安装与发现两级证据
已覆盖"分发通道可用"的主张，模型调用属账号侧前置条件。

## 4. 与 README 安装矩阵的一致性

- README 矩阵 Codex 行给出的安装命令即本文件 §1 所用
  `bash scripts/install.sh --agent codex`，验证一致。
- 免认证验证命令与 codex.md §3 "验证命令"一致，第二来源复验通过。
