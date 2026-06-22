# Project Walkthrough Generator

[![CI](https://github.com/zwyin/ruyi-skills/actions/workflows/test.yml/badge.svg)](https://github.com/zwyin/ruyi-skills/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.6.3-blue.svg)]

为任意软件项目生成分层技术走读文档的 Claude Code skill。输出 markdown 文档 + 交互式 HTML。

[← 返回 ruyi-skills 合集](https://github.com/zwyin/ruyi-skills#readme)

## 功能

- **多深度**：brief（概览）、medium（进阶）、deep（深入）、all（全部）
- **多受众**：general（类比+白话）、dev（纯技术）
- **多语言**：zh（中文+英文术语，默认）、zh-pure（纯中文）、en（纯英文）、bilingual（中英对照）
- **输出**：编号 markdown 章节 + 自包含交互式 HTML（暗色/亮色、侧边栏、quiz）
- **Converter-first HTML**：`md_to_html.py` 离线转换器，Python 预渲染静态 HTML，避免 innerHTML 限制导致的空内容问题
- **自动质量门禁**：生成后自动校验 section 完整性、内容密度、broken links，失败自动修复（最多 3 轮），不通过不交付
- **自适应范围**：Phase 0 分析内容类型，推荐 scope/depth/format，交互确认后再生成
- **偏好配置**：支持项目级/用户级 EXTEND.md，保存常用参数组合
- **自动探索协议**：识别项目类型 → 读核心文件 → 提取创新点 → 生成章节
- **Manifest-first 准确性保证**：先验证所有声明，再写内容，每个事实可追溯到源码

## 安装

### Claude Code（推荐）

```bash
# 1. 添加 marketplace
/plugin marketplace add zwyin/ruyi-skills

# 2. 安装插件
/plugin install ruyi-skills@ruyi-skills
```

安装后直接在任意项目中使用 `/ruyi-project-walkthrough` 命令。

### 手动安装

将本仓库 clone 到本地，然后在 Claude Code 中指定 plugin 目录：

```bash
git clone https://github.com/zwyin/ruyi-skills.git
claude --plugin-dir ./ruyi-skills  # 保留完整目录结构，路径引用不会断裂
```

### 其他平台

| 平台 | 安装方式 |
|------|---------|
| **Cursor** | 复制 `cursor/ruyi-project-walkthrough.mdc` 到项目的 `.cursor/rules/` 目录 |
| **Windsurf** | 复制 `.windsurf/rules/ruyi-project-walkthrough.md` 到项目的 `.windsurf/rules/` 目录，或全局复制到 `~/.codeium/windsurf/rules/` |
| **OpenCode** | 复制 `.opencode/skills/ruyi-project-walkthrough/` 到项目的 `.opencode/skills/` 目录，或全局复制到 `~/.config/opencode/skills/` |
| **Gemini CLI** | `gemini skills install https://github.com/zwyin/ruyi-skills.git --path skills/ruyi-project-walkthrough` |

> **注意：** Python 辅助脚本（`verify_sources.py`、`import_graph.py`）需要 Python 3 环境。在非 Claude Code 平台上，部分依赖脚本的功能可能需要手动调整路径。

## 快速上手

**新手 / 第一次用？** 不带任何参数，直接分析当前项目：

```
/ruyi-project-walkthrough
```

这会生成一份中文概览走读（brief + general），包含 7-8 个章节 + 一个可在浏览器打开的交互式 HTML。打开 `interactive/walkthrough.html` 即可浏览。

**资深开发者？** 推荐用这个模式获取最深度的项目分析：

```
/ruyi-project-walkthrough /path/to/project --depth deep --audience dev
```

这会生成完整的技术深入走读：逐行代码分析、设计模式、安全模型、性能特征、错误处理、配置系统，附带 15-20 道测验题。

## 用法

```
/ruyi-project-walkthrough                                              # Brief + general + zh (CWD)
/ruyi-project-walkthrough /path/to/project                             # Brief + general + zh
/ruyi-project-walkthrough /path/to/project --depth medium              # Medium + general + zh
/ruyi-project-walkthrough /path/to/project --depth deep --audience dev # Deep + dev + zh
/ruyi-project-walkthrough --depth all                                  # All depths + general + zh (CWD)
/ruyi-project-walkthrough /path/to/project --lang en                   # Brief + general + en
/ruyi-project-walkthrough /path/to/project --depth deep --no-confirm    # Deep + 跳过确认门
/ruyi-project-walkthrough /path/to/project --lang zh-pure               # Brief + general + 纯中文
/ruyi-project-walkthrough /path/to/project --lang bilingual             # Brief + general + 中英对照
/ruyi-project-walkthrough --version                                    # 显示版本号
```

**参数说明：**

| 参数 | 允许值 | 默认值 | 说明 |
|------|--------|--------|------|
| `[path]` | 目录路径 | 当前目录 | 项目目录 |
| `--depth` | `brief`, `medium`, `deep`, `all` | `brief` | `brief` 概览 ~30min 7-8 文档；`medium` 进阶 ~60min 12-15 文档；`deep` 深入 ~120min 8-15 文档；`all` 依次生成三级 |
| `--audience` | `general`, `dev` | `general` | `general` 类比+白话；`dev` 纯技术分析 |
| `--lang` | `zh`, `zh-pure`, `en`, `bilingual` | `zh` | `zh` 中文正文+英文术语；`zh-pure` 纯中文；`en` 纯英文；`bilingual` 中英对照 |
| `--no-confirm` | — | — | 跳过 Phase 0 确认门，使用推荐默认值 |
| `--version` | — | — | 显示版本号并退出 |

**语法规则：** 空格分隔（`--depth medium`），不支持 `--depth=medium`。无效值回退到默认。重复 flag 取最后一次。flags 大小写敏感。

> 详细解析规则见 `skills/ruyi-project-walkthrough/SKILL.md` Usage 部分。

## 偏好配置（EXTEND.md）

保存常用参数，避免每次手动指定。Skill 按以下顺序加载（后者覆盖前者）：

| 优先级 | 路径 | 作用域 |
|--------|------|--------|
| 1 | `.project-walkthrough/EXTEND.md` | 项目级 |
| 2 | `$HOME/.project-walkthrough/EXTEND.md` | 用户级（全局） |

**首次使用时**自动触发设置引导，生成示例配置。格式示例：

```yaml
# .project-walkthrough/EXTEND.md
---
default_depth: deep
default_audience: dev
default_lang: zh        # zh | zh-pure | en | bilingual
skip_confirm: false
---
```

也可添加自定义指令（如重点关注安全模块、忽略测试目录等），详见 `references/preferences-schema.md`。

## 输出结构

```
<prefix>_project_study_<project-name>-<depth>-<lang>-<audience>/
├── docs/
│   ├── 01-overview.md              ← Brief
│   ├── sources-manifest.json       ← Brief manifest（强制性）
│   ├── medium/
│   │   └── sources-manifest.json   ← Medium manifest
│   └── deep/
│       └── sources-manifest.json   ← Deep manifest
└── interactive/
    ├── walkthrough.html
    ├── medium-walkthrough.html
    └── deep-walkthrough.html
```

## 准确性机制

核心原则：**verify before write**。通过 12 轮迭代验证建立：

- **Manifest-first**：Phase 3A 先验证所有声明写入 manifest，Phase 3B 只写已验证内容
- **Source citation**：每个代码块必须有 `// Simplified from: path:lines`
- **禁止 `// Source:`**：统一使用 `Simplified from:`（walkthrough 代码总是简化的）
- **不可验证 = 不写入**：无法验证的声明不能出现在 walkthrough 中
- **自动化验证**：`scripts/verify_sources.py` 检查 manifest 完整性和源文件存在性

## 测试

```bash
pytest tests/ -v                    # 单元测试 + 产出物结构验证
python scripts/verify_sources.py --check-all examples/ --strict  # manifest 验证
```

## 项目结构

```
├── .claude-plugin/
│   ├── plugin.json                 # Claude Code 插件元数据
│   └── marketplace.json            # Marketplace 注册信息
├── AGENTS.md                       # 跨平台自描述文件（Cursor/Windsurf/OpenCode 自动扫描）
├── cursor/
│   └── project-walkthrough.mdc     # Cursor IDE 规则文件
├── .windsurf/
│   └── rules/
│       └── project-walkthrough.md  # Windsurf 规则文件
├── .opencode/
│   └── skills/
│       └── project-walkthrough/
│           └── SKILL.md            # OpenCode skill 文件
├── skills/
│   └── project-walkthrough/
│       └── SKILL.md                # Skill 定义（流程、规范、checklist）
├── docs/
│   ├── html-reference.md           # HTML 模板和 CSS 组件规范
│   ├── documentation-standards.md  # 文档写作和格式规范
│   ├── chapter-templates.md        # 按项目类型的章节模板
│   ├── exploration-protocol.md     # 探索协议
│   ├── sources-manifest-schema.md  # Manifest schema 文档
│   ├── sources-manifest.schema.json  # Manifest JSON Schema
│   └── accuracy-verification-protocol.md  # 准确性验证协议
├── scripts/
│   ├── convert.sh                  # 跨平台文件自动生成
│   ├── md_to_html.py               # Markdown→交互式 HTML 转换器（自动校验 + 多语言 + quiz）
│   ├── release.sh                  # 版本发布自动化
│   ├── verify_sources.py           # Manifest 验证脚本
│   └── import_graph.py             # 依赖图提取脚本
├── tests/
│   ├── test_walkthrough_output.py  # 输出验证测试
│   ├── test_verify_sources.py      # Manifest 验证测试
│   ├── test_import_graph.py        # 依赖图测试
│   ├── test_convert.py             # 跨平台转换测试
│   ├── test_adaptive_scope.py      # 自适应范围测试
│   ├── test_lang_output.py         # 多语言输出测试
│   └── test_release_sh.py          # 发布脚本测试
├── CHANGELOG.md                    # 版本变更记录
├── CONTRIBUTING.md                 # 贡献指南
├── Makefile                        # 开发命令（test/ci/release）
└── TODO.md                         # 待办事项
```

## 示例 / Demo

本仓库包含自生成的 walkthrough 示例，展示插件产出物的实际效果：

| 示例 | 语言 | 说明 |
|------|------|------|
| [`examples/self-demo-zh/`](examples/self-demo-zh/) | `--lang zh` | 中文概览 walkthrough（本插件自身） |
| [`examples/self-demo-en/`](examples/self-demo-en/) | `--lang en` | 英文概览 walkthrough（本插件自身） |

打开 `interactive/walkthrough.html` 即可在浏览器中体验交互式走读。

## License

MIT
