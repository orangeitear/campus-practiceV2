from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Result(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


def success(data: Any = None, message: str = "success") -> dict:
    return Result(code=200, message=message, data=data).model_dump(mode="json")


def error(message: str = "error", code: int = 400) -> dict:
    return Result(code=code, message=message, data=None).model_dump(mode="json")


def unauthorized(message: str = "未授权，请先登录") -> dict:
    return Result(code=401, message=message, data=None).model_dump(mode="json")


def forbidden(message: str = "无权限访问") -> dict:
    return Result(code=403, message=message, data=None).model_dump(mode="json")


def not_found(message: str = "资源不存在") -> dict:
    return Result(code=404, message=message, data=None).model_dump(mode="json")