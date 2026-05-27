# 依赖注入系统

> FastAPI 最强大的设计模式——声明式依赖解析，支持嵌套和异步。

## 核心概念

`Depends()` 让你声明 endpoint 需要什么，框架自动解析和注入：

<!-- Simplified from: fastapi/dependencies/utils.py:1-50 -->
```python
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

## 解析流程

<!-- Simplified from: fastapi/dependencies/utils.py:1-50 -->
```
Endpoint 函数签名
  ↓
[分析每个参数]
  ↓
遇到 Depends(fn)
  ↓
执行 fn，获取返回值
  ↓
如果 fn 本身也有 Depends 参数 → 递归解析
  ↓
所有依赖解析完毕 → 执行 endpoint
  ↓
[清理阶段] yield 依赖的 finally 块执行
```

## 嵌套依赖

依赖可以依赖其他依赖，形成 DAG：

<!-- Simplified from: fastapi/dependencies/utils.py:1-50 -->
```python
def get_token(header: str = Header()):
    # 解析 token
    return token

def get_current_user(token: str = Depends(get_token), db = Depends(get_db)):
    # 用 token 查用户
    return user

@app.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user
```

FastAPI 自动按拓扑顺序解析：`get_token` → `get_db` → `get_current_user` → `me`。

## 全局依赖

可以在路由器和应用级别声明依赖，每个请求都会执行：

<!-- Simplified from: fastapi/dependencies/utils.py:1-50 -->
```python
app = FastAPI(dependencies=[Depends(verify_api_key)])
router = APIRouter(dependencies=[Depends(check_permissions)])
```

## 依赖缓存

同一请求内，同一依赖只执行一次（结果缓存）。这是性能优化——不会重复查数据库或重复验证 token。

---

[← 上一章](02-routing-and-params.md) | [下一章 →](04-openapi-generation.md)
