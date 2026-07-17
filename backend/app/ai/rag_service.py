"""
RAG 服务 - 完整流程编排
文档处理 → 向量入库 → 检索 → 生成回答
"""

import logging
from typing import Dict, Any, List, Optional
from app.ai.embedding_service import embedding_service
from app.ai.vector_store import vector_store
from app.ai.document_processor import document_processor
from app.ai.llm_client import llm_client
from app.ai.prompt_builder import prompt_builder
from app.core.config import settings

logger = logging.getLogger(__name__)


class RagService:
    """RAG 服务 - 流程编排"""
    
    def __init__(self):
        self.top_k = settings.DEFAULT_TOP_K
        self.threshold = settings.SIMILARITY_THRESHOLD
    
    def process_document(self, doc_id: int, file_path: str) -> Dict[str, Any]:
        """
        处理文档：提取 → 切分 → 向量化 → 入库
        
        Args:
            doc_id: 文档 ID
            file_path: 文件路径
        
        Returns:
            Dict: {chunk_count: int, status: str}
        """
        try:
            logger.info(f"开始处理文档: doc_id={doc_id}, path={file_path}")
            
            # 1. 提取 + 切分
            result = document_processor.process(file_path)
            chunks = result['chunks']
            
            if not chunks:
                logger.warning(f"文档 {doc_id} 无有效文本内容")
                return {
                    "chunk_count": 0,
                    "status": "failed",
                    "error": "无法提取文本内容"
                }
            
            # 2. 向量化（批量）
            vectors = embedding_service.embed_batch(chunks, batch_size=32)
            
            # 3. 构建元数据
            metas = []
            for i, chunk in enumerate(chunks):
                metas.append({
                    "content": chunk,
                    "doc_id": doc_id,
                    "chunk_idx": i
                })
            
            # 4. 入库（先删除旧向量）
            vector_store.delete_by_doc_id(doc_id)
            vector_store.add(vectors, metas)
            
            logger.info(f"文档 {doc_id} 处理完成: {len(chunks)} 个块")
            
            return {
                "chunk_count": len(chunks),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"文档 {doc_id} 处理失败: {e}")
            return {
                "chunk_count": 0,
                "status": "failed",
                "error": str(e)
            }
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        RAG 问答
        
        Args:
            question: 用户问题
        
        Returns:
            Dict: {answer: str, sources: List[Dict]}
        """
        try:
            logger.info(f"收到问答请求: {question[:50]}...")
            
            # 1. 问题向量化
            query_vector = embedding_service.embed(question)
            
            # 2. 向量检索
            chunks = vector_store.search(query_vector, top_k=self.top_k)
            logger.info(f"检索到 {len(chunks)} 个相关文本块")
            
            # 3. 构建 Prompt
            if chunks:
                prompt = prompt_builder.build(question, chunks)
            else:
                # 无检索结果，使用无上下文 Prompt
                prompt = prompt_builder.build_without_context(question)
                logger.info("无检索结果，使用无上下文模式")
            
            # 4. 调用 LLM
            answer = llm_client.chat(prompt)
            
            # 5. 提取来源信息
            sources = []
            for chunk in chunks:
                sources.append({
                    "doc_id": chunk.get('doc_id'),
                    "content": chunk.get('content'),
                    "score": chunk.get('score')
                })
            
            logger.info(f"问答完成，回答长度: {len(answer)} 字符")
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"问答失败: {e}")
            return {
                "answer": f"抱歉，处理您的问题时出现了错误：{str(e)}",
                "sources": []
            }
    
    def ask_stream(self, question: str):
        """
        流式 RAG 问答
        
        Args:
            question: 用户问题
        
        Yields:
            str: 逐字输出的回答
        """
        try:
            logger.info(f"收到流式问答请求: {question[:50]}...")
            
            # 1. 问题向量化
            query_vector = embedding_service.embed(question)
            
            # 2. 向量检索
            chunks = vector_store.search(query_vector, top_k=self.top_k)
            logger.info(f"检索到 {len(chunks)} 个相关文本块")
            
            # 3. 构建 Prompt
            if chunks:
                prompt = prompt_builder.build(question, chunks)
            else:
                prompt = prompt_builder.build_without_context(question)
            
            # 4. 流式调用 LLM
            for token in llm_client.chat_stream(prompt):
                yield token
                
        except Exception as e:
            logger.error(f"流式问答失败: {e}")
            yield f"抱歉，处理您的问题时出现了错误：{str(e)}"
    
    def delete_document(self, doc_id: int):
        """删除文档的向量数据"""
        vector_store.delete_by_doc_id(doc_id)
        logger.info(f"已删除文档 {doc_id} 的向量数据")
    
    def get_stats(self, doc_id: Optional[int] = None) -> Dict[str, Any]:
        """获取统计信息"""
        if doc_id:
            return vector_store.get_doc_stats(doc_id)
        return vector_store.get_stats()


# 全局单例
rag_service = RagService()