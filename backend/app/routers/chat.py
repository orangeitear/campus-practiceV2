from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import success
import json

router = APIRouter(prefix="/api/chat", tags=["聊天"])


@router.post("/stream")
async def chat_stream(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """流式聊天接口"""
    # TODO: 实现流式聊天
    # 暂时返回一个示例流
    async def generate():
        yield f"data: {json.dumps({'content': '你好！我是校园问答助手。', 'done': False})}\n\n"
        yield f"data: {json.dumps({'content': '有什么可以帮你的吗？', 'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")