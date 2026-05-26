# 微型 Bundle 架构

> Zod v4 的分层设计：core 仅 2KB gzip，classic 完整 API，mini 按需裁剪。

## 分层策略

<!-- Simplified from: packages/zod/src/v4/index.ts:1-30 + packages/zod/package.json -->
```
┌─────────────────────────────────────────────┐
│  zod (classic)                              │
│  完整 API: z.string(), z.object(), ...      │
│  适合大多数场景                               │
├─────────────────────────────────────────────┤
│  zod/mini                                   │
│  最小化子集: z.string(), z.object() 等       │
│  去掉错误格式化、coerce 等非核心功能           │
├─────────────────────────────────────────────┤
│  zod/core                                   │
│  核心引擎: $ZodType, parse(), $ZodError      │
│  ~2KB gzip                                  │
└─────────────────────────────────────────────┘
```

## Core 层 (`v4/core/`)

Core 层只包含最基础的抽象：

<!-- Simplified from: packages/zod/src/v4/core/index.ts:1-30 -->
```typescript
// 核心导出
export { $ZodType } from "./core";        // 基类
export { $constructor } from "./core";    // 类型工厂
export { $ZodError, $ZodIssue } from "./error";  // 错误
export { parse, safeParse } from "./parse";       // 解析
```

不包含具体类型（没有 `ZodString`、`ZodNumber` 等），只有类型系统的基础设施。

## Classic 层 (`v4/classic/`)

Classic 层在 core 之上构建完整的用户 API：

<!-- Simplified from: ls packages/zod/src/v4/classic/ -->
```
v4/classic/
├── string.ts      # z.string()
├── number.ts      # z.number()
├── boolean.ts     # z.boolean()
├── object.ts      # z.object()
├── array.ts       # z.array()
├── union.ts       # z.union() + z.discriminatedUnion()
├── record.ts      # z.record()
├── tuple.ts       # z.tuple()
├── enum.ts        # z.enum()
├── native-enum.ts # z.nativeEnum()
├── effects.ts     # refine / transform / preprocess
├── coerce.ts      # 类型强制转换
├── brand.ts       # 名义类型
├── parse.ts       # parse / safeParse / async 版本
├── error.ts       # 错误格式化
└── external.ts    # 重新导出所有类型
```

## Mini 层 (`v4/mini/`)

针对 bundle size 敏感的场景（浏览器、边缘计算）：

<!-- Simplified from: packages/zod/src/v4/mini/index.ts:1-30 -->
```typescript
// 从 mini 导入 — 只打包用到的类型
import { z } from "zod/mini";

const schema = z.object({
  name: z.string(),
  age: z.number(),
});
```

Mini 裁掉了：
- 错误格式化（format/flatten）
- Coercion
- Branded types
- JSON Schema 互转
- 国际化

## Tree-shaking 设计

Zod v4 的模块化设计天然支持 tree-shaking：

<!-- Simplified from: packages/zod/src/v4/classic/external.ts:1-20 -->
```typescript
// 只导入 string 和 object，不会打包 array/union/...
import { z } from "zod";
z.string(); // 只打包 string 相关代码
```

每个类型是独立模块，bundler 可以精确地只打包用到的类型。

## 与 v3 的对比

| 维度 | v3 | v4 |
|------|----|----|
| 架构 | 单体 | core + classic + mini |
| Core gzip | ~13KB | ~2KB |
| Bundle 策略 | 无分层 | 三层可选 |
| 模块化 | 全量导入 | per-type 模块 |
| 向后兼容 | — | v3 作为子集保留 |

---

[← 上一章](04-schema-types.md) | [下一章 →](06-innovation-summary.md)
