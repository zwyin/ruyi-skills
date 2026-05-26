# 路由系统与参数提取

> FastAPI 的核心：类型标注驱动的路由注册和自动参数解析。

## 路由注册

`applications.py` 中的 `FastAPI` 类继承自 Starlette，在此基础上增加了参数自动提取：

```python
# fastapi/applications.py — 核心装饰器
class FastAPI(Starlette):
    def get(self, path: str, **kwargs):
        return self.router.add_api_route(path, **kwargs)
```

`routing.py` 的 `APIRouter` 负责实际的注册逻辑：

```python
# fastapi/routing.py
class APIRouter:
    def add_api_route(self, path, endpoint, ...):
        # 1. 解析函数签名，提取参数
        # 2. 根据类型标注决定参数来源 (path/query/body/header)
        # 3. 注册路由到 Starlette
```

## 参数来源自动推断

FastAPI 根据参数的默认值和类型自动判断参数来源：

| 参数形式 | 来源 | 示例 |
|---------|------|------|
| `{param}` 在路径中 | Path | `user_id: int` |
| 有默认值 | Query | `q: str = None` |
| 类型是 Pydantic Model | Body | `item: Item` |
| `Header()` 包装 | Header | `user_agent: str = Header()` |
| `Cookie()` 包装 | Cookie | `session: str = Cookie()` |
| `Depends()` 包装 | 依赖注入 | `db: Session = Depends(get_db)` |

## 请求体校验

当参数类型是 Pydantic Model 时，FastAPI 自动：
1. 读取请求体 JSON
2. 用 Pydantic 校验每个字段
3. 校验失败返回 422 + 详细错误信息
4. 校验成功传入 typed 对象

```python
class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
    tags: list[str] = []

@app.post("/items/")
async def create_item(item: Item):  # 自动从 body 解析 + 校验
    return item
```

## 响应模型

返回类型标注控制响应序列化和文档生成：

<!-- Simplified from: fastapi/routing.py:200-260 -->
```python
@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int) -> UserResponse:
    return user  # 自动序列化，过滤多余字段
```

`response_model` 同时影响：
- OpenAPI schema 中的响应定义
- 实际响应的数据过滤（只返回 model 中定义的字段）
- 响应状态码

---

[← 上一章](01-overview.md) | [下一章 →](03-dependency-injection.md)
