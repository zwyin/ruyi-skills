# 创新总结与行业影响

> FastAPI 重新定义了 Python Web 框架的开发体验——类型标注即 API。

## 五大创新

### 1. 类型标注驱动的 API 开发

Python 的 type hints 不只是注解，而是框架的配置语言：

```python
async def read_user(user_id: int, q: str | None = None) -> User:
```

这一行定义了路由、参数来源、校验规则、响应类型、API 文档——传统框架需要 5 处配置。

### 2. 自动 OpenAPI 文档

零维护成本的交互式 API 文档。代码改了，文档自动跟着改。消除了"文档和代码不一致"的经典问题。

### 3. 声明式依赖注入

`Depends()` 实现了声明式 IoC——endpoint 只声明需要什么，框架负责解析、注入、清理。支持嵌套、异步、生成器（yield + finally 清理）。

### 4. Pydantic 深度集成

请求体校验、响应序列化、JSON Schema 生成全部委托给 Pydantic。FastAPI 专注路由和依赖注入，不做重复的校验逻辑。

### 5. 异步优先的 ASGI 设计

基于 Starlette 的 ASGI 架构，原生支持 async/await。同一套代码可以跑同步和异步，不需要额外配置。

## 竞品对比

| 维度 | FastAPI | Flask | Django | Starlette |
|------|---------|-------|--------|-----------|
| 异步支持 | 原生 | 需扩展 | 部分支持 | 原生 |
| 自动文档 | 内置 | 需扩展 | 需扩展 | 无 |
| 类型校验 | Pydantic | 手动 | 手动 | 无 |
| 依赖注入 | 内置 | 无 | 无 | 无 |
| 性能 | 极高 | 中等 | 中等 | 极高 |
| 学习曲线 | 低 | 低 | 中 | 中 |

## 适用场景

最适合：API 服务、微服务、实时应用（WebSocket）、数据科学服务端。
不太适合：服务端渲染 HTML、CMS、需要 Django admin 的项目。

---

[← 上一章](05-middleware.md)
