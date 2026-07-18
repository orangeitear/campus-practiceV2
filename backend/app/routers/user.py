import traceback
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import RegisterDTO, LoginDTO, UserResponse, UpdateStatusDTO, UpdateRoleDTO
from app.schemas.common import success
from app.services import user_service

router = APIRouter(prefix="/api/user", tags=["用户模块"])


@router.post("/register")
async def register(data: RegisterDTO, db: Session = Depends(get_db)):
    """用户注册"""
    print(f"=== 注册请求: username={data.username}, email={data.email} ===")
    user = user_service.create_user(db, data)
    print(f"=== 注册成功: {user.username}, id={user.id} ===")
    return success(data=UserResponse.model_validate(user), message="注册成功")


@router.post("/login")
async def login(data: LoginDTO, db: Session = Depends(get_db)):
    """用户登录"""
    print("=== 进入 login 路由 ===")
    print(f"=== 收到的数据: {data} ===")
    try:
        from app.core.security import create_access_token
        user = user_service.authenticate_user(db, data.username, data.password)
        print(f"=== 用户验证通过: {user.username}, role={user.role} ===")
        token = create_access_token(data={"sub": str(user.id), "role": user.role})
        print(f"=== Token 生成成功 ===")
        return success(data={"token": token, "user": UserResponse.model_validate(user)}, message="登录成功")
    except Exception as e:
        print(f"=== 登录异常 ===")
        print(traceback.format_exc())
        raise


@router.get("/users")
async def get_user_list(
    keyword: str = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（仅管理员）"""
    result = user_service.get_user_list(db, keyword, page, size)
    result["list"] = [UserResponse.model_validate(u) for u in result["list"]]
    return success(data=result)


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    data: UpdateStatusDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """启用/禁用用户（仅管理员）"""
    user = user_service.update_user_status(db, user_id, data.is_active)
    return success(data=UserResponse.model_validate(user), message="状态更新成功")


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    data: UpdateRoleDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """修改用户角色（仅管理员）"""
    user = user_service.update_user_role(db, user_id, data.role)
    return success(data=UserResponse.model_validate(user), message="角色更新成功")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除用户（仅管理员）"""
    user_service.delete_user(db, user_id)
    return success(message="用户已删除")