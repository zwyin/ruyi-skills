# 语法高亮引擎

> bat 的核心价值——基于 syntect 的 TextMate 语法高亮。

## 高亮流程

<!-- Simplified from: src/printer.rs:432-470 + src/assets.rs:1-50 -->
```
文件内容
  ↓
[语言检测] — 文件扩展名 / shebang / 自定义映射
  ↓
[语法加载] — 从缓存或内置语法集加载 TextMate 语法
  ↓
[Tokenize] — syntect 解析为 token 序列
  ↓
[Theme 应用] — 将 token 映射到主题颜色
  ↓
[ANSI 输出] — 生成终端可显示的彩色文本
```

## 语言检测

bat 的语言检测链：

<!-- Simplified from: src/syntax_mapping.rs:1-40 -->
```
1. --language 参数（显式指定）
2. 自定义映射 (--map-syntax)
3. 文件扩展名匹配
4. shebang 行检测 (#!/usr/bin/env python)
5. 内容嗅探 (第一行匹配)
6. 回退到纯文本
```

`syntax_mapping/` 目录包含自定义语言映射规则，用户可以通过配置文件扩展。

## 语法资源管理

`assets/` 模块处理语法集和主题的加载：

<!-- Simplified from: src/assets.rs:100-180 -->
```rust
// 两种加载模式
// 1. 内置模式：编译时打包到二进制
let syntax_set = SyntaxSet::load_defaults_newlines();

// 2. 缓存模式：从缓存目录加载（支持用户自定义语法）
let syntax_set = asset::get_syntax_set()?;
```

缓存机制：
- 首次运行：从二进制解压到 `~/.cache/bat/`
- 后续运行：直接从缓存加载
- 用户自定义语法放入 `~/.config/bat/syntaxes/` 后自动编译

## 主题系统

内置多个主题，也可以自定义：

<!-- Simplified from: src/theme.rs:1-30 -->
```bash
bat --list-themes          # 列出所有可用主题
bat --theme=TwoDark file   # 使用特定主题
```

---

[← 上一章](02-input-and-config.md) | [下一章 →](04-git-and-paging.md)
