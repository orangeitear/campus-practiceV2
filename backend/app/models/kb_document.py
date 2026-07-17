from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.sql import func

from app.core.database import Base


class KbDocument(Base):
    __tablename__ = "kb_document"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="文档标题")
    file_name = Column(String(255), nullable=False, comment="文件名")  # ✅ 新增
    file_path = Column(String(500), nullable=False, comment="存储路径")
    file_type = Column(String(20), nullable=False, comment="pdf/doc/docx/txt")
    file_size = Column(BigInteger, nullable=True, comment="文件大小（字节）")
    chunk_count = Column(Integer, default=0, comment="切分块数")
    status = Column(String(20), default="待处理", comment="待处理/处理中/已完成/处理失败")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")