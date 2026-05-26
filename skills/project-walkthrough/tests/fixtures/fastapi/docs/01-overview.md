# FastAPI 项目走读 — 总览

> 版本: 0.115.x | 作者: Sebastián Ramírez | 协议: MIT
> 源码: https://github.com/fastapi/fastapi
> 走读日期: 2026-05-07

## 一句话概括

FastAPI 是一个基于 Python 类型提示的高性能 Web 框架——类型标注就是 API 定义，自动生成文档、校验、序列化。

## 核心问题

传统 Web 框架需要手写三遍：路由代码 + 数据校验 + API 文档。类型标注已经提供了足够的信息，为什么不能自动化？

## 解决方案

```python
@app.get("/users/{user_id}")
async def read_user(user_id: int, q: str | None = None) -> User:
    ...
```

这一个函数定义同时产出：
- 路由匹配（`/users/{user_id}`）
- 参数校验（`user_id` 必须是 int）
- 自动文档（Swagger UI / ReDoc）
- 响应序列化（返回 `User` 模型）

## 项目结构

<!-- Simplified from: ls examples/_src_fastapi/fastapi/ -->
```
fastapi/
├── fastapi/                    # 核心源码
│   ├── applications.py        # FastAPI 主类（继承 Starlette）
│   ├── routing.py             # 路由注册、参数提取
│   ├── dependencies/          # 依赖注入系统
│   ├── openapi/               # OpenAPI schema 生成
│   ├── middleware/            # 中间件（CORS, GZIP 等）
│   ├── security/              # 安全工具（OAuth2, JWT）
│   ├── encoders.py            # JSON 序列化
│   └── exceptions.py          # HTTP 异常
├── docs/                      # 文档站（大量 Markdown）
├── tests/                     # 测试套件
└──pyproject.toml              # 项目配置
```

## 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.10+** | 核心语言，重度使用 type hints |
| **Starlette** | ASGI 基础层（请求/响应/中间件） |
| **Pydantic** | 数据校验 + 序列化 |
| **uvicorn** | ASGI 服务器 |
| **httpx** | 测试 HTTP 客户端 |
| **anyio** | 异步兼容层 |

## 架构概览

```
HTTP 请求
  ↓
[ASGI Server (uvicorn)]
  ↓
[Starlette 中间件栈] — CORS, GZIP, HTTPSRedirect...
  ↓
[FastAPI 路由匹配] — URL pattern → endpoint
  ↓
[依赖注入系统] — 解析参数、校验类型、注入依赖
  ↓
[Endpoint 函数] — 用户写的业务逻辑
  ↓
[响应序列化] — Pydantic model → JSON
  ↓
HTTP 响应 + 自动 OpenAPI 文档
```

---

[下一章 →](02-routing-and-params.md)
