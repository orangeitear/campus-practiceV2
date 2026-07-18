from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """上传文档响应"""
    id: int
    status: str
    message: str


class DocumentListResponse(BaseModel):
    """文档列表项响应"""
    id: int
    title: str
    file_type: str
    file_size: Optional[int] = None
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentListData(BaseModel):
    """文档列表数据"""
    total: int
    page: int
    size: int
    list: list[DocumentListResponse]


class DocumentReprocessResponse(BaseModel):
    """重新处理响应"""
    id: int
    status: str
    message: str