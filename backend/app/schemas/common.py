from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel


class Result(BaseModel):
    """统一响应模型"""
    
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    timestamp: datetime = datetime.now()


def success(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return Result(code=200, message=message, data=data).model_dump()


def error(message: str = "error", code: int = 400) -> dict:
    """错误响应"""
    return Result(code=code, message=message, data=None).model_dump()


def unauthorized(message: str = "未授权，请先登录") -> dict:
    """401 未授权响应"""
    return Result(code=401, message=message, data=None).model_dump()


def forbidden(message: str = "无权限访问") -> dict:
    """403 无权限响应"""
    return Result(code=403, message=message, data=None).model_dump()


def not_found(message: str = "资源不存在") -> dict:
    """404 资源不存在响应"""
    return Result(code=404, message=message, data=None).model_dump()