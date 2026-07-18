from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.core.exception_handler import (
    biz_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.core.exceptions import BizException
from app.schemas.common import success
from app.routers import user  # 新增
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import conversation
from app.routers import chat
from app.routers import document



app = FastAPI(
    title="Campus QA Backend",
    description="校园问答助手后端 API",
    version="1.0.0"
)

# 创建数据库表
Base.metadata.create_all(bind=engine)
app.include_router(conversation.router)
app.include_router(chat.router)

# 注册路由
app.include_router(user.router)
app.include_router(document.router)
# app.include_router(user.admin_router)
# 配置 CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(BizException, biz_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
def root():
    return success(message="Campus QA Backend is running")


@app.get("/health")
def health_check():
    return success(message="ok")