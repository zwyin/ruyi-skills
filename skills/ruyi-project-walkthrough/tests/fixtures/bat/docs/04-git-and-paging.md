# Git 集成与分页器

> bat 如何在文件查看中集成 Git 变更标记和多策略分页。

## Git 集成

bat 使用 `git2` 库（libgit2 的 Rust 绑定）实现原生 Git 支持：

```bash
# 显示 Git 变更标记
bat --style changes src/main.rs
```

输出示例：
```
    1 │ use std::io;          ← 无变更
+   2 │ use clap::Parser;     ← 新增行 (绿色 +)
-   3 │ fn main() {           ← 删除行 (红色 -，与工作树对比)
    4 │     println!("hi");   ← 无变更
```

### 变更检测策略

<!-- Simplified from: src/diff.rs:1-50 -->
```
1. 检查文件是否在 Git 仓库中
2. 比较工作区文件与 HEAD 版本
3. 对每行标记状态: added / removed / modified / unchanged
4. 用 ANSI 颜色在 gutter 区域显示标记
```

如果文件不在 Git 仓库中，变更标记自动跳过，不影响性能。

## 分页器策略

`output.rs` 实现了三种分页模式：

| 模式 | 说明 | 何时使用 |
|------|------|---------|
| **never** | 直接输出到 stdout | 输出内容少，或管道模式 |
| **always** | 总是使用分页器 | 用户显式指定 |
| **auto** | 自动判断 | 默认模式 |

### auto 模式决策逻辑

<!-- Simplified from: src/paging.rs:1-60 -->
```
输出到终端？
  ├─ 否 → 直接输出 (管道/重定向)
  └─ 是 → 输出行数 > 终端高度？
       ├─ 否 → 直接输出
       └─ 是 → 启动分页器
```

### 分页器选择

<!-- Simplified from: src/pager.rs:1-50 + src/output.rs:1-60 -->
```
1. 内置分页器 (minus) — 如果启用了 builtin-pager feature
2. 环境变量 BAT_PAGER — 用户自定义
3. 环境变量 PAGER — 系统 pager
4. less — 默认分页器
   └─ 自动传入 -R (支持 ANSI color) + -F (内容不足一屏不启动)
```

这个设计让 bat 的输出体验像 `git diff` 一样——内容少时直接显示，多时自动分页。

---

[← 上一章](03-syntax-highlighting.md) | [下一章 →](05-innovation-summary.md)
