from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.core.exceptions import BizException

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise BizException(code=401, message="无效的 Token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise BizException(code=401, message="无效的 Token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise BizException(code=401, message="用户不存在")
    if not user.is_active:
        raise BizException(code=403, message="账号已被禁用")
    
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前登录用户，并校验是否为管理员"""
    if current_user.role != "admin":
        raise BizException(code=403, message="无权限访问，需要管理员权限")
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前登录用户（可选，未登录返回 None）"""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except BizException:
        return None