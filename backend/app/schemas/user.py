from typing import Optional
from datetime import datetime  # 添加这行导入
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
    """用户信息响应模型"""
    id: int
    username: str
    email: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime  # str → datetime

    class Config:
        from_attributes = True
        json_encoders = {  # 添加这个配置，自动将 datetime 转为字符串
            datetime: lambda v: v.isoformat()
        }