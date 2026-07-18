import os
import shutil
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.kb_document import KbDocument
from app.schemas.document import DocumentListResponse
from app.core.ai_client import ai_client
from app.core.exceptions import BizException


# 上传文件存储目录
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def save_file(file: UploadFile) -> str:
    """保存文件到磁盘"""
    print(f"=== save_file 开始 ===")
    print(f"文件名: {file.filename}, 大小: {file.size}")
    
    ext = os.path.splitext(file.filename)[1].lower()
    print(f"扩展名: {ext}")
    
    if ext not in ALLOWED_EXTENSIONS:
        raise BizException(code=400, message=f"不支持的文件类型: {ext}")
    if file.size and file.size > MAX_FILE_SIZE:
        raise BizException(code=400, message="文件大小不能超过 50MB")

    # 生成唯一文件名
    file_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    print(f"保存路径: {file_path}")
    
    # 确保目录存在
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print("目录已创建/确认")
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    print("文件已写入")
    
    return str(file_path)


def create_document(db: Session, file: UploadFile, file_path: str) -> KbDocument:
    """保存文档记录"""
    ext = os.path.splitext(file.filename)[1].lower()
    doc = KbDocument(
        title=file.filename,
        file_name=file.filename,
        file_path=file_path,
        file_type=ext[1:],
        file_size=file.size,
        status="待处理",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


async def process_document_async(doc_id: int, file_path: str, db: Session):
    """异步处理文档：调用 AI 服务"""
    try:
        # 更新状态为处理中
        doc = db.query(KbDocument).filter(KbDocument.id == doc_id).first()
        if doc:
            doc.status = "处理中"
            db.commit()

        # 调用 AI 服务
        result = await ai_client.process_document(doc_id, file_path)

        # 更新状态为已完成
        if doc:
            doc.status = "已完成"
            doc.chunk_count = result.get("chunk_count", 0)
            db.commit()
    except Exception as e:
        # 更新状态为处理失败
        doc = db.query(KbDocument).filter(KbDocument.id == doc_id).first()
        if doc:
            doc.status = "处理失败"
            doc.error_message = str(e)
            db.commit()
        raise e


def get_document_list(
    db: Session,
    keyword: str = None,
    status: str = None,
    page: int = 1,
    size: int = 10
):
    """获取文档列表（分页 + 搜索 + 状态筛选）"""
    query = db.query(KbDocument)
    if keyword:
        query = query.filter(KbDocument.title.contains(keyword))
    if status:
        query = query.filter(KbDocument.status == status)

    total = query.count()
    items = query.order_by(KbDocument.created_at.desc()).offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "list": [DocumentListResponse.model_validate(item.__dict__) for item in items]
    }


def delete_document_with_vectors(db: Session, doc_id: int) -> bool:
    """
    删除文档（级联清理：数据库记录 + 磁盘文件 + FAISS 向量）
    """
    doc = db.query(KbDocument).filter(KbDocument.id == doc_id).first()
    if not doc:
        raise BizException(code=404, message="文档不存在")

    # 1. 删除磁盘文件
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            # 文件删除失败不影响主流程，记录日志即可
            pass

    # 2. TODO: 删除 FAISS 向量（按 doc_id）
    # 调用陈梦的 FAISS 删除接口，或直接操作向量库

    # 3. 删除数据库记录
    db.delete(doc)
    db.commit()

    return True


def delete_document(db: Session, doc_id: int):
    """删除文档（记录 + 向量 + 文件）"""
    doc = db.query(KbDocument).filter(KbDocument.id == doc_id).first()
    if not doc:
        raise BizException(code=404, message="文档不存在")

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # TODO: 调用 AI 服务删除向量

    db.delete(doc)
    db.commit()