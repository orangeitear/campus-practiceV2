"""
AI 模块 - 提供 RAG 相关能力
- 文档切分与向量化
- FAISS 向量存储与检索
- LLM 调用与 Prompt 构建
- RAG 流程编排
"""

from app.ai.rag_service import rag_service
from app.ai.embedding_service import embedding_service
from app.ai.vector_store import vector_store
from app.ai.llm_client import llm_client
from app.ai.prompt_builder import prompt_builder

__all__ = [
    "rag_service",
    "embedding_service",
    "vector_store",
    "llm_client",
    "prompt_builder",
]