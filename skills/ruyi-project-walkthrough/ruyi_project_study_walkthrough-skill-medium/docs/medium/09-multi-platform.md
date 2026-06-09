# 09 多平台兼容策略

## 为什么要多平台

project-walkthrough 最初只支持 Claude Code。但 AI 编码助手生态快速扩张，Cursor、Windsurf、OpenCode、Gemini CLI 各有自己的 skill/rule 系统。为了最大化覆盖面，需要同时支持多个平台。

## 支持的平台

| 平台 | 文件位置 | 安装方式 |
|------|---------|---------|
| **Claude Code** | `.claude-plugin/plugin.json` | `/plugin install` |
| **Cursor** | `cursor/ruyi-project-walkthrough.mdc` | 复制到 `.cursor/rules/` |
| **Windsurf** | `.windsurf/rules/ruyi-project-walkthrough.md` | 复制到 `.windsurf/rules/` |
| **OpenCode** | `.opencode/skills/ruyi-project-walkthrough/SKILL.md` | 复制到 `.opencode/skills/` |
| **Gemini CLI** | `skills/ruyi-project-walkthrough/SKILL.md` | `gemini skills install` |

## 单一事实源策略

所有平台文件都从 `skills/ruyi-project-walkthrough/SKILL.md`（890 行）通过 `convert.sh` 生成。**不应该手动编辑平台文件**。

```bash
# 修改 SKILL.md 后，运行：
./scripts/convert.sh
```

这确保所有平台的内容始终与 SKILL.md 同步。

## 各平台的适配差异

### Cursor (.mdc 格式)

Cursor 的规则文件使用 `.mdc` 扩展名，frontmatter 包含 `description`、`globs`、`alwaysApply` 字段。

```bash
# Simplified from: scripts/convert.sh:53-54
def gen_cursor(body, trigger_desc):
    return f'---\ndescription: "{trigger_desc}"\nglobs:\nalwaysApply: false\n---\n{body}'
```

Cursor 读取完整 SKILL.md body，不做精简。

### OpenCode (SKILL.md 格式)

OpenCode 使用与 SKILL.md 相同的格式，但 frontmatter 额外包含 `license` 和 `compatibility` 字段。

```bash
# Simplified from: scripts/convert.sh:56-60
def gen_opencode(body, fm):
    name = fm.get("name", "project-walkthrough")
    desc = fm.get("description", "")
    arg_hint = fm.get("argument-hint", "")
    return f'---\nname: {name}\ndescription: {desc}\nlicense: MIT\ncompatibility: opencode\nargument-hint: {arg_hint}\n---\n{body}'
```

### Windsurf (精简版)

Windsurf 对规则文件有字符数限制（12,000 字符）。`convert.sh` 会智能精简：

```bash
# Simplified from: scripts/convert.sh:63-68
def gen_windsurf(body, trigger_desc, max_chars):
    """Condense body to fit Windsurf's char limit by removing verbose sections."""
```

精简策略：
1. 跳过 `## Checklist` 和 `## Documentation Standards` 整个段落
2. 跳过 Phase 3A/3B/3C 详细验证步骤
3. 如果仍然超限，进一步移除 Examples 段落
4. 最后检查字符数是否在限制内

### Gemini CLI

Gemini CLI 直接使用 `skills/` 目录结构，不需要额外转换。安装命令：

```bash
gemini skills install https://github.com/zwyin/project-walkthrough-skill.git --path skills/project-walkthrough
```

## AGENTS.md：跨平台自描述

项目根目录的 `AGENTS.md` 是一个跨平台自描述文件。Cursor、Windsurf、OpenCode 都会自动扫描项目根目录的 `AGENTS.md` 来了解项目用途。

```markdown
// Simplified from: AGENTS.md:1-4
# Project Walkthrough Generator

Generate a structured technical walkthrough of any software project...
```

这个文件提供了一个简短的 Quick Start + 选项说明 + 平台安装表格，让任何平台的用户都能快速上手。

## 同步检查

CI 中通过 `convert.sh --check` 确保平台文件与 SKILL.md 保持同步：

```bash
# CI 中的检查
make check  # 等价于 ./scripts/convert.sh --check
```

如果 SKILL.md 被修改但没有重新生成平台文件，CI 会失败并提示 `OUT_OF_SYNC`。

[← 上一章](08-release-automation.md) | [下一章 →](10-testing-ci.md)
