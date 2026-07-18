# app/core/ai_client.py
from typing import List, Dict, Any

# TODO: 陈梦完成 AI 服务后，替换为真实调用
# from app.core.rag_service import process_document, search_documents


def process_document(doc_id: int, file_path: str) -> Dict[str, Any]:
    """模拟文档处理"""
    print(f"[模拟] 处理文档: doc_id={doc_id}, file_path={file_path}")
    return {"chunk_count": 0}


def search_documents(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """模拟向量检索"""
    print(f"[模拟] 检索: question={question}, top_k={top_k}")
    return []


class AiClient:
    async def process_document(self, doc_id: int, file_path: str) -> Dict[str, Any]:
        return process_document(doc_id, file_path)

    async def search(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return search_documents(question, top_k)


ai_client = AiClient()