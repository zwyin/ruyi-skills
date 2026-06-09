# 12 总结与扩展指南

## 项目核心总结

project-walkthrough 是一个 Claude Code skill，为任意软件项目自动生成结构化技术走读文档。它的核心贡献不是"生成文档"本身，而是**如何确保生成的文档是可信的**。

### 关键数字

| 维度 | 数值 |
|------|------|
| 版本 | 1.6.1（6 个版本迭代） |
| SKILL.md | 890 行（单一事实源） |
| 脚本 | 5 个，共 1635 行 Python + Bash |
| 测试 | 250 个测试函数，2778 行 |
| 支持平台 | 5 个（Claude Code, Cursor, Windsurf, OpenCode, Gemini CLI） |
| 支持语言 | 4 种（zh, zh-pure, en, bilingual） |
| 支持深度 | 4 种（brief, medium, deep, all） |
| 项目类型模板 | 8 个（AI Tool, Library, Web App, CLI, Document, Game Engine, Database, Compiler） |

### 架构一句话总结

5 阶段 pipeline（分析→探索→规划→生成→验证），以 manifest-first 保证准确性，converter-first 保证 HTML 质量，SKILL.md 单一来源保证一致性。

## 创新点

1. **Manifest 作为写入许可证** — 不是审计日志，而是结构化的写入前置条件
2. **Converter-first HTML** — 用 Python 预渲染替代 LLM 手动拼 DOM，消除空内容 bug
3. **6 位置版本同步** — 从单一来源自动同步到 6 个位置
4. **自适应范围系统** — Phase 0 分析输入后推荐 scope/depth，交互确认后再生成
5. **Windsurf 智能精简** — 根据字符限制自动跳过冗长段落

## 已知限制

| 限制 | 说明 |
|------|------|
| Python 依赖 | HTML 生成需要 Python 3，无 Python 时只能输出 markdown |
| 版本手动更新 | 仍需手动修改 SKILL.md frontmatter 的 version 字段 |
| 插件无自动更新 | 用户需重新安装或 `git pull` 来获取更新 |
| `--version` 硬编码 | 版本输出是字符串，不从 plugin.json 动态读取 |
| Windsurf 精简 | 为满足 12K 字符限制，部分详细内容被省略 |

## 扩展指南

### 添加新的项目类型模板

1. 在 `docs/chapter-templates.md` 中添加新模板
2. 在 `docs/exploration-protocol.md` 的 Step 1 表格中添加新类型
3. 运行 `./scripts/convert.sh` 更新所有平台文件

### 添加新的声明类型

1. 在 `docs/sources-manifest-schema.md` 中添加类型说明
2. 在 `docs/sources-manifest.schema.json` 的 enum 中添加类型
3. 在 `scripts/verify_sources.py` 的 `VALID_CLAIM_TYPES` 集合中添加
4. 添加对应的验证逻辑

### 添加新的支持平台

1. 在 `scripts/convert.sh` 中添加新的生成函数
2. 在 `convert.sh` 的 `--check` 模式中添加同步检查
3. 在 `AGENTS.md` 和 `README.md` 中添加安装说明

### 修改 pipeline 流程

1. 在 `skills/ruyi-project-walkthrough/SKILL.md` 中修改对应 Phase
2. 更新 Checklist 部分
3. 运行 `./scripts/convert.sh` 同步到所有平台
4. 在 `CHANGELOG.md` 中记录变更

## 版本发布流程

1. 修改 `SKILL.md` frontmatter 的 `version` 字段
2. 运行 `./scripts/release.sh X.Y.Z --bump-only`
3. 手动更新 `CHANGELOG.md` 内容
4. 运行 `./scripts/convert.sh` 同步平台文件
5. 更新 `tests/test_lang_output.py` 中的版本断言
6. 运行 `pytest tests/ -q` 验证
7. 推送到 develop，创建 PR 到 master

## 贡献者资源

- **CONTRIBUTING.md** — 贡献指南和发布流程
- **AGENTS.md** — 跨平台自描述文件
- **docs/** — 6 个设计规范文档
- **examples/** — 自生成示例（zh + en）
- **Makefile** — 开发命令速查

[← 上一章](11-design-philosophy.md)

## Quiz

**Q1:** project-walkthrough 的 Manifest-first 原则中，sources-manifest.json 在 Phase 3A 和 Phase 3B 之间扮演什么角色？

- A. 事后审计日志，记录所有已写入内容的来源
- B. 写入许可证，只有 verified: true 的声明才能在 Phase 3B 中被写入
- C. 配置文件，定义哪些源文件应该被读取
- D. 临时缓存，在 Phase 3C 中被删除

**Answer: B**
**Explanation:** Manifest 是"写入许可证"（write permit），不是审计日志。Phase 3A 验证声明并记录到 manifest，Phase 3B 只能使用 manifest 中 verified: true 的声明。这从结构层面消除了编造内容的可能性。

**Q2:** 为什么 project-walkthrough 禁止使用 `// Source:` 引用格式，只允许 `// Simplified from:`？

- A. 因为 `Source:` 是其他工具的注册商标
- B. 因为 walkthrough 中的代码总是被简化的，`Simplified from:` 更诚实
- C. 因为 `Source:` 格式在 JSON 中会导致解析错误
- D. 因为 `Simplified from:` 可以自动链接到源文件

**Answer: B**
**Explanation:** Walkthrough 中的代码总是会被简化（缩进改变、注释省略、上下文移除）。`Source:` 暗示逐字复制，而 `Simplified from:` 诚实表达了"这段代码来自源文件但经过了简化"。

**Q3:** `md_to_html.py` 转换器的 `verify_html()` 函数检查 HTML 大小是否 ≥ markdown 总大小的 80%。这个检查的目的是什么？

- A. 确保 HTML 文件有足够的空间存储 CSS 和 JavaScript
- B. 防止转换器静默丢弃大量内容（空内容 bug）
- C. 确保浏览器能正确渲染文件
- D. 满足 GitHub 的文件大小限制

**Answer: B**
**Explanation:** 这个检查直接针对 v1.6.0 之前的空内容 bug——HTML 文件可能只有标题没有内容。80% 的比率确保 HTML 包含了 markdown 的大部分内容，而不是被静默裁剪。

**Q4:** `convert.sh` 对 Windsurf 平台做了什么特殊处理？

- A. 为 Windsurf 生成完全不同的内容
- B. 将内容翻译为纯英文
- C. 将 SKILL.md body 精简到 12,000 字符以内
- D. 生成 ZIP 压缩包

**Answer: C**
**Explanation:** Windsurf 对规则文件有字符数限制。convert.sh 通过跳过 Checklist、Documentation Standards、Phase 3 详细步骤等冗长段落来精简内容。如果仍然超限，进一步移除 Examples 段落。

**Q5:** `import_graph.py` 的 "parallel siblings" 概念指什么？

- A. 同一个目录下的所有文件
- B. 共享一个依赖但不互相导入的两个模块
- C. 具有相同函数名的两个模块
- D. 版本号相同的两个依赖

**Answer: B**
**Explanation:** Parallel siblings 是指两个模块都依赖同一个模块，但彼此之间没有导入关系。这表示它们可以独立开发和修改，是架构解耦的信号。

**Q6:** `release.sh` 的 CI 等待机制中，什么条件会导致发布中止？

- A. CI 运行时间超过 60 秒
- B. CI 状态包含 "fail" 或等待超过 120 秒
- C. PR 有待处理的 review
- D. develop 分支和 master 分支有冲突

**Answer: B**
**Explanation:** release.sh 每 10 秒轮询一次 CI 状态，最多等 120 秒。如果 `gh pr checks` 输出包含 "fail"，立即中止。如果 120 秒后仍有 "pending" 状态，也中止并报超时错误。

**Q7:** project-walkthrough 的 Phase 0 确认门中，`--depth medium` 标志会预选哪个 scope 选项？

- A. Full walkthrough
- B. Focused walkthrough
- C. Overview
- D. Custom

**Answer: B**
**Explanation:** Depth ↔ Scope 映射表中，`--depth medium` 对应 `focused` scope。确认门的 Q1 会预选 "Focused walkthrough (Recommended)"，但用户仍可以覆盖选择。

**Q8:** `sources-manifest.json` 中 claim 的 `source_lines` 字段在什么类型中可以为 null？

- A. code_example
- B. api_signature
- C. directory_structure
- D. version_number

**Answer: C**
**Explanation:** directory_structure 类型的声明描述的是目录路径本身，不是一个文件中的具体行范围，所以 source_lines 可以为 null。

**Q9:** `md_to_html.py` 中 `sanitize_url()` 函数允许哪些 URL 协议？

- A. 只允许 http 和 https
- B. 允许 http, https, mailto, tel
- C. 允许所有协议
- D. 允许 http, https, ftp

**Answer: B**
**Explanation:** sanitize_url() 的白名单包含 http, https, mailto, tel 和空字符串（相对路径）。所有其他协议（javascript:, data:, vbscript: 等）被替换为 `#`。

**Q10:** 如果 `project-walkthrough` 的 `--version` 标志出现在命令行中，会怎样？

- A. 显示 SKILL.md 的完整内容
- B. 显示 plugin.json 中的版本号
- C. 打印 "project-walkthrough v1.6.1" 并立即退出，忽略所有其他参数
- D. 从 GitHub API 获取最新版本号

**Answer: C**
**Explanation:** `--version` 是一个独立标志，不消耗值。当它出现在命令行中时，打印硬编码的版本字符串并立即停止，忽略所有其他标志和路径参数。
