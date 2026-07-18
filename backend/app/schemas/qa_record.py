from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class QaRecordResponse(BaseModel):
    """问答记录响应"""
    id: int
    question: str
    answer: str
    source_docs: Optional[str] = None
    created_at: datetime


class QaRecordListData(BaseModel):
    """问答记录列表数据"""
    total: int
    page: int
    size: int
    list: List[QaRecordResponse]