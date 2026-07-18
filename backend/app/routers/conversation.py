import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.qa_record import QaRecord
from app.schemas.common import success

router = APIRouter(prefix="/api/conversations", tags=["对话"])


def _build_messages(record: QaRecord) -> list:
    """从单条 QaRecord 构建消息列表（一问一答 = 2 条消息）"""
    sources = []
    if record.source_docs:
        try:
            raw = json.loads(record.source_docs)
            sources = [
                {"index": i + 1, "title": s.get("title", ""),
                 "content": s.get("content", ""), "score": s.get("score", 0)}
                for i, s in enumerate(raw)
            ]
        except (json.JSONDecodeError, TypeError):
            pass

    return [
        {"id": record.id * 100, "role": "USER", "content": record.question},
        {"id": record.id * 100 + 1, "role": "ASSISTANT",
         "content": record.answer, "sources": sources},
    ]


@router.get("")
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的对话列表（每条 QaRecord 作为一个单轮对话）"""
    records = (
        db.query(QaRecord)
        .filter(QaRecord.user_id == current_user.id)
        .order_by(desc(QaRecord.created_at))
        .all()
    )
    result = [
        {
            "id": r.id,
            "title": (r.question[:40] + "…") if len(r.question) > 40 else r.question,
            "updated_at": r.created_at.isoformat() if r.created_at else "",
            "message_count": 2,
        }
        for r in records
    ]
    return success(data=result)


@router.get("/{conv_id}")
async def get_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单条对话详情"""
    record = db.query(QaRecord).filter(
        QaRecord.id == conv_id,
        QaRecord.user_id == current_user.id
    ).first()
    if not record:
        from app.schemas.common import error as err_resp
        return err_resp(message="对话不存在", code=404)

    messages = _build_messages(record)
    return success(data={
        "id": record.id,
        "title": (record.question[:40] + "…") if len(record.question) > 40 else record.question,
        "updated_at": record.created_at.isoformat() if record.created_at else "",
        "message_count": 2,
        "messages": messages,
    })


@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除对话记录"""
    record = db.query(QaRecord).filter(
        QaRecord.id == conv_id,
        QaRecord.user_id == current_user.id
    ).first()
    if not record:
        from app.schemas.common import error as err_resp
        return err_resp(message="对话不存在", code=404)

    db.delete(record)
    db.commit()
    return success(message="删除成功")