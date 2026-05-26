# Zod 项目走读 — 总览

> 版本: 4.x | 作者: Colin McDonnell | 协议: MIT
> 源码: https://github.com/colinhacks/zod
> 走读日期: 2026-05-07

## 一句话概括

Zod 是一个 TypeScript 优先的 schema 验证库——定义 schema 既做运行时校验，又自动推断出编译时类型，一个定义两处生效。

## 核心问题

JavaScript/TypeScript 项目中，外部数据（API 响应、表单输入、配置文件）的类型安全怎么保证？TypeScript 只在编译时检查，运行时的 `any` 毫无防护。

## 解决方案

<!-- Simplified from: packages/zod/src/v4/core/core.ts:1-50 -->
```
z.object({ name: z.string(), age: z.number() })
  ↓ 编译时
type Person = { name: string; age: number }  ← 自动推断
  ↓ 运行时
schema.parse(input)  ← 校验 + 类型窄化
```

一个 schema 定义同时产出：
- 运行时验证逻辑（parse/safeParse）
- 编译时 TypeScript 类型（通过类型推断）

## 项目结构

<!-- Simplified from: ls packages/zod/src/v4/ + packages/zod/package.json -->
```
zod/
├── packages/
│   ├── zod/                    # 主包
│   │   ├── src/
│   │   │   ├── v4/             # 当前版本
│   │   │   │   ├── core/       # 核心引擎 + 类型系统
│   │   │   │   ├── classic/    # 经典 API 层
│   │   │   │   ├── locales/    # 国际化错误消息
│   │   │   │   └── mini/       # 最小化 bundle
│   │   │   └── v3/             # 旧版（兼容）
│   │   └── package.json
│   ├── bench/                  # 性能基准
│   ├── docs/                   # 文档站
│   └── integration/            # 集成测试
├── pnpm-workspace.yaml
└── package.json
```

## 技术栈

| 技术 | 用途 |
|------|------|
| **TypeScript** | 核心语言，ES modules |
| **pnpm** | monorepo 管理 + workspace |
| **esbuild / rollup** | 构建打包 |
| **Vitest** | 测试框架 |
| **Biome** | lint + format |
| **零外部依赖** | 核心包无任何 runtime dependency |

## 核心工作流

<!-- Simplified from: packages/zod/src/v4/core/parse.ts:1-50 + packages/zod/src/v4/core/schemas.ts:1-50 -->
```
定义 Schema (z.object, z.string, ...)
    ↓
.parse(data)          → 成功返回 typed data / 失败抛 ZodError
.safeParse(data)      → 返回 { success, data, error }
.parseAsync(data)     → 异步版本（支持 async refine）
    ↓
类型推断: z.infer<typeof schema> 自动得到 TypeScript 类型
```

---

[下一章 →](02-type-system.md)
