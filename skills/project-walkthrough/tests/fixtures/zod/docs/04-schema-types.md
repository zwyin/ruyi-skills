# Schema 类型体系

> Zod 提供的完整类型动物园——从基础类型到高级组合子。

## 基础类型

| Schema | TypeScript 类型 | 用途 |
|--------|----------------|------|
| `z.string()` | `string` | 字符串，支持 min/max/email/url/uuid 等约束 |
| `z.number()` | `number` | 数字，支持 int/positive/negative/finite |
| `z.boolean()` | `boolean` | 布尔值 |
| `z.bigint()` | `bigint` | 大整数 |
| `z.date()` | `Date` | 日期对象 |
| `z.symbol()` | `symbol` | Symbol |
| `z.undefined()` | `undefined` | undefined |
| `z.null()` | `null` | null |
| `z.any()` | `any` | 任意值 |
| `z.unknown()` | `unknown` | 未知类型 |
| `z.void()` | `void` | void |
| `z.never()` | `never` | 永不匹配 |

## 复合类型

### Object

<!-- Simplified from: packages/zod/src/v4/core/schemas.ts:300-380 -->
```typescript
const User = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
});
```

Object schema 支持：
- `.extend()` / `.merge()` — 扩展字段
- `.pick()` / `.omit()` — 选择/排除字段
- `.partial()` — 所有字段变 optional
- `.required()` — 所有字段变 required
- `.strict()` — 禁止多余字段

### Array / Tuple

<!-- Simplified from: packages/zod/src/v4/core/schemas.ts:500-560 -->
```typescript
z.array(z.string());              // string[]
z.tuple([z.string(), z.number()]); // [string, number]
z.record(z.string(), z.number()); // Record<string, number>
```

### Union / Discriminated Union

<!-- Simplified from: packages/zod/src/v4/core/schemas.ts:600-660 -->
```typescript
// 普通联合
z.union([z.string(), z.number()]);

// 鉴别联合（性能更优，按 discriminator 字段分发）
z.discriminatedUnion("type", [
  z.object({ type: z.literal("success"), data: z.any() }),
  z.object({ type: z.literal("error"), message: z.string() }),
]);
```

## 高级特性

### Branded Types

名义类型（nominal typing），让 TypeScript 区分结构相同但语义不同的类型：

<!-- Simplified from: packages/zod/src/v4/core/api.ts:900-940 -->
```typescript
const BrandEmail = z.string().email().brand<"Email">();
type Email = z.infer<typeof BrandEmail>; // string & Brand<"Email">

// Email 不能赋给普通 string，需要通过验证才能获得
```

### Coercion

输入自动强制转换类型：

<!-- Simplified from: packages/zod/src/v4/core/api.ts:74-100 -->
```typescript
z.coerce.string();  // 123 → "123"
z.coerce.number();  // "42" → 42
z.coerce.date();    // "2024-01-01" → Date
z.coerce.boolean(); // "true" → true
```

### Transform / Refine

<!-- Simplified from: packages/zod/src/v4/core/api.ts:1430-1480 -->
```typescript
z.string()
  .transform((val) => val.trim().toLowerCase())  // 数据变换
  .refine((val) => val.length > 0, "不能为空")     // 自定义校验
  .pipe(z.email());                               // 链式组合
```

### JSON Schema 互转

v4 内置了 JSON Schema 的双向转换：

<!-- Simplified from: packages/zod/src/v4/core/json-schema.ts:1-40 -->
```typescript
z.toJsonSchema(schema);  // Zod schema → JSON Schema
z.fromJsonSchema(json);  // JSON Schema → Zod schema
```

这使 Zod 可以与任何支持 JSON Schema 的工具集成（OpenAPI、FastAPI、Prisma 等）。

---

[← 上一章](03-validation-engine.md) | [下一章 →](05-micro-bundle.md)
