
# Day2 技术设计文档

**文档版本**：v1.0  
**日期**：2026-07-16  
**作者**：陈梦  


## 一、FastAPI 分层架构

项目采用三层架构，各层职责如下：

| 层级 | 目录 | 职责 |
|------|------|------|
| 路由层（Router） | `app/routers/` | 接收 HTTP 请求，参数校验，调用 Service 层 |
| 业务层（Service） | `app/services/` | 核心业务逻辑，数据库操作 |
| 数据模型层（Model） | `app/models/` | SQLAlchemy ORM 模型，表结构定义 |
| Schema 层 | `app/schemas/` | Pydantic 请求/响应模型，数据校验 |

**调用链**：

```
前端请求 → routers/ → services/ → models/ → 数据库
              ↓
         schemas/ 进行数据校验
```

**代码示例**：

```python
# 路由层（routers/user.py）
@router.post("/register")
async def register(data: RegisterDTO, db: Session = Depends(get_db)):
    user = user_service.create_user(db, data)
    return success(data=UserResponse.model_validate(user))

# 业务层（services/user_service.py）
def create_user(db: Session, data: RegisterDTO) -> User:
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise BizException(code=400, message="用户名已存在")
    # 创建用户...

# 数据模型层（models/user.py）
class User(Base):
    __tablename__ = "sys_user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)

# Schema层（schemas/user.py）
class RegisterDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=20)
```


## 二、统一响应规范

### 响应模型定义（`schemas/common.py`）

所有接口返回统一格式：

```python
class Result(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    timestamp: datetime = datetime.now()
```

### 工厂函数

```python
def success(data: Any = None, message: str = "success") -> dict:
    return Result(code=200, message=message, data=data).model_dump()

def error(message: str = "error", code: int = 400) -> dict:
    return Result(code=code, message=message, data=None).model_dump()
```

### 响应示例

**成功时**：
```json
{
  "code": 200,
  "message": "注册成功",
  "data": { "id": 1, "username": "test" },
  "timestamp": "2026-07-16T17:00:00"
}
```

**失败时**：
```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null,
  "timestamp": "2026-07-16T17:00:00"
}
```

### 状态码说明

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 参数错误 / 业务异常 |
| 401 | 未认证 / Token 失效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |


## 三、全局异常处理

### 自定义异常基类（`core/exceptions.py`）

```python
class BizException(Exception):
    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message
        super().__init__(self.message)

# 具体异常子类
class NotFoundException(BizException): ...      # 404
class UnauthorizedException(BizException): ...  # 401
class ForbiddenException(BizException): ...     # 403
class ValidationException(BizException): ...    # 400
```

### 异常处理器（`core/exception_handler.py`）

| 异常类型 | 处理器函数 | 处理方式 |
|----------|-----------|----------|
| `BizException` | `biz_exception_handler` | 返回自定义 code 和 message |
| `RequestValidationError` | `validation_exception_handler` | 返回 400，拼接校验失败字段 |
| `StarletteHTTPException` | `http_exception_handler` | 返回对应 HTTP 状态码 |
| `Exception`（兜底） | `general_exception_handler` | 返回 500，记录错误信息 |

### 注册方式（在 `main.py` 中）

```python
app.add_exception_handler(BizException, biz_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

### 异常处理流程

```
请求 → 路由层 → Service 层
                    ↓
              发生异常？
             /          \
            否           是
            ↓             ↓
          返回成功    抛出 BizException
                           ↓
                exception_handler 捕获
                           ↓
                  返回统一错误格式
```


## 四、依赖注入（Depends）

### 数据库会话注入（`core/database.py`）

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 认证依赖链（`core/deps.py`）

```
HTTPBearer → get_current_user → get_current_admin_user
   (提取Token)    (解析Token+查用户)    (校验角色)
```

**代码示例**：

```python
# 仅需登录的接口
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    ...

# 仅管理员可访问的接口
@router.get("/list")
async def get_user_list(
    current_user: User = Depends(get_current_admin_user)
):
    ...
```


## 五、配置管理（`core/config.py`）

使用 `pydantic-settings` 从 `.env` 文件读取配置：

```python
class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "sqlite:///./campus_qa.db"
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # DashScope
    DASHSCOPE_API_KEY: str
    # RAG 参数
    TOP_K: int = 5
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    class Config:
        env_file = ".env"

settings = Settings()
```
