# 11 设计哲学：准确性、Converter-First、Manifest-First

## 三个核心设计决策

project-walkthrough 的设计围绕三个相互支撑的原则，它们共同解决了"AI 生成的技术文档能不能信任"这个问题。

## 原则 1：Manifest-First — 验证先于写入

### 问题

LLM 在生成技术内容时容易"编造"合理的代码片段——函数签名看起来正确但实际不存在，版本号来自 README 而不是 package.json，目录结构是推断的而不是验证的。

### 解决方案

Phase 3 分为 3A（验证）和 3B（写入）两个子阶段。manifest 不是事后审计，而是**写入许可证**。

```
传统流程：  写内容 → 审查 → 发现错误 → 重写
Manifest：  验证声明 → 获得"许可证" → 只写已验证的内容
```

### 核心规则

1. **不可验证 = 不写入** — 如果 Phase 3A 无法验证一个声明，它不会出现在 walkthrough 中
2. **禁止 `// Source:`** — 统一使用 `Simplified from:`，因为 walkthrough 代码总是被简化的
3. **12 轮迭代** — 通过 12 轮验证迭代建立，最后 3 轮零问题

### 代价

- 生成速度较慢（每个声明都需要额外读取源文件）
- 内容量可能比无验证方式少（无法写入不确定的内容）
- 对 LLM 的上下文窗口有更高要求

### 收益

- 读者可以信任每个代码片段都来自真实源码
- 每个 `// Simplified from: path:lines` 引用可以手动验证
- 减少了"看起来专业但内容不准确"的风险

## 原则 2：Converter-First — Python 预渲染替代 LLM 拼装

### 问题

v1.6.0 之前，HTML 由 LLM 通过 DOM API（createElement、textContent）手动拼装。这导致了多个问题：
- innerHTML 限制使得富内容生成几乎不可能
- 手动拼装 3-5 倍冗长于等价 HTML
- 出现过静默空内容 bug（section 只有标题没有内容）
- 安全 hook 阻止动态 DOM 写入

### 解决方案

`md_to_html.py` 作为唯一的 HTML 生成器，所有深度级别都走 converter：
- Brief/Medium：converter 自动处理，产出物可靠
- Deep：完整 markdown-to-HTML 转换，零内容裁剪

### 内置安全保障

converter 自带三层 XSS 防护：
1. `sanitize_url()` — 阻止 `javascript:` 和 `data:` URL
2. `escape_html()` — 所有文本内容 HTML 转义
3. `preprocess_md()` — 移除 HTML 注释

### 生成后自动校验

每次 converter 运行后自动执行 `verify_html()`：
- Section 计数 = markdown 文件数
- 每个章节至少有标题和内容元素
- HTML 大小 ≥ markdown 总大小的 80%
- 零残留 `.md` 链接

## 原则 3：单一事实源 — SKILL.md 驱动一切

### 问题

多平台支持意味着同一份内容需要出现在不同格式、不同位置。手动维护会导致不一致。

### 解决方案

`skills/ruyi-project-walkthrough/SKILL.md`（890 行）是所有内容的唯一来源：

```
SKILL.md (890 行，单一事实源)
    │
    ├─→ convert.sh → cursor/ruyi-project-walkthrough.mdc
    ├─→ convert.sh → .windsurf/rules/ruyi-project-walkthrough.md (精简 <12K)
    └─→ convert.sh → .opencode/skills/ruyi-project-walkthrough/SKILL.md
```

版本号也是单一来源：
```
SKILL.md frontmatter (version: "1.6.1")
    │
    ├─→ release.sh → plugin.json
    ├─→ release.sh → marketplace.json
    ├─→ release.sh → README badge
    └─→ release.sh → CHANGELOG
```

CI 通过 `convert.sh --check` 确保同步，任何不同步都会导致 CI 失败。

## 三个原则的协同

```
SKILL.md (单一事实源)
    │
    ├─→ Manifest-First 保证内容准确性
    │     └─→ verify_sources.py 验证
    │
    └─→ Converter-First 保证 HTML 质量
          └─→ md_to_html.py + verify_html() 校验
```

三个原则形成一个闭环：
- SKILL.md 定义了"应该做什么"
- Manifest-first 确保执行时不偏离事实
- Converter-first 确保输出质量不受 LLM 限制

## 权衡与取舍

| 决策 | 优势 | 代价 |
|------|------|------|
| Manifest-first | 内容可信 | 生成更慢，需要更多上下文 |
| Converter-first | HTML 质量稳定 | 依赖 Python 环境 |
| SKILL.md 单一来源 | 一致性保证 | 修改任何内容都需要 convert.sh |
| Windsurf 12K 限制 | 兼容 Windsurf | 部分内容被精简 |

[← 上一章](10-testing-ci.md) | [下一章 →](12-summary.md)
