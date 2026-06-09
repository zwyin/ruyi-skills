# 01 概览：什么是 project-walkthrough

## 这个项目是什么

project-walkthrough 是一个 Claude Code skill（技能插件），为任意软件项目自动生成结构化的技术走读文档。输入一个项目路径，输出编号的 markdown 章节文件 + 一个可在浏览器打开的交互式 HTML。

> 类比理解：project-walkthrough 就像一个"技术导游"——你给它一个项目地址，它帮你把整个项目从头到尾走一遍，写一份带地图、带讲解、带小测验的旅行手册。

## 核心功能

| 功能 | 说明 |
|------|------|
| **多深度输出** | brief（概览 ~30min）、medium（进阶 ~60min）、deep（深入 ~120min）、all（依次生成三级） |
| **多受众模式** | general（类比+白话解释）、dev（纯技术分析） |
| **多语言** | zh（中文+英文术语）、zh-pure（纯中文）、en（纯英文）、bilingual（中英对照） |
| **交互式 HTML** | 自包含单文件，暗色/亮色切换、侧边栏导航、可展开详情、互动 quiz |
| **Manifest-first 准确性** | 先验证所有事实声明，再写内容，每个代码块可追溯到源码 |
| **Converter-first HTML** | Python 预渲染静态 HTML，避免 innerHTML 限制导致的空内容问题 |

## 版本与仓库

当前版本 **v1.6.1**，MIT 许可证。

版本号出现在 6 个位置，全部从 `skills/ruyi-project-walkthrough/SKILL.md` frontmatter 同步：

```
// Simplified from: skills/ruyi-project-walkthrough/SKILL.md:1-5
---
name: project-walkthrough
version: "1.6.1"
description: "..."
---
```

## 技术栈

| 层面 | 技术 |
|------|------|
| Skill 定义 | Markdown (SKILL.md)，890 行 |
| 辅助脚本 | Python 3（md_to_html.py, verify_sources.py, import_graph.py） |
| 平台转换 | Bash（convert.sh） |
| 版本发布 | Bash（release.sh） |
| 测试 | pytest，8 个测试文件，250 个测试函数 |
| CI | GitHub Actions，ubuntu-latest + Python 3.12 |
| 多平台 | Cursor / Windsurf / OpenCode / Gemini CLI 兼容 |

## 项目目录结构

```
project-walkthrough/
├── .claude-plugin/           ← 插件元数据（plugin.json, marketplace.json）
├── skills/
│   └── ruyi-project-walkthrough/
│       ├── SKILL.md          ← 890 行，skill 的单一事实源
│       └── references/       ← 分析框架、范围矩阵、偏好配置
├── scripts/
│   ├── md_to_html.py         ← 643 行，Markdown→HTML 转换器
│   ├── verify_sources.py     ← 315 行，manifest 验证
│   ├── import_graph.py       ← 239 行，依赖图提取
│   ├── convert.sh            ← 272 行，多平台文件生成
│   └── release.sh            ← 166 行，版本发布自动化
├── docs/                     ← 设计文档（6 个规范文件）
├── tests/                    ← 8 个测试文件，3 个 fixture 项目
├── cursor/                   ← Cursor IDE 规则文件
├── .windsurf/                ← Windsurf 规则文件
├── .opencode/                ← OpenCode skill 文件
├── examples/                 ← 自生成示例（zh + en）
└── CHANGELOG.md              ← 6 个版本的变更记录
```

## 设计亮点

1. **Manifest-first**：Phase 3A 先验证所有声明写入 manifest，Phase 3B 只写已验证内容——"不可验证 = 不写入"
2. **Converter-first**：所有深度级别的 HTML 都由 `md_to_html.py` 生成，不依赖 LLM 手动拼 DOM
3. **SKILL.md 是单一事实源**：所有平台文件由 `convert.sh` 从 SKILL.md 生成
4. **自动质量门禁**：HTML 生成后自动校验 section 完整性、内容密度、broken links

[下一章 →](02-pipeline.md)
