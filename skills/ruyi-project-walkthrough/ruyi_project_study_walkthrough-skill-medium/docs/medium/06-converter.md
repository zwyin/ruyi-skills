# 06 md_to_html.py：Markdown 到交互式 HTML 转换器

## 概览

`scripts/md_to_html.py`（643 行）是 project-walkthrough 的 HTML 生成引擎。从 v1.6.0 起，所有深度级别的 HTML 都由这个转换器生成——不再依赖 LLM 手动拼 DOM。

> 类比理解：这个转换器就像一个"印刷机"——markdown 是手稿，转换器把它们排版成精美的交互式网页。它处理文字排版、配色、导航、测验等功能。

## 核心函数一览

| 函数 | 行号 | 作用 |
|------|------|------|
| `convert_md_to_html()` | 129 | Markdown→HTML 核心转换 |
| `parse_table()` | 103 | Markdown 表格→HTML 表格 |
| `process_inline()` | 84 | 行内格式处理（加粗、斜体、代码、链接） |
| `extract_quiz_section()` | 201 | 从 markdown 中分离 quiz 部分 |
| `parse_quiz_md()` | 223 | 解析 quiz markdown 为结构化数据 |
| `build_quiz_section()` | 270 | 生成交互式 quiz 的 HTML+JS |
| `build_watermark_section()` | 314 | 生成"关于本报告"尾页 |
| `build_html()` | 358 | 组装完整 HTML 页面 |
| `verify_html()` | 462 | 生成后自动校验 |
| `main()` | 553 | CLI 入口 |

## 转换流程

```bash
# 基本用法
python scripts/md_to_html.py docs/ output.html \
  --title "Project Name" --accent "#4a6fa5" --lang zh --quiz-chapter 6

# 验证已生成的 HTML
python scripts/md_to_html.py --verify output.html --source-dir docs/
```

转换器按以下顺序处理：

1. 读取 `docs_dir` 下的所有 `.md` 文件（按文件名排序）
2. 提取第一个文件的 `# 标题` 作为 HTML 标题
3. 对每个文件调用 `convert_md_to_html()` 转换
4. 如果指定 `--quiz-chapter`，从对应章节提取 quiz
5. 可选生成 watermark（"关于本报告"页面）
6. 调用 `build_html()` 组装完整页面
7. 调用 `verify_html()` 自动校验
8. 写入 `verify-result.json` 校验结果

## Markdown 元素映射

转换器支持所有常见 markdown 元素：

| Markdown | HTML |
|----------|------|
| `# H1` | `<h1>` |
| `## H2` | `<h2>` |
| `### H3` | `<h3>` |
| `#### H4` | `<h4>` |
| `---` | `<hr>` |
| `` ```code``` `` | `<pre><code>` |
| `| table |` | `<table>` |
| `> quote` | `<blockquote>` |
| `- list` | `<ul>` |
| `1. list` | `<ol>` |
| `**bold**` | `<strong>` |
| `*italic*` | `<em>` |
| `` `code` `` | `<code>` |
| `<details>` | 原样保留 |

## 多语言支持 (I18N)

4 种语言模式影响导航、按钮、quiz 标题的文案：

```python
// Simplified from: scripts/md_to_html.py:23-30
I18N = {
    "zh": {
        "lang": "zh-CN", "chapters": "章节",
        "prev": "&larr; 上一章", "next": "下一章 &rarr;",
        "quiz_title": "知识测验",
    },
    "en": { ... },
}
```

每种语言模式还定义了 `nav_skip` 正则表达式，用于移除 markdown 中的"上一章/下一章"导航链接（HTML 中用 JS `showChapter()` 替代）。

## Quiz 系统

Quiz 从 markdown 的 `## Quiz` 章节中提取，格式为：

```markdown
**Q1:** 问题描述？
- A. 选项1
- B. 选项2
- C. 选项3
- D. 选项4
**Answer: B**
**Explanation:** 解释文本
```

解析后生成一个 JavaScript `quizData` 数组，用 DOM API 渲染为交互式按钮：
- 点击选项后禁用所有按钮
- 正确答案绿色高亮，错误答案红色
- 显示解释文本

## XSS 防护

转换器内置三层安全防护：

```python
// Simplified from: scripts/md_to_html.py:62-68
def sanitize_url(url):
    """Block javascript:, data:, vbscript: etc."""
    scheme = re.match(r'^([a-zA-Z][a-zA-Z0-9+.-]*):', url.strip())
    if scheme and scheme.group(1).lower() not in ('http', 'https', 'mailto', 'tel', ''):
        return '#'
    return url
```

1. **URL 过滤** — 阻止 `javascript:` 和 `data:` 协议
2. **HTML 转义** — 所有文本内容通过 `escape_html()` 处理
3. **HTML 注释剥离** — `preprocess_md()` 移除所有 `<!-- ... -->`

## 自动校验 (verify_html)

每次生成后自动运行 6 项校验：

1. **Section 计数** — HTML 章节数 = markdown 文件数
2. **Per-section 内容检查** — 每个章节至少有标题和内容元素
3. **文件大小比率** — HTML ≥ markdown 总大小的 80%
4. **Broken links** — 零残留 `.md` 链接
5. **导航一致性** — 侧边栏链接数 = 章节数
6. **Quiz 存在性** — 如果源 markdown 有 quiz，HTML 也必须有

校验结果写入 `verify-result.json`：

```json
{
  "passed": true,
  "section_count": 12,
  "html_size": 45678,
  "markdown_size": 52345,
  "ratio_pct": 87,
  "errors": []
}
```

[← 上一章](05-manifest-accuracy.md) | [下一章 →](07-supporting-scripts.md)
