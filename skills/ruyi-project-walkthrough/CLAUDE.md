# project-walkthrough-skill

## 版本管理

### 唯一版本源

版本号定义在 `skills/ruyi-project-walkthrough/SKILL.md` frontmatter 的 `version` 字段。**所有其他位置的版本号必须从这里同步，不允许手动分别修改。**

### 版本号出现位置（6 处）

| # | 文件 | 位置 | 说明 |
|---|------|------|------|
| 1 | `skills/ruyi-project-walkthrough/SKILL.md` | frontmatter `version: "X.Y.Z"` | **唯一版本源**，手动修改 |
| 2 | `skills/ruyi-project-walkthrough/SKILL.md` | `--version` flag 文档 + Phase 0 启动横幅 | `ruyi-project-walkthrough vX.Y.Z`（2 处）、`> **Version X.Y.Z**`（1 处，Phase 0 横幅） |
| 3 | `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` | Claude Code 插件元数据 |
| 4 | `.claude-plugin/marketplace.json` | `"version": "X.Y.Z"` | Marketplace 注册信息 |
| 5 | `README.md` | version badge URL | `badge/version-X.Y.Z-blue` |
| 6 | `CHANGELOG.md` | 版本标题 | `## [X.Y.Z] - YYYY-MM-DD` |

### 发版流程

1. **修改版本源**：编辑 `skills/ruyi-project-walkthrough/SKILL.md` frontmatter 的 `version` 字段
2. **运行 `scripts/release.sh X.Y.Z --bump-only`**：自动同步位置 1-6（从 SKILL.md frontmatter 读取当前版本，写入新版本到全部 6 处）
3. **手动更新 CHANGELOG.md 内容**—— `release.sh` 只创建标题，不写变更内容
4. **同步平台文件**：`bash scripts/convert.sh`
5. **更新测试中的版本断言**：`tests/test_lang_output.py` 中有两处硬编码版本号
6. **运行测试**：`pytest tests/ -q`
7. **提交并推送 develop，创建 PR 到 master**

### 当前已知限制

- 用户无法自动更新已安装的插件，需要重新安装（`/plugin install`）或 `git pull`
- `--version` 输出是硬编码字符串，不是从 plugin.json 动态读取
- `release.sh --bump-only` 的 sed 模式（`project-walkthrough v` / `Project Walkthrough v`）匹配不到 Phase 0 横幅（格式为 `> **Version X.Y.Z**`，无 `v` 前缀）→ 横幅需手动同步，或后续扩展 release.sh 增加 `Version X.Y.Z` 模式

### 版本同步检查清单

每次修改版本号后，必须验证以下命令输出一致：

```bash
# 位置 1: SKILL.md frontmatter
grep '^version:' skills/ruyi-project-walkthrough/SKILL.md

# 位置 2: --version 输出文本（2处）
grep 'ruyi-project-walkthrough v' skills/ruyi-project-walkthrough/SKILL.md

# 位置 2b: Phase 0 启动横幅（1处）
grep '> \*\*Version' skills/ruyi-project-walkthrough/SKILL.md

# 位置 3: plugin.json
grep '"version"' .claude-plugin/plugin.json

# 位置 4: marketplace.json
grep '"version"' .claude-plugin/marketplace.json

# 位置 5: README badge
grep 'badge/version-' README.md

# 位置 6: CHANGELOG
head -5 CHANGELOG.md
```

所有 6 处的版本号必须一致。

## 项目结构要点

- **SKILL.md 是单一事实源**：`skills/ruyi-project-walkthrough/SKILL.md` 是所有平台文件的源头
- **平台文件由 convert.sh 生成**：`cursor/`、`.windsurf/`、`.opencode/` 下的文件不要手动编辑，改完 SKILL.md 后运行 `bash scripts/convert.sh`
- **HTML 转换器**：`scripts/md_to_html.py` 是所有深度级别的 HTML 生成器，支持 `--lang`、`--quiz-chapter`、`--verify`
- **验证结果文件**：converter 自动在 HTML 同目录生成 `verify-result.json`，Phase 5 交付门禁必须读取该文件作为质量证据

## 网络问题

GitHub HTTPS（port 443）经常超时。替代方案：
- 用 `gh api` Contents API 逐文件推送（需要 base64 编码）
- 推完后 `git fetch origin master && git reset --hard origin/master` 同步本地
- SSH 走本地代理也可能失败，Contents API 更稳定

## 测试

```bash
pytest tests/ -q           # 快速验证
make ci                    # 完整 CI（pytest + convert.sh --check）
```
