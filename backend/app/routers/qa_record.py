from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.qa_record import QaRecord
from app.schemas.qa_record import QaRecordResponse, QaRecordListData
from app.schemas.common import success
from app.core.exceptions import BizException

router = APIRouter(prefix="/api/chat", tags=["问答记录"])


@router.get("/history")
async def get_chat_history(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的问答历史记录"""
    query = db.query(QaRecord).filter(QaRecord.user_id == current_user.id)
    total = query.count()
    items = query.order_by(QaRecord.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    result = {
        "total": total,
        "page": page,
        "size": size,
        "list": [QaRecordResponse.model_validate(item) for item in items]
    }
    return success(data=QaRecordListData(**result))


@router.delete("/history/{record_id}")
async def delete_chat_history(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除当前用户的问答记录"""
    record = db.query(QaRecord).filter(QaRecord.id == record_id).first()
    if not record:
        raise BizException(code=404, message="记录不存在")
    if record.user_id != current_user.id:
        raise BizException(code=403, message="无权删除此记录")
    
    db.delete(record)
    db.commit()
    return success(message="删除成功")