# 08 发布自动化：release.sh 与版本管理

## 版本同步问题

project-walkthrough 的版本号出现在 6 个位置。手动维护容易遗漏或导致不一致。`scripts/release.sh`（166 行）自动化了这个过程。

## 版本号的 6 个位置

| # | 文件 | 位置 | 说明 |
|---|------|------|------|
| 1 | `SKILL.md` | frontmatter `version: "X.Y.Z"` | **唯一版本源**，手动修改 |
| 2 | `SKILL.md` | `--version` 输出文本 | 2 处 `project-walkthrough vX.Y.Z` |
| 3 | `plugin.json` | `"version": "X.Y.Z"` | Claude Code 插件元数据 |
| 4 | `marketplace.json` | `"version": "X.Y.Z"` | Marketplace 注册信息 |
| 5 | `README.md` | version badge URL | `badge/version-X.Y.Z-blue` |
| 6 | `CHANGELOG.md` | 版本标题 | `## [X.Y.Z] - YYYY-MM-DD` |

## release.sh 工作流

### 用法

```bash
# 完整发布（bump + PR + CI + merge + tag）
./scripts/release.sh 1.7.0

# 只更新版本号，不推送
./scripts/release.sh 1.7.0 --bump-only

# 验证不执行
./scripts/release.sh 1.7.0 --dry-run
```

### 完整发布流程

```
验证版本格式 (semver)
    │
    ▼
检查分支 (必须在 develop) + 工作区干净
    │
    ▼
运行 CI (make ci)
    │
    ▼
更新 6 处版本号 (sed)
    │
    ▼
提交 "chore: bump version to X.Y.Z"
    │
    ▼
推送到 develop
    │
    ▼
创建 PR (develop → master) via gh CLI
    │
    ▼
等待 CI (最多 120 秒)
    │
    ├─ CI 失败 → 停止，报错
    ├─ CI 超时 → 停止，报错
    └─ CI 通过 ↓
    │
    ▼
合并 PR + 删除分支
    │
    ▼
打 tag v.X.Y.Z + 推送
    │
    ▼
同步 develop (ff merge from master)
    │
    ▼
✓ 发布完成
```

### 版本更新细节

```bash
# Simplified from: scripts/release.sh:57-63
# 读取当前版本（单一事实源）
CURRENT_VERSION=$(grep '^version:' skills/project-walkthrough/SKILL.md | head -1 | sed 's/version: * "//;s/"//')

# 更新 SKILL.md frontmatter
sed -i.bak "s/^version: \"${CURRENT_VERSION}\"/version: \"${VERSION}\"/" skills/project-walkthrough/SKILL.md

# 更新 plugin.json
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" .claude-plugin/plugin.json
```

每次 `sed` 后立即删除 `.bak` 文件，保持工作区干净。

### CI 等待机制

```bash
# Simplified from: scripts/release.sh:129-143
MAX_WAIT=120
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep 10
    ELAPSED=$((ELAPSED + 10))
    CHECKS=$(gh pr checks "$PR_NUM" 2>&1 || true)
    if echo "$CHECKS" | grep -q "fail"; then
        echo "ERROR: CI failed!" >&2; exit 1
    fi
    if echo "$CHECKS" | grep -q "pass" && ! echo "$CHECKS" | grep -q "pending"; then
        echo "CI passed!"; break
    fi
done
```

每 10 秒轮询一次 CI 状态，最多等 120 秒。失败或超时都会中止发布。

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| 1.0.0 | 2026-05-09 | Manifest-first Phase 3 + 185 tests |
| 1.1.0 | 2026-05-20 | 多语言 + 自适应 scope + 多平台 + EXTEND.md |
| 1.2.0 | 2026-05-20 | AGENTS.md + GitHub Actions CI + convert.sh tests |
| 1.3.0 | 2026-05-20 | release.sh 自动化 |
| 1.4.0 | 2026-05-20 | 4 种语言模式 + `--version` flag |
| 1.5.0 | 2026-05-20 | Deep mode 全内容转换 |
| 1.6.0 | 2026-05-22 | Converter-first + i18n + quiz + 自动质量门禁 |
| 1.6.1 | 2026-05-22 | verify-result.json 结构化验证证据 |

[← 上一章](07-supporting-scripts.md) | [下一章 →](09-multi-platform.md)
