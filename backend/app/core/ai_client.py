# app/core/ai_client.py
from typing import List, Dict, Any
from app.core.rag_service import process_document, search_documents


class AiClient:
    async def process_document(self, doc_id: int, file_path: str) -> Dict[str, Any]:
        """文档处理：切分 → 向量化 → FAISS 入库"""
        # rag_service.process_document 包含完整流水线
        return process_document(doc_id, file_path)

    async def search(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """向量检索"""
        return search_documents(question, top_k)


ai_client = AiClient()