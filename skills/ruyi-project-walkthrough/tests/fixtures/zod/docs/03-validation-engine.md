# 验证引擎

> Zod 的验证流程：从用户调用 `.parse()` 到输出结果或错误的完整链路。

## 验证入口

Classic API 层提供了几个入口函数：

<!-- Simplified from: packages/zod/src/v4/core/parse.ts:1-50 -->
```typescript
// packages/zod/src/v4/classic/parse.ts

// 严格模式：失败抛异常
function parse<T extends $ZodType>(schema: T, data: unknown): infer<T>;

// 安全模式：返回结果对象
function safeParse<T extends $ZodType>(schema: T, data: unknown): SafeResult<T>;

// 异步版本（支持 async refine/transform）
function parseAsync<T extends $ZodType>(schema: T, data: unknown): Promise<infer<T>>;
function safeParseAsync<T extends $ZodType>(schema: T, data: unknown): Promise<SafeResult<T>>;
```

## 验证流程

<!-- Simplified from: packages/zod/src/v4/core/parse.ts:50-120 -->
```
input
  ↓
[预处理] coerce — 类型强制转换 (e.g. "42" → 42)
  ↓
[类型检查] 核心校验逻辑
  ↓                         ↓
成功 → 返回 typed data    失败 → 收集 issue
  ↓                         ↓
[后处理]                   构造 $ZodError
  refine — 自定义校验        ├─ issues[] 结构化错误列表
  transform — 数据变换       ├─ tree formatting
  default — 默认值填充       └─ flat formatting
  ↓
返回最终 output
```

## 错误系统 (`$ZodError`)

错误是 Zod 的一等公民，不是简单的字符串：

<!-- Simplified from: packages/zod/src/v4/core/errors.ts:1-80 -->
```typescript
interface $ZodError {
  issues: $ZodIssue[];  // 所有验证问题的列表
}

interface $ZodIssue {
  code: string;         // 错误类型码
  message: string;      // 人类可读消息
  path: (string|number)[];  // 数据路径 e.g. ["user", "email"]
  expected?: string;    // 期望的类型
  received?: string;    // 实际的类型
}
```

错误格式化提供两种视图：

<!-- Simplified from: packages/zod/src/v4/core/errors.ts:200-260 -->
```typescript
// 树形格式（按路径嵌套）
error.format()
// { user: { email: { _errors: ["Invalid email"] } } }

// 扁平格式
error.flatten()
// { formErrors: [], fieldErrors: { "user.email": ["Invalid email"] } }
```

## 国际化

v4 的错误消息支持多语言：

<!-- Simplified from: ls packages/zod/src/v4/locales/ -->
```
v4/locales/
├── en.ts      # 英文
├── zh-CN.ts   # 简体中文
├── ja.ts      # 日文
└── ...        # 其他语言
```

每个 locale 文件导出错误消息映射表，替换默认的英文提示。

## Lazy Method Binding

Zod 使用了一种延迟绑定的优化技巧：

<!-- Simplified from: packages/zod/src/v4/core/core.ts:350-400 -->
```typescript
// 方法首次调用时才绑定到实例
get optional() {
  return /* 新的 optional schema */;
}
```

这样做的好处是：
- 减少实例创建开销（不是每个方法都在构造时生成）
- 保持不可变语义（每次调用返回新实例）
- 用户代码无感知

---

[← 上一章](02-type-system.md) | [下一章 →](04-schema-types.md)
