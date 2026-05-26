# 类型系统设计

> Zod 最核心的创新：一套 schema 定义同时产出运行时验证和编译时类型。

## 双层架构

<!-- Simplified from: packages/zod/src/v4/core/core.ts:1-80 + packages/zod/src/v4/classic/ -->
```
┌─────────────────────────────────────┐
│         Classic API 层              │
│  z.string() z.object() z.union()   │  ← 用户写的
├─────────────────────────────────────┤
│         Core 引擎                   │
│  $ZodType, $constructor, parse()   │  ← 内部机制
├─────────────────────────────────────┤
│         TypeScript 类型推断          │
│  z.infer<T>, z.output<T>           │  ← 编译时
└─────────────────────────────────────┘
```

## Core 类型系统 (`v4/core/`)

核心是 `$ZodType` 基类，所有 schema 类型都继承自它：

<!-- Simplified from: packages/zod/src/v4/core/core.ts:80-150 -->
```typescript
// packages/zod/src/v4/core/core.ts
// $ZodType 定义了所有 schema 共享的接口
interface $ZodType {
  _zid: string;           // 唯一 ID
  _def: $ZodDef;          // schema 定义
  parse(input): unknown;  // 同步解析
  safeParse(input): SafeResult;
  optional(): $ZodType;
  nullable(): $ZodType;
  // ...
}
```

`$constructor()` 工厂函数用于创建新的 schema 类型：

<!-- Simplified from: packages/zod/src/v4/core/core.ts:200-250 -->
```typescript
// 通过 $constructor 创建具体类型
const ZodString = $constructor("$ZodString", (inst, def) => {
  // 初始化逻辑
  $ZodType.init(inst, def);
  // 注册验证器
});
```

## 类型推断机制

Zod 利用 TypeScript 的条件类型和映射类型实现自动推断：

<!-- Simplified from: packages/zod/src/v4/core/schemas.ts:1-60 -->
```typescript
// z.infer 的简化实现原理
type infer<T extends $ZodType> =
  T extends $ZodString ? string :
  T extends $ZodNumber ? number :
  T extends $ZodObject<infer Shape> ? { [K in keyof Shape]: infer<Shape[K]> } :
  // ... 递归处理所有类型
  never;
```

用户写 `z.object({ name: z.string() })`，TypeScript 自动推断出 `{ name: string }`，无需手写接口。

## 输入/输出类型分离

v4 引入了 input/output 类型分离：

<!-- Simplified from: packages/zod/src/v4/core/core.ts:300-350 -->
```typescript
const schema = z.object({
  name: z.string(),
  age: z.coerce.number()  // 输入是 string，输出是 number
});

type Input  = z.input<typeof schema>;   // { name: string; age: string | number }
type Output = z.output<typeof schema>;  // { name: string; age: number }
```

这解决了 coerce/transform 场景下输入输出类型不同的问题。

## 不可变 API

每个方法调用都返回新的 schema 实例，不修改原实例：

<!-- Simplified from: packages/zod/src/v4/core/api.ts:1-50 -->
```typescript
const base = z.string();
const optional = base.optional(); // 新实例，base 不变
const withDefault = optional.default("hello"); // 又一个新实例
```

---

[← 上一章](01-overview.md) | [下一章 →](03-validation-engine.md)
