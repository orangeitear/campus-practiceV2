from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.user import User
from app.schemas.common import success

router = APIRouter(prefix="/api/documents", tags=["文档管理"])

@router.get("")
async def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取文档列表（仅管理员）"""
    # TODO: 实现文档列表查询
    return success(data=[])