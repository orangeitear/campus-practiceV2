from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DocumentUploadResponse(BaseModel):
    """上传文档响应"""
    id: int
    status: str
    message: str


class DocumentListResponse(BaseModel):
    """文档列表项响应（字段名对齐前端）"""
    id: int
    title: str
    filename: str = Field(alias="file_name")
    file_type: str
    size: Optional[int] = Field(default=None, alias="file_size")
    chunk_count: int
    status: str
    error: Optional[str] = Field(default=None, alias="error_message")
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


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