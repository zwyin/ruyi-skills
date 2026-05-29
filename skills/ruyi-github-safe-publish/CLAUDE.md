# github-safe-publish

## 推送命令

本地代理拦截 HTTPS（端口 443），需显式绕过：

```bash
git -c http.proxy="" -c https.proxy="" push github master
```

SSH 密钥绑定 `openclaw-jarvis-lab` 账户，无法推送到 `zwyin/` 仓库。使用 gh CLI 的 OAuth token（`gh auth setup-git`）+ 上述绕过代理方式推送。

### 唯一版本源

版本号定义在 `skills/ruyi-github-safe-publish/SKILL.md` frontmatter 的 `version` 字段。

### 版本号出现位置（6 处）

| # | 文件 | 位置 | 说明 |
|---|------|------|------|
| 1 | `skills/ruyi-github-safe-publish/SKILL.md` | frontmatter `version: "X.Y.Z"` | **唯一版本源** |
| 2 | `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` | |
| 3 | `.claude-plugin/marketplace.json` | `"version": "X.Y.Z"` | |
| 4 | `README.md` | version badge URL | |
| 5 | `CHANGELOG.md` | 版本标题 | |
| 6 | `scripts/release.sh` | 读取并同步 | |

所有 6 处位置均已存在。

## 测试

```bash
pytest tests/ -q
pytest tests/ --cov=tests --cov-report=term-missing -q
scripts/validate_skill.sh
```

### 覆盖率目标

| 层 | 目标 | 当前 |
|----|------|------|
| Tests 总体 | ≥ 95% | 99% |
| test_skill_structure | ≥ 90% | 100% |
| test_scanning_rules | ≥ 90% | 97% |
| test_detection | ≥ 95% | 100% |
| test_convert | ≥ 90% | 100% |
| test_plugin_metadata | ≥ 90% | 100% |
| test_conftest | ≥ 90% | 100% |
| test_entropy | ≥ 90% | 100% |

### 规则检测覆盖

134/135 scanning rules 有端到端检测测试（唯一未覆盖：`large-file-in-history`，基于文件大小阈值无正则）。
检测测试使用 `_detects()` 和 `_detects_file()` 从 `docs/scanning-rules.md` 提取正则并验证。

## 项目结构要点

- **SKILL.md 是唯一事实源**：所有扫描规则、步骤流程、修复逻辑都定义在 `skills/ruyi-github-safe-publish/SKILL.md` 中
- **scanning-rules.md 是规则参考**：`docs/scanning-rules.md` 是第 1 层规则的完整正则定义，供维护者参考，SKILL.md 引用但不重复全部正则
- **convert.sh 多平台转换**：`scripts/convert.sh` 将 SKILL.md 转换为 Cursor (.mdc)、Windsurf (.windsurfrules)、OpenCode (AGENTS.md) 格式，输出到 `dist/`
- **已发布**：https://github.com/zwyin/github-safe-publish
