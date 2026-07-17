from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.schemas.user import RegisterDTO, LoginDTO, UserResponse
from app.schemas.common import success
from app.services import user_service
from pydantic import BaseModel


router = APIRouter(prefix="/api/user", tags=["用户模块"])
# ✅ 在这里定义 UpdateStatusRequest（在接口之前）
class UpdateStatusRequest(BaseModel):
    is_active: bool

class UpdateRoleRequest(BaseModel):
    role: str

@router.post("/register")
async def register(data: RegisterDTO, db: Session = Depends(get_db)):
    """用户注册"""
    user = user_service.create_user(db, data)
    return success(data=UserResponse.model_validate(user), message="注册成功")


@router.post("/login")
async def login(data: LoginDTO, db: Session = Depends(get_db)):
    """用户登录"""
    from app.core.security import create_access_token
    from app.schemas.common import Result
    
    user = user_service.authenticate_user(db, data.username, data.password)
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    return Result(
        code=200,
        message="登录成功",
        data={"token": token, "user": UserResponse.model_validate(user)}
    )


@router.get("/list")
async def get_user_list(
    keyword: str = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（分页 + 关键字搜索，仅管理员）"""
    result = user_service.get_user_list(db, keyword, page, size)
    result["list"] = [UserResponse.model_validate(u) for u in result["list"]]
    return success(data=result)


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    request_data: UpdateStatusRequest,  # ✅ 从 Body 接收
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户状态"""
    # 查询用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException("用户不存在")
    
    # 不能修改自己的状态（可选）
    if user.id == current_user.id:
        raise BizException("不能修改自己的状态")
    
    # 更新状态
    user.is_active = request_data.is_active
    db.commit()
    db.refresh(user)
    
    return success(data=user)

@router.post("/guest")
async def guest_login(db: Session = Depends(get_db)):
    """游客登录 - 自动创建或获取游客账号"""
    from app.core.security import create_access_token
    
    guest = user_service.get_or_create_guest(db)
    token = create_access_token(data={"sub": str(guest.id), "role": guest.role})
    return success(
        data={"token": token, "user": UserResponse.model_validate(guest)},
        message="游客登录成功"
    )


# ==================== 用户管理（管理员专用）====================

@router.get("/users")
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).all()
    return success(data=[UserResponse.model_validate(u) for u in users])

from pydantic import BaseModel

class UpdateStatusRequest(BaseModel):
    is_active: bool

@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    request_data: UpdateStatusRequest,  # 从 Body 接收
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException("用户不存在")
    
    user.is_active = request_data.is_active
    db.commit()
    db.refresh(user)
    return success(data=user)




@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException("用户不存在")
    
    # 不能删除自己
    if user.id == current_user.id:
        raise BizException("不能删除自己的账号")
    
    db.delete(user)
    db.commit()
    return success(message="用户已删除")

# ✅ 修改更新角色接口
@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    request_data: UpdateRoleRequest,  # 从 Body 接收
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户角色（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException("用户不存在")
    if user.id == current_user.id:
        raise BizException("不能修改自己的角色")
    
    user.role = request_data.role
    db.commit()
    db.refresh(user)
    return success(data=user)
