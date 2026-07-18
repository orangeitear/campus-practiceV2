import traceback
from fastapi import APIRouter, Depends, Query, UploadFile, File, BackgroundTasks, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.kb_document import KbDocument
from app.schemas.common import success, error
from app.schemas.document import DocumentListData, DocumentListResponse
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["知识库管理"])


@router.post("")
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传文档"""
    try:
        print(f"=== 1. 收到文件: {file.filename}, 标题: {title}, 大小: {file.size} ===")

        # 保存文件
        file_path = document_service.save_file(file)
        print(f"=== 2. 文件保存路径: {file_path} ===")

        # 创建文档记录
        doc = document_service.create_document(db, title, file, file_path)
        print(f"=== 3. 文档记录创建: id={doc.id}, status={doc.status} ===")

        # 异步触发 AI 处理
        background_tasks.add_task(
            document_service.process_document_async,
            doc.id,
            file_path,
        )
        print(f"=== 4. 异步任务已添加 ===")

        return success(data={"id": doc.id, "status": doc.status}, message="上传成功，正在处理")
    except Exception as e:
        print(f"=== 上传异常 ===")
        print(traceback.format_exc())
        raise


@router.get("")
async def get_document_list(
    keyword: str = Query(None, description="搜索关键词"),
    status: str = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取文档列表"""
    result = document_service.get_document_list(db, keyword, status, page, size)
    
    # 将 SQLAlchemy 模型对象转换为 Pydantic Schema 对象
    result["list"] = [DocumentListResponse.model_validate(item) for item in result["list"]]
    
    return success(data=DocumentListData(**result))


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """删除文档（仅管理员）"""
    document_service.delete_document_with_vectors(db, doc_id)
    return success(message="删除成功")


@router.post("/{doc_id}/reprocess")
async def reprocess_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """重新处理文档（仅管理员）"""
    doc = db.query(KbDocument).filter(KbDocument.id == doc_id).first()
    if not doc:
        return error(message="文档不存在", code=404)

    doc.status = "PENDING"
    doc.error_message = None
    db.commit()

    background_tasks.add_task(
        document_service.process_document_async,
        doc.id,
        doc.file_path,
    )
    return success(message="已启动重新处理")