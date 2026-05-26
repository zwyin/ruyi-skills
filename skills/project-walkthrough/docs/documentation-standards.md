# Documentation Standards

This file defines the writing and formatting rules for walkthrough output.
Extracted from `SKILL.md` to keep the skill definition focused on process.

## Language

The output language is controlled by the `--lang` parameter (default: `zh`).

### `zh` mode (Chinese body + English terms)

- **Default mode.** Write all explanatory text in Chinese regardless of the source project's language.
- **Technical terms:** Keep standard terms in English (e.g., "middleware", "hook", "schema", "plugin", "CI/CD"). On first appearance, add a brief Chinese annotation in parentheses if the term might be unfamiliar.
- **Code comments in examples:** Match the style of the actual source code. If source uses English comments, keep English. If Chinese, keep Chinese.
- **Architecture diagrams:** Labels in Chinese. Technical identifiers (file names, function names, module names) always stay in English.
- **Source citations:** `// Simplified from: path:lines` stays in English.
- **Quiz questions and explanations:** Written in Chinese.
- **类比理解 cards:** Written in Chinese.
- **Code block summaries:** Written in Chinese.

### `en` mode (Pure English)

- Write all text in English.
- Technical terms used directly, no translation needed.
- Follow standard English technical writing conventions.
- Code comments match source code style.

### `zh-pure` mode (Pure Chinese)

- All text in Chinese, including technical terms translated where possible.
- Terms with no accepted Chinese translation kept in English (e.g., Kubernetes, OAuth, gRPC).
- Code comments translated to Chinese.
- Architecture diagram labels in Chinese; identifiers kept in English (cannot translate code names).
- Source citations (`// Simplified from:`) kept in English (machine-readable format).
- Quiz questions and explanations in Chinese with translated terms.
- 类比理解 cards in Chinese with translated technical terms.

### `bilingual` mode (Chinese-English side-by-side)

- Each major section: Chinese paragraph first, then English translation.
- Technical terms kept in English in both versions.
- Code blocks shown once (shared between both language sections).
- Quiz questions in both languages.
- 类比理解 cards in Chinese only (English readers don't need analogies for technical terms).
- Navigation and metadata in both languages.

### Common rules (all modes)

- **File names, function names, module names, variable names** always stay in English (these are code identifiers, not prose).
- **Version numbers** always from config files (`package.json` / `Cargo.toml` / `pyproject.toml`), never from README.
- **Directory trees** show actual paths in English.
- **Source citation format** is always `// Simplified from: path:lines`.

## Structure

- Every chapter starts with a title + one-line subtitle
- Use backend analogies for every concept (middleware, CI/CD, HTTP, databases)
- Include code examples from the actual source (not fabricated)
- **Every code block must have a source citation** — `// Simplified from: path:lines`. Code blocks without source citations are a quality violation.
- Include architecture diagrams in ASCII or CSS flow format
- Every chapter ends with navigation links (← previous | next →)

## Source Verification

All source verification happens in Phase 3A (verify & build manifest) and Phase 3C (validate coverage). See SKILL.md Process section for the complete verification procedure.

## Audience: `general` mode specifics

Add these elements when audience is `general`:

**类比理解 cards** (at every technical term's first appearance):
```
┌─────────────────────────────────────────┐
│ 🔍 类比理解                              │
│                                         │
│ Prompt 注入 ≈ 钓鱼邮件                   │
│                                         │
│ 就像钓鱼邮件伪装成正常邮件骗你点击链接，   │
│ Prompt 注入是伪装成正常网页内容骗 AI 执行  │
│ 恶意指令。防御方式也类似：过滤器 = 垃圾    │
│ 邮件过滤，蜜罐 = 诱饵链接检测。           │
└─────────────────────────────────────────┘
```

**Code block summaries** (before every code block):
```
这段代码的作用：在网页内容中插入一个唯一的"标记"，
如果 AI 被骗后把这个标记说出来了，就说明攻击成功。
```

When `--lang en`, replace 类比理解 cards with **Analogy** cards in English:
```
┌─────────────────────────────────────────┐
│ 💡 Analogy                              │
│                                         │
│ Prompt injection ≈ phishing emails      │
│                                         │
│ Just as phishing emails trick you into   │
│ clicking malicious links, prompt         │
│ injection tricks AI into executing       │
│ malicious instructions hidden in web     │
│ content.                                │
└─────────────────────────────────────────┘
```

And code block summaries in English:
```
What this code does: Inserts a unique marker into web content.
If the AI reveals the marker, the attack succeeded.
```

## Audience: `dev` mode specifics

- No analogy cards
- Code blocks analyzed line by line with inline comments
- Technical terms used directly
- Performance data and benchmarks where available
