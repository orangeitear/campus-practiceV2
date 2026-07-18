from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterDTO(BaseModel):
    """注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class LoginDTO(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应模型（不包含密码）"""
    id: int
    username: str
    email: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime  # ✅ 改为 datetime 类型

    class Config:
        from_attributes = True