from typing import Optional, List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求"""
    question: str


class SourceDoc(BaseModel):
    """引用来源"""
    content: str
    doc_id: int
    title: str
    score: float


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    sources: Optional[List[SourceDoc]] = None


class ChatHistoryResponse(BaseModel):
    """问答历史响应"""
    id: int
    question: str
    answer: str
    source_docs: Optional[str] = None
    created_at: str