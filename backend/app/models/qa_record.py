from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship  # 暂时注释

from app.core.database import Base


class QaRecord(Base):
    __tablename__ = "qa_record"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=False, comment="AI回答")
    source_docs = Column(Text, nullable=True, comment="引用来源（JSON字符串）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 暂时注释掉，等 User 模型的 qa_records 启用后再恢复
    # user = relationship("User", back_populates="qa_records")