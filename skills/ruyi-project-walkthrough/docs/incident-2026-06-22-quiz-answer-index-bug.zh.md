# 事故报告 2026-06-22：测验答案索引总是塌成选项 A

**Bug：** `md_to_html.py` 的 `parse_quiz_md` 用 `re.search(r'([A-D])', line)` 提取答案字母，结果匹配到单词 "Answer" 里的字面量 `A`，而不是真正的答案字母。无论正确答案实际是哪个，每道测验题的正确答案索引都塌成了 `0`（选项 A）—— 选 A 永远被判正确，选真正答案反而被判错。

**影响：** 自 2026-05-27（commit `ca1f371`）起，所有用 `--quiz-chapter` 生成、且落在 `repo_ds1600` 下的 11 份报告，测验答案全部错误。修复过程中又发现两个相关问题：(1) `check_update.sh` 缓存逻辑会让用户升级插件后立刻看到一条方向反的"有新版本"假提示（同根因：过期 SHA 比对）；(2) `parse_quiz_md` 把题间分隔符 `---` 拼到了上一题的解释文本里。

**修复策略：** `parse_quiz_md` 改一行正则锚定 + 解释收集遇到 `---` 提前停止。沿四条传播渠道依次推进（开发仓 → 通过 `brand-sync-tool` 同步品牌仓 → 本机 Claude Code 插件 `/plugin` 更新 → 本机 agents 直接复制）。原 `release.sh` 在合集架构下不可用（旧架构假设 + 要求 develop 分支），改用手动 7 处版本号 bump。每次修复独立发版（v0.9.1/2/3），让用户能增量更新。

**纵深防御：** 新增 `tests/test_quiz_parsing.py`，覆盖所有答案字母（A/B/C/D）、中文冒号、混合答案。现有 `test_html_quiz_answer_index_valid` 只查 `0 ≤ c < len(opts)` 形态——这正是漏掉此 bug 的原因，应改成"对照源 markdown 字母"的交叉检查。`parse_quiz_md` 用锚定正则，从结构上杜绝字母误匹配。

**端到端独立验证：** 每个传播步骤都做真实源 vs 真实 HTML 的 c 值比对（不是只看形状）。

---

## 1. 背景与范围

### 1.1 `parse_quiz_md` 是什么

`scripts/md_to_html.py` 的 `parse_quiz_md` 解析 walkthrough 章节 markdown 中的 `## Quiz` 段（按 SKILL.md L541-572 规范）。输出是嵌入 HTML 的 `quizData` JS 数组——每项 `{q, o, c, e}` 对应题文、选项、正确索引、解释。HTML 交互组件把 `o[c]` 高亮为正确选项。

```python
def parse_quiz_md(quiz_md):
    ...
    for line in lines:
        opt_match = re.match(r'^(?:[-*]\s+)?([A-D])[.)]\s+(.*)', line)
        if opt_match and state in ("question", "options"):
            state = "options"
            opts.append(opt_match.group(2))
        elif re.match(r'^\*\*Answer\s*[：:]\s*[A-D]\s*\*\*', line, re.IGNORECASE):
            # FIXED: 锚定字母搜索
            m = re.search(r'[：:]\s*([A-D])\s*\*\*', line, re.IGNORECASE)
            if m: answer = m.group(1).upper()
            state = "answer"
        elif re.match(r'^\*\*Explanation\s*[：:]', line, re.IGNORECASE):
            ...
```

### 1.2 怎么坏的

原来的答案提取是一对语句：

```python
elif re.match(r'^\*\*Answer\s*[：:]\s*[A-D]\s*\*\*', line, re.IGNORECASE):
    m = re.search(r'([A-D])', line, re.IGNORECASE)   # ← bug
    if m: answer = m.group(1).upper()
    state = "answer"
```

`re.match(...)` 确实正确卡住了 `**Answer: X**` 的形状，但接下来的 `re.search(r'([A-D])', line)` 是**扫整行**找第一个 A-D 字母。任何 `**Answer: B**` 形状的行，第一个 A-D 字母是单词 "Answer" 里的 `A`（位置 2），不是真正的答案字母（位置 10+）。所以 `answer` 永远是 `"A"`，`correct = ord('A') - ord('A') = 0`。

这个 bug 由 commit `ca1f371`（2026-05-27）引入。从那以后所有用 `--quiz-chapter` 生成的报告，每道题的 `c` 都是 0。

### 1.3 为什么测试没拦住

`tests/test_walkthrough_output.py::test_html_quiz_answer_index_valid` 只断言：

```python
if not isinstance(correct, int) or correct < 0 or correct >= len(opts):
    errors.append(...)
```

它检查答案索引的**形状**（`0 ≤ c < len(opts)`），但从不**交叉核对** `c` 是否对应源 markdown 里的 `**Answer: X**` 字母。因为 `c=0` 永远成立，形状测试永远通过。

`tests/fixtures/*/interactive/walkthrough.html` 这 3 个测试 fixture 在 `--quiz-chapter` 出现之前就建好了（旧版基于 DOM 拼装），没有一个跑过 `parse_quiz_md`。**对 `parse_quiz_md` 的直接单元测试覆盖率为 0**。

### 1.4 用户复现

用户给 `repo_ds1600/github_individual_follow_naizhao/...deep-zh-general` 生成了 walkthrough。测验 Q1："这个项目的核心数据管线顺序是？" 正确答案应该是 B（解释文本："配置定义目标→采集器抓数据→存到 data→分析器处理→生成报告"）。选 B 报错，选 A 显示正确。用户 2026-06-22 上报，触发本次事故。

---

## 2. 根因（一句话）

`parse_quiz_md` 里的 `re.search(r'([A-D])', line)` 没有锚定到答案字母的位置——它匹配了单词 "Answer" 里的 `A`，导致所有测验题的正确答案索引都塌成 0。

---

## 3. 修复

### 3.1 代码改动（1 行正则）

**文件：** `skills/ruyi-project-walkthrough/scripts/md_to_html.py` L247

**改前：**
```python
m = re.search(r'([A-D])', line, re.IGNORECASE)
```

**改后：**
```python
# 把字母搜索锚定在"冒号后、收尾 ** 前"，才能取到真正的答案字母，
# 而不是 "Answer" 这个单词里的 'A'。原 re.search(r'([A-D])', ...)
# 在整行扫描永远先匹配那个 'A' → 不论真答案是什么，c 都塌成 0。
m = re.search(r'[：:]\s*([A-D])\s*\*\*', line, re.IGNORECASE)
```

替换的正则 `r'[：:]\s*([A-D])\s*\*\*'` 把搜索区间卡在冒号（`: / ：`）和收尾 `**` 之间。只有当字母被这两个标记夹着时才会匹配——不会被 "Answer" 里的 `A` 骗。

### 3.2 附带修复：解释吞 `---`

审计 `parse_quiz_md` 其他分支时，发现解释收集器把题间分隔符 `---` 拼进了上一题的解释文本（HTML 里能看到每条解释末尾都带个 ` ---`）。

**文件：** `skills/ruyi-project-walkthrough/scripts/md_to_html.py` L253-254

```python
elif state == "explanation":
    # `---` 是题间分隔符；停止收集，避免被拼进解释文本
    if line.strip() == "---":
        break
    explanation += " " + line
```

### 3.3 测试覆盖

**新增文件：** `skills/ruyi-project-walkthrough/tests/test_quiz_parsing.py` — 7 个用例：
- `test_answer_b_yields_index_1`（核心回归）
- `test_answer_a_yields_index_0`（碰巧掩盖 bug 的那条）
- `test_answer_c_yields_index_2`
- `test_answer_d_yields_index_3`
- `test_answer_with_chinese_colon`（`**Answer：C**`）
- `test_mixed_answers_across_questions`（真实场景：B/D/A/C 混合）
- `test_explanation_and_question_preserved`

改前：6 fail / 1 pass（只有 A 那条碰巧通过）。改后：7 pass。

---

## 4. 关联发现：`check_update.sh` 缓存假提示

v0.9.2 加的 SessionStart hook（见 §5.2）让 `scripts/check_update.sh` 一个潜在的旧 bug 变得可见。症状：刚跑完 `claude plugin update ruyi-skills@ruyi-skills`，下一次 SessionStart 立刻弹一条假的"🔄 有新版本可用（新本地 → 旧缓存远程）"，方向反。

**根因：** `check_update.sh` L48-56 只要 `remoteSha ≠ LOCAL_SHA` 就 replay 缓存的 remoteSha，没意识到 `LOCAL_SHA` 本身可能已经变了（即用户升级了）。

**修复：** 缓存多存一个 `localShaAtCheck`。只有当当前 `LOCAL_SHA == localShaAtCheck` 时才 replay。如果两者不等（用户中途升级过），缓存视为过期 → 脚本重新查远程而不是反方向 replay。向后兼容（旧缓存没有这个字段→视为过期→重新查）。

---

## 5. 传播链

开发仓修好后，必须到达 4 个下游渠道。每步都验证后才推进下一步。

### 5.1 渠道 A：`repo_ds1600` 下受影响的 11 份报告

用户最初只要"排查"，不要重生。排查结论：`repo_ds1600` 下 11 份报告每道题 `c=0`（`article_archieve_claude` ×7、`github_individual_follow_naizhao` ×1、`claude-md-manager` ×1、`gz-ai-chat-eval-toolkit` ×1、`llm-benchmark-claude` ×1）。

用户后来授权重生。11 份都用修复后的 converter 重生。每份安全模式：备份 `.bak` → 重生（覆盖）→ 验证 c 值 == markdown 答案字母 + `verify-result.json` 通过 → 删除 `.bak` 或回滚。**11/11 成功，零回滚。**

### 5.2 渠道 B：品牌仓（paoding / davinci / doraemon）

用户要求："确保所有直接安装者体验一致" → 修复必须落到品牌仓（不只是 ruyi）。

**发现：** `md_to_html.py` 全盘共 **17 份**。只有 1 份（开发仓）已修；其余 15 份（品牌仓通过 brand-sync、本机装的 Claude Code 插件、本机装的 agents）都带同样的源码 bug。

**brand-sync 机制：** `brand-sync-tool/sync.sh` 从 `ruyi-skills` rsync 到每个品牌的 `output/{brand}/`（再推到该品牌的 GitHub 仓）。L96 `RSYNC_EXCLUDES` 不排除 `scripts/`，所以 `scripts/md_to_html.py` 会被传播。L264-273 Step 9a 会对 `scripts/check_update.sh` 做品牌名替换（`REPO=` 和 `PLUGIN_KEY=`）。

**本地验证：** `bash sync.sh --dry-run` 三品牌 11/11 传播成功（paoding `d24de66`、davinci `59140fe`、doraemon `1256a10`，每个都是 `sync: update from ruyi-skills @ fb5b066`）。

**推送：** 去掉 `--dry-run` 重跑，网络失败时重试。**paoding `43816c0`、davinci `697a42c`、doraemon `76acef2`** 全部推到 `zwyin/{brand}-skills.git`。每个 `sync: update from ruyi-skills @ b204bd4`（之后是 `181ca23`）。

### 5.3 渠道 C：本机 Claude Code 插件

`~/.claude/plugins/marketplaces/ruyi-skills` 是 `zwyin/ruyi-skills` 的 git clone。用户跑 `/plugin` 重装 → cache 更新到 `b204bd4`（v0.9.2）再到 `181ca23`（v0.9.3）。验证：`installed_plugins.json` 的 `gitCommitSha` = 最新，`hooks/session-start` 每次 SessionStart 运行，输出合法 JSON `additionalContext`。

### 5.4 渠道 D：本机 agents 技能（`~/.agents/skills/{4品牌}`）

`~/.agents/skills/` 下 4 份品牌 walkthrough 技能副本还是 BUG 版本。通过 `_agents.mount_config: /mnt/host/.../.agents:/mnt/.agents` 挂到 agent 容器里——没 git、没安装脚本（大概是手动复制的）。没有插件管理命令。

**更新方式：** `md_to_html.py` 含品牌字符串（`tool_name` / `tool_url` 默认值，每个品牌差 6 行）。不能直接复用 ruyi 版本——必须从各品牌的 sync output 复制。从 `brand-sync-tool/output/{brand}/skills/{brand}-project-walkthrough/scripts/md_to_html.py`（v0.9.3、品牌已替换、测验已修）→ `~/.agents/skills/{brand}-project-walkthrough/scripts/md_to_html.py`。**4/4 更新完成；品牌字符串保留；测验修复。**

### 5.5 渠道 E：死残留清理

全盘扫描 18 份 `md_to_html.py`。完成上述四条传播后：
- **10 份已修**（所有运行时路径）
- **8 份仍 BUG**，分类如下：

| 类型 | 数量 | 处理 |
|------|------|------|
| 旧插件 cache（`a44ad7433343`、`fcaedc33cf26`） | 2 | 死残留——`installed_plugins` 指向 `b204bd4`。**已删**（careful `rm`）。 |
| 已归档 marketplace（`project-walkthrough-skill`） | 1 | 死残留——未安装，但注册在 `~/.claude/plugins/known_marketplaces.json`。**移除注册条目 + `rm` 目录**。 |
| `4_compare/{4品牌}/`（品牌输出对比快照） | 4 | **有意保留**——用户对比品牌输出的参照，更新会破坏用途。 |
| `~/repo_skillforge/project-walkthrough-skill/` | 1 | **有意保留**——归档的合集前源仓，不维护。 |

用户通过 AskUserQuestion 明确授权清理 3 个死残留（vs 保留）。清理后：磁盘上 5 份 BUG 版本副本全部带"有意保留"标签。**没有任何运行时可达的 BUG 副本。**

---

## 6. 版本与发版

### 6.1 为什么一天发三轮

每个版本解决独立问题，用户能增量更新，不必等打包大版本：

| 版本 | 日期 | Skill | 合集 | 内容 |
|------|------|-------|------|------|
| v0.9.1 | 2026-06-22 | 1.6.1→1.6.2 | 0.9.0→0.9.1 | 测验答案索引修复（PR#10）|
| v0.9.2 | 2026-06-22 | 1.6.2→1.6.3 | 0.9.1→0.9.2 | SessionStart 自动更新检查 hook |
| v0.9.3 | 2026-06-22 | 1.6.3→1.6.4 | 0.9.2→0.9.3 | `check_update.sh` 缓存假提示修复 |

### 6.2 `release.sh` 在合集架构下坏掉了

`skills/ruyi-project-walkthrough/scripts/release.sh`（为合集前布局设计）算出 `ROOT = scripts/..` 然后相对 `ROOT` 读 `skills/ruyi-project-walkthrough/SKILL.md`。在当前 ruyi-skills 合集布局下解析成 `skills/ruyi-project-walkthrough/skills/ruyi-project-walkthrough/SKILL.md`（不存在）。它还卡 `branch == develop`（我们在 main）。

**三轮都用的临时方案：** 手动 7 处版本号 bump + `bash scripts/convert.sh --all && --check` + `pytest tests/` + commit + push + tag。`test_lang_output.py` 的断言是动态的（读 SKILL.md frontmatter），所以 bump 后自动跟——不用改测试。

修 `release.sh` 本身（或新写 `release-collection.sh`）**不在本次事故范围**，留作后续。

### 6.3 发版产物位置

4 个仓库（ruyi-skills + 3 品牌仓）每轮都在 `main` + git tag `v0.9.X` 上收到：

| 仓库 | v0.9.1 commit | v0.9.2 commit | v0.9.3 commit |
|------|---------------|---------------|---------------|
| ruyi-skills | `fb5b066` | `b204bd4` | `181ca23` |
| paoding-skills | `a4e99d7` | `43816c0` | `67b9ff3` |
| davinci-skills | `c8ae722` | `697a42c` | `eadfc74` |
| doraemon-skills | `256c5a5` | `76acef2` | `9d3a9f4` |

所有 commit 在 `main`。所有 tag 已推。

---

## 7. 验证矩阵

| 验证项 | 结果 |
|--------|------|
| 单元测试（`tests/test_quiz_parsing.py`） | 7/7 通过 |
| skill 完整测试（`pytest tests/`） | 292 pass, 23 skipped（无回归）|
| 合集根测试（`pytest tests/`） | 18/18 通过 |
| 本地 `make ci` | 通过 |
| `bash scripts/convert.sh --check` | ✓ 两个 skill |
| `python3 scripts/check_self_contained.py` | OK |
| marketplace.json 合法性 | OK |
| PR#10 CI（7 个 job，macOS/Ubuntu/Python 3.10/3.12） | 全部 SUCCESS |
| 真实测验源端到端（naizhao 16 题）| c 值序列 `[B,C,A,B,B,A,C,B,B,C,B,B,C,B,B,B]` 与 markdown 真值完全一致 |
| brand-sync --dry-run 三品牌 | hooks 已传播；`check_update.sh` REPO/PLUGIN_KEY 品牌替换正确 |
| `hooks/session-start` JSON 输出 | 合法 JSON；仅在有更新时填充 `additionalContext` |
| 清理后全盘扫描 | 10 已修 + 5 有意保留（零运行时可达 BUG 副本）|

---

## 8. 纵深防御

同形态的未来回归被三层挡住：

1. **直接单元测试：** `test_quiz_parsing.py` 覆盖所有 4 个答案字母 + 中文冒号 + 多题场景。改前：6/7 fail。改后：7/7 pass。
2. **锚定正则：** 修复把提取正则从 `re.search(r'([A-D])', line)` 改成 `re.search(r'[：:]\s*([A-D])\s*\*\*', line)`。新模式**强制**字母必须在冒号和收尾 `**` 之间——不会被 "Answer" 里的 `A` 骗。未来若有人手贱去掉锚定，单元测试会立刻拦住。
3. **流程层面：** 现有 `test_html_quiz_answer_index_valid` 只查形状（`0 ≤ c < len(opts)`）——这正是本次 bug 上线的原因。建议后续加固：改成对照源 markdown `**Answer: X**` 字母做交叉核对（不是只看形状）。这是原始缺口。

---

## 9. 明确没做的事（及原因）

- **4_compare 和 archived 源 `md_to_html.py`** — 用户确认是有意保留的参照（品牌对比 / 归档历史）。更新会破坏用途。已在 `memory/quiz-bug-regen-followup.md` 标注为"有意保留"。
- **修 `release.sh` 本身** — 在合集架构下坏掉，但修它是独立重构，不在本事故范围。手动 7 处 bump 能用但脆弱。建议作为后续 issue。
- **用户本机 `v0.9.2 → v0.9.3` 的 `/plugin update`** — 用户管理；agent 侧无法自动。用户已收到通知。
- **agents 技能的 `SKILL.md` 版本号 + `check_update.sh` 缓存修复传播** — 优先级低；agent 容器不一定执行。出测验答案正确性的事故范围。

---

## 10. 时间线（2026-06-22）

- **用户上报** Bug（naizhao walkthrough，Q1 测验答案错）。
- **根因定位** `md_to_html.py:247`（正则锚错位置）。
- **PR#10** 提交（`fb5b066`），CI 全绿，合并。
- **`repo_ds1600` 11 份受影响报告重生**。
- **四条传播渠道完成**：开发仓 → brand-sync → Claude Code 插件 → agents。
- **v0.9.1 / v0.9.2 / v0.9.3** 发到 4 个仓库。
- **3 个死残留清理**（旧 cache + archived marketplace）。
- **最终全盘扫描：** 10 已修 + 5 有意保留（零运行时可达 BUG 副本）。
- **总耗时：** 一个工作日。

---

## 11. 交叉引用

- PR：[#10](https://github.com/zwyin/ruyi-skills/pull/10) — `fix(walkthrough): quiz correct-answer index always collapsed to option A`
- Commit：`fb5b066`（v0.9.1 根修复）
- CHANGELOG：`skills/ruyi-project-walkthrough/CHANGELOG.md` 中 `[1.6.2]`、`[1.6.3]`、`[1.6.4]` 三条
- 测试文件（新增）：`skills/ruyi-project-walkthrough/tests/test_quiz_parsing.py`
- 同类文档参考：`docs/fix-proposal-empty-html.md`（结构相似：bug → 根因 → 修复策略 → 纵深防御）
- SessionStart hook 机制：`~/.claude/plugins/marketplaces/ruyi-skills/skills/ruyi-project-walkthrough/hooks/hooks.json` + `hooks/session-start`
- 跨会话 memory：`memory/quiz-bug-regen-followup.md`、`memory/ruyi-skills-update-check-hook.md`

---

## 12. 英文版

本文档的英文版见同目录 `incident-2026-06-22-quiz-answer-index-bug.md`（英文为原本，中文为翻译版，结构与内容一一对应）。
