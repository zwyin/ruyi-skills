# OpenAPI 自动生成

> 代码即文档——从类型标注自动产出 Swagger UI + ReDoc + OpenAPI JSON。

## 生成流程

<!-- Simplified from: fastapi/openapi/docs.py:1-50 -->
```
FastAPI 启动
  ↓
遍历所有注册的 route
  ↓
对每个 endpoint:
  ├─ 分析函数签名 → 提取参数定义
  ├─ 分析 Pydantic model → 生成 JSON Schema
  ├─ 分析响应类型 → 生成响应 schema
  └─ 读取默认值/Field 描述 → 填充元数据
  ↓
合并为 OpenAPI 3.x spec (JSON)
  ↓
/swagger/docs     → Swagger UI
/redoc            → ReDoc
/openapi.json     → 原始 JSON
```

## 核心模块

`openapi/utils.py` 中的 `get_openapi` 函数负责整个生成过程：

<!-- Simplified from: fastapi/openapi/docs.py:1-50 -->
```python
# 简化逻辑
def get_openapi(title, version, routes):
    openapi_schema = {
        "openapi": "3.1.0",
        "info": {"title": title, "version": version},
        "paths": {},
        "components": {"schemas": {}}
    }
    for route in routes:
        # 从 endpoint 函数签名提取参数
        # 从 Pydantic model 生成 schema
        # 添加到 paths 和 components
    return openapi_schema
```

## Pydantic → JSON Schema 转换

每个 Pydantic Model 自动转换为 JSON Schema：

<!-- Simplified from: fastapi/openapi/utils.py:200-260 -->
```python
class Item(BaseModel):
    name: str = Field(description="物品名称")
    price: float = Field(gt=0, description="价格")

# 自动生成:
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "string", "description": "物品名称"},
#     "price": {"type": "number", "exclusiveMinimum": 0, "description": "价格"}
#   },
#   "required": ["name", "price"]
# }
```

## 自定义 OpenAPI

可以完全覆盖默认生成：

<!-- Simplified from: fastapi/openapi/docs.py:1-50 -->
```python
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(...)
    # 自定义修改
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

[← 上一章](03-dependency-injection.md) | [下一章 →](05-middleware.md)
