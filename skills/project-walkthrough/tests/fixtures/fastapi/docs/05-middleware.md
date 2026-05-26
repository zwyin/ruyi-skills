# 中间件与安全

> FastAPI 继承 Starlette 的中间件栈 + 自带安全工具。

## 内置中间件

```
fastapi/middleware/
├── cors.py            # 跨域资源共享
├── gzip.py            # GZIP 压缩
├── httpsredirect.py   # HTTP → HTTPS 重定向
├── trustedhost.py     # 信任主机头
└── wsgi.py            # WSGI 应用挂载
```

中间件是洋葱模型，请求从外到内，响应从内到外：

```
[CORS 中间件] → [GZIP 中间件] → [路由] → [endpoint]
     ←              ←            ←
```

### CORS 配置

<!-- Simplified from: fastapi/middleware/ -->
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 安全模块

`fastapi/security/` 提供了常见的认证方案：

| 模块 | 用途 |
|------|------|
| `oauth2.py` | OAuth2 密码流、授权码流 |
| `http.py` | HTTP Basic/Digest 认证 |
| `api_key.py` | API Key (header/query/cookie) |
| `jwt.py` | JWT Bearer token |

这些安全工具返回 `Depends()` 兼容的依赖，直接注入 endpoint：

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/me")
async def me(token: str = Depends(oauth2_scheme)):
    # token 自动从 Authorization header 提取
    return decode_token(token)
```

## 异常处理

FastAPI 统一了 HTTP 异常和请求校验错误：

```python
# 主动抛出
raise HTTPException(status_code=404, detail="Item not found")

# Pydantic 校验失败自动返回 422:
{
    "detail": [
        {
            "loc": ["body", "price"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

---

[← 上一章](04-openapi-generation.md) | [下一章 →](06-innovation-summary.md)
