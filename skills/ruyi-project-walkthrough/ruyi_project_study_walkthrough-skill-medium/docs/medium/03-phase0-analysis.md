# 03 Phase 0：内容分析与确认门

## Phase 0 的角色

Phase 0 是整个 pipeline 的"调度中心"——它分析输入内容，推荐 scope/depth/format，然后让用户确认后才进入正式生成。这避免了"生成了半天发现不是用户想要的"问题。

> 类比理解：Phase 0 就像餐厅的菜单推荐——先看你是几个人、什么口味、预算多少，给你推荐套餐，你确认了再下单做菜。

## 三个子阶段

### Phase 0.1：加载偏好 (EXTEND.md)

project-walkthrough 支持两级偏好配置文件：

| 优先级 | 路径 | 作用域 |
|--------|------|--------|
| 1 | `.project-walkthrough/EXTEND.md` | 项目级 |
| 2 | `$HOME/.project-walkthrough/EXTEND.md` | 用户级（全局） |

```yaml
// Simplified from: .project-walkthrough/EXTEND.md:1-7
---
scope: auto
depth: auto
language: zh
manifest_strictness: auto
confirm_scope: true
---
```

偏好文件遵循以下规则：
- **找到**：显示摘要，继续执行
- **找到但 YAML 无效**：显示错误，提供重新设置选项
- **未找到**：运行首次设置引导，生成 EXTEND.md 后继续

### Phase 0.2：内容分析 → analysis.md

内容分析框架定义在 `references/analysis-framework.md` 中，包含 5 个维度：

1. **检测内容类型** — 软件项目 / 文档报告 / 混合
2. **测量输入规模** — 文件数、行数、目录深度
3. **分析内容结构** — 统计数据、案例研究、代码块、引用
4. **评估技术密度** — 低 / 中 / 高
5. **生成推荐** — scope、章节数、每章深度、manifest 严格度

分析结果保存为 `analysis.md`，包含 YAML front matter（类型、规模、技术密度）+ 分析正文。

### Phase 0.3：确认门 (Confirmation Gate)

确认门通过交互式问答让用户最终决定生成参数。这是 Phase 0 的核心交互环节。

**跳过条件**：`--no-confirm` 标志或 EXTEND.md 中 `confirm_scope: false`

确认门包含 5 个问题：

| 问题 | 选项 |
|------|------|
| Q1: 走读范围 | Full / Focused / Overview / Custom |
| Q2: 每章深度 | Detailed / Standard / Summary |
| Q3: 输出格式 | HTML+Markdown / Markdown only / HTML only |
| Q4: 审查大纲 | Yes / No |
| Q5: 输出语言 | zh / zh-pure / en / bilingual |

`--depth` 标志会影响 Q1 的推荐选项。例如 `--depth medium` 对应 Focused scope，Q1 会预选 "Focused walkthrough (Recommended)"。

## Depth ↔ Scope 映射表

CLI 的 `--depth` 标志设置两个内部参数的默认值：

| `--depth` | Scope | 每章深度 | 章节数指南 |
|-----------|-------|---------|-----------|
| `brief` | `overview` | `standard` | 5-8 个主题章节 |
| `medium` | `focused` | `detailed` | 10-15 个关键章节 |
| `deep` | `full` | `detailed` | 无硬性上限，适应输入 |
| `all` | 依次三级 | 按级别变化 | 按级别变化 |

## 范围不匹配警告

如果 `--depth` 提示的 scope 会导致丢弃超过 50% 的输入章节（例如 `--depth brief` 作用在 30 章文档上），会显示警告：

> Warning: overview scope will consolidate [N] chapters into 5-8 thematic groups. Consider 'focused' to preserve top chapters.

这确保用户在知情的情况下做出选择。

[← 上一章](02-pipeline.md) | [下一章 →](04-exploration-planning.md)
