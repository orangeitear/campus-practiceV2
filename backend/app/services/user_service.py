from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.schemas.user import RegisterDTO
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import BizException


def create_user(db: Session, data: RegisterDTO) -> User:
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise BizException(code=400, message="用户名已存在")
    
    # 检查邮箱是否已存在
    if data.email:
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise BizException(code=400, message="邮箱已被使用")
    
    # 创建新用户
    hashed_password = get_password_hash(data.password)
    user = User(
        username=data.username,
        password=hashed_password,
        email=data.email,
        role="user",  # 默认普通用户
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User:
    """用户登录验证"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise BizException(code=401, message="用户名或密码错误")
    if not verify_password(password, user.password):
        raise BizException(code=401, message="用户名或密码错误")
    if not user.is_active:
        raise BizException(code=403, message="账号已被禁用")
    return user


def get_user_list(db: Session, keyword: str = None, page: int = 1, size: int = 10):
    """获取用户列表（分页 + 关键字搜索）"""
    query = db.query(User)
    
    # 关键字搜索（用户名或邮箱）
    if keyword:
        query = query.filter(
            or_(
                User.username.contains(keyword),
                User.email.contains(keyword)
            )
        )
    
    # 分页
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "list": users
    }


def get_user_by_id(db: Session, user_id: int) -> User:
    """根据 ID 获取用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException(code=404, message="用户不存在")
    return user


def update_user_status(db: Session, user_id: int, is_active: bool) -> User:
    """更新用户状态（启用/禁用）"""
    user = get_user_by_id(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user