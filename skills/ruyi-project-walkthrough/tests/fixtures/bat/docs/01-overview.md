# bat 项目走读 — 总览

> 版本: 0.25.x | 作者: David Peter (sharkdp) | 协议: Apache 2.0 / MIT
> 源码: https://github.com/sharkdp/bat
> 走读日期: 2026-05-07

## 一句话概括

bat 是一个用 Rust 写的 cat(1) 替代品——加了语法高亮、Git 集成和分页器，让终端文件查看体验从 1980 年代跳到了现代。

## 核心问题

`cat` 命令 50 年没变——无高亮、无行号、无 Git 感知。终端已经是开发者最常用的界面，为什么查看文件还这么原始？

## 解决方案

```bash
# cat — 无高亮、无行号
cat src/main.rs

# bat — 语法高亮 + 行号 + Git 变更标记 + 自动分页
bat src/main.rs
```

## 项目结构

<!-- Simplified from: ls examples/_src_bat/src/ + examples/_src_bat/Cargo.toml -->
```
bat/
├── src/
│   ├── bin/bat/main.rs     # CLI 入口
│   ├── lib.rs              # 库 API
│   ├── controller.rs       # 主控流程
│   ├── input.rs            # 输入处理（文件/stdin）
│   ├── printer.rs          # 语法高亮引擎
│   ├── output.rs           # 输出 & 分页
│   ├── config.rs           # 配置管理
│   ├── assets/             # 语法 & 主题资源
│   └── syntax_mapping/     # 语言映射规则
├── tests/                  # 集成测试
├── assets/                 # 打包资源（语法集、主题）
└── Cargo.toml              # Rust 项目配置
```

## 技术栈

| 技术 | 用途 |
|------|------|
| **Rust 1.88+** | 核心语言 |
| **syntect** | 语法高亮引擎（TextMate 语法） |
| **clap** | CLI 参数解析 |
| **git2** | Git 集成（可选 feature） |
| **minus** | 内置分页器（可选 feature） |
| **nu-ansi-term** | ANSI 颜色输出 |

## 架构概览

<!-- Simplified from: src/controller.rs:1-50 + src/input.rs:1-30 + src/printer.rs:1-30 + src/output.rs:1-30 -->
```
输入源 (文件/stdin/管道)
  ↓
[Input] — 文件读取 + 编码检测
  ↓
[Config] — 合并 CLI 参数 + 配置文件 + 环境变量
  ↓
[Controller] — 编排整个流程
  ↓
[Printer] — 语法高亮 + 行号 + Git 变更标记
  ↓
[Output] — stdout / 分页器 / 内置分页器
```

---

[下一章 →](02-input-and-config.md)
