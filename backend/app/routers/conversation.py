from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import success

router = APIRouter(prefix="/api/conversations", tags=["对话"])


@router.get("")
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的对话列表"""
    # TODO: 实现对话列表查询
    return success(data=[])