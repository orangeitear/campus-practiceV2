import json
import traceback
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.qa_record import QaRecord
from app.schemas.chat import ChatRequest, ChatResponse, SourceDoc
from app.schemas.common import success
from app.core.llm_client import llm_client
from app.core.prompt import build_prompt
from app.core.rag_service import search_documents as search_endpoint
from app.ai.vector_store import vector_store

router = APIRouter(prefix="/api/chat", tags=["问答接口"])


@router.post("")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """同步问答接口"""
    # 1. 检索
    results = search_endpoint(request.question, top_k=5)

    # 2. 构建 Prompt
    messages = build_prompt(request.question, results)

    # 3. 调用 LLM
    answer = await llm_client.chat(messages)

    # 4. 整理来源
    sources = [
        SourceDoc(
            content=r.get("content", ""),
            doc_id=r.get("doc_id", 0),
            title=r.get("title", "未知文档"),
            score=r.get("score", 0.0)
        )
        for r in results
    ]

    # 5. 保存问答记录
    record = QaRecord(
        user_id=current_user.id,
        question=request.question,
        answer=answer,
        source_docs=json.dumps([s.model_dump() for s in sources], ensure_ascii=False)
    )
    db.add(record)
    db.commit()

    return success(data=ChatResponse(answer=answer, sources=sources))


@router.get("/stream")
async def chat_stream(
    question: str = Query(..., description="用户问题"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """SSE 流式问答接口"""
    async def generate() -> AsyncGenerator[str, None]:
        try:
            # 1. 检索
            results = search_endpoint(question, top_k=5)
            print(f"=== 检索结果: {len(results)} 条, FAISS总数: {vector_store.total_count} ===")
            for i, r in enumerate(results):
                print(f"  [{i}] doc_id={r.get('doc_id')}, score={r.get('score'):.4f}, content={r.get('content','')[:60]}...")

            # 2. 构建 Prompt
            messages = build_prompt(question, results)

            # 3. 整理来源
            sources = [
                {"content": r.get("content", ""), "doc_id": r.get("doc_id", 0),
                 "title": r.get("title", "未知文档"), "score": r.get("score", 0.0)}
                for r in results
            ]

            # 4. 发送 meta 事件（来源信息）
            yield f"event: meta\ndata: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"

            # 5. 流式生成
            full_answer = ""
            async for token in llm_client.chat_stream(messages):
                full_answer += token
                yield f"event: token\ndata: {json.dumps({'text': token}, ensure_ascii=False)}\n\n"

            # 6. 保存记录
            record = QaRecord(
                user_id=current_user.id,
                question=question,
                answer=full_answer,
                source_docs=json.dumps(sources, ensure_ascii=False)
            )
            db.add(record)
            db.commit()

            # 7. 结束标记
            yield f"event: done\ndata: [DONE]\n\n"

        except Exception as e:
            print(f"=== 问答流式错误 ===")
            traceback.print_exc()
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")