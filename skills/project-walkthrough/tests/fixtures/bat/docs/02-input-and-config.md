# 输入处理与配置系统

> bat 如何处理多种输入源和三层配置合并。

## 输入源

`input.rs` 负责处理多种输入来源：

| 输入类型 | 处理方式 |
|---------|---------|
| 文件路径 | 直接读取，检测编码 |
| stdin/管道 | 缓冲读取 |
| 目录 | 跳过，提示 |
| `-` (显式 stdin) | 与 stdin 相同 |
| 内联脚本 `<<<` | shell 展开后读取 |

编码检测：优先尝试 UTF-8，失败后用无损转换保证不丢数据。

## 配置系统

`config.rs` 实现了三层配置合并：

<!-- Simplified from: src/config.rs:37-100 -->
```
优先级从高到低:
1. CLI 参数 (--style, --theme, --paging 等)
2. 环境变量 (BAT_STYLE, BAT_THEME, BAT_PAGER 等)
3. 配置文件 (~/.config/bat/config)
```

配置文件是简单的 key=value 格式：

```
# ~/.config/bat/config
--theme="TwoDark"
--style="full"
--paging="auto"
--map-syntax ".conf:JSON"
```

## Style 组件

bat 的 `--style` 参数支持组合多个组件：

<!-- Simplified from: src/style.rs:8-60 -->
```bash
# 只显示行号和高亮
bat --style numbers,highlight

# 完整样式（默认）
bat --style full
# = header + grid + numbers + changes + snip
```

| 组件 | 作用 |
|------|------|
| `numbers` | 行号 |
| `header` | 文件名头部 |
| `grid` | 行分隔线 |
| `changes` | Git 变更标记 |
| `snip` | 长文件省略标记 |

---

[← 上一章](01-overview.md) | [下一章 →](03-syntax-highlighting.md)
