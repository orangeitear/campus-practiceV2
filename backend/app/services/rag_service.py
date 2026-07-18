"""
RAG 服务编排模块
整合检索、Prompt 构建、LLM 生成，实现完整的 RAG 问答流程

对外暴露的接口（供 document_service.py 调用）:
    - process_document(doc_id, file_path) → {"chunk_count": int}
    - search_documents(question, top_k) → [{content, doc_id, chunk_idx, score}]
"""
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator

from app.core.exceptions import BizException
from app.ai.processor import document_processor
from app.ai.vector_store import vector_store
from app.ai.embedding import embedding_client


class RAGService:
    """
    RAG 服务编排类
    负责串联检索、Prompt 构建和 LLM 生成
    """
    
    def __init__(
        self,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        temperature: float = 0.3,
    ):
        """
        初始化 RAG 服务
        
        Args:
            top_k: 检索时返回的最大文档块数
            similarity_threshold: 相似度阈值，低于此值的结果将被过滤
            temperature: LLM 生成温度（0-1，越低越确定）
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.temperature = temperature
        self._llm_client = None
        self._prompt_builder = None
    
    @property
    def llm_client(self):
        """延迟加载 llm_client（等待王嘉欣完成）"""
        if self._llm_client is None:
            from app.core.llm_client import llm_client
            self._llm_client = llm_client
        return self._llm_client
    
    @property
    def prompt_builder(self):
        """延迟加载 prompt_builder（等待王嘉欣完成）"""
        if self._prompt_builder is None:
            from app.core.prompt import build_chat_messages
            self._prompt_builder = build_chat_messages
        return self._prompt_builder
    
    # ============ 内部检索方法 ============
    
    def _retrieve(
        self,
        question: str,
        top_k: Optional[int] = None,
        doc_id_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        检索阶段：向量化问题并检索相关文档块
        
        Args:
            question: 用户问题
            top_k: 检索数量（覆盖默认值）
            doc_id_filter: 限定检索的文档 ID
            
        Returns:
            检索结果列表，包含 content, doc_id, chunk_idx, score
        """
        print(f"=== _retrieve 开始 ===")
        print(f"问题: {question[:50]}...")
        
        if top_k is None:
            top_k = self.top_k
        
        # 1. 将问题向量化
        question_vector = embedding_client.embed_single(question)
        
        if len(question_vector) == 0:
            return []
        
        # 2. 在向量库中检索
        results = vector_store.search(
            query_vector=question_vector,
            top_k=top_k
        )
        
        # 3. 如果指定了文档过滤，进一步过滤
        if doc_id_filter is not None:
            results = [
                r for r in results
                if r["doc_id"] == doc_id_filter
            ]
        
        # 4. 过滤低相关结果（低于阈值丢弃）
        filtered = [
            r for r in results
            if r["score"] >= self.similarity_threshold
        ]
        
        print(f"检索完成，过滤前: {len(results)} 条，过滤后: {len(filtered)} 条")
        return filtered
    
    def _extract_sources(
        self,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        提取来源信息（用于返回给前端展示）
        
        Args:
            retrieved_chunks: 检索结果列表
            
        Returns:
            来源信息列表，每个包含 doc_id 和 chunk_idx
        """
        sources = []
        seen = set()
        for chunk in retrieved_chunks:
            doc_id = chunk.get("doc_id")
            if doc_id not in seen:
                seen.add(doc_id)
                sources.append({
                    "doc_id": doc_id,
                    "chunk_idx": chunk.get("chunk_idx"),
                    "score": chunk.get("score"),
                })
        return sources
    
    # ============ 对外接口（供 document_service.py 调用） ============
    
    def process_document(self, doc_id: int, file_path: str) -> Dict[str, int]:
        """
        处理文档：读取 → 切分 → 向量化 → 入库
        
        对应王嘉欣调用的 ai_client.process_document()
        
        Args:
            doc_id: 文档 ID
            file_path: 文件路径
            
        Returns:
            {"chunk_count": int} 切分后的块数
        """
        print(f"=== RAGService.process_document 开始 ===")
        print(f"文档 ID: {doc_id}, 文件路径: {file_path}")
        
        try:
            # 1. 读取并切分文档
            chunks = document_processor.process_document(file_path, doc_id)
            
            if not chunks:
                return {"chunk_count": 0}
            
            # 2. 向量化并存入 FAISS
            added_count = vector_store.add_document_chunks(chunks)
            
            print(f"文档处理完成，块数: {added_count}")
            return {"chunk_count": added_count}
            
        except BizException:
            raise
        except Exception as e:
            raise BizException(code=500, message=f"文档处理失败: {str(e)}")
    
    def search_documents(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        向量检索：根据问题检索相关文档块
        
        对应王嘉欣调用的 ai_client.search_documents()
        
        Args:
            question: 用户问题
            top_k: 返回的最大结果数
            
        Returns:
            检索结果列表，每个包含 content, doc_id, chunk_idx, score
        """
        print(f"=== RAGService.search_documents 开始 ===")
        print(f"问题: {question[:50]}...")
        
        # 1. 将问题向量化
        question_vector = embedding_client.embed_single(question)
        
        if len(question_vector) == 0:
            return []
        
        # 2. 在向量库中检索
        results = vector_store.search(
            query_vector=question_vector,
            top_k=top_k
        )
        
        # 3. 转换为标准输出格式
        return [
            {
                "content": r["content"],
                "doc_id": r["doc_id"],
                "chunk_idx": r["chunk_idx"],
                "score": r["score"],
            }
            for r in results
        ]
    
    # ============ 完整问答流程（供 chat.py 路由调用） ============
    
    async def answer_question(
        self,
        question: str,
        top_k: Optional[int] = None,
        doc_id_filter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        同步问答：检索 → 生成 → 返回完整答案
        
        Args:
            question: 用户问题
            top_k: 检索数量
            doc_id_filter: 限定检索的文档 ID
            
        Returns:
            包含 answer 和 sources 的字典
        """
        print(f"=== RAGService.answer_question 开始 ===")
        print(f"问题: {question[:50]}...")
        
        # 1. 检索
        retrieved = self._retrieve(question, top_k, doc_id_filter)
        
        # 2. 如果无结果，返回友好提示
        if not retrieved:
            return {
                "answer": "抱歉，知识库中暂未找到与您问题相关的内容。\n\n建议您：\n1. 尝试用更具体的关键词重新提问\n2. 上传相关文档到知识库后再进行询问",
                "sources": [],
                "retrieved_count": 0,
            }
        
        # 3. 构建 Prompt（使用延迟加载的 prompt_builder）
        chunks_with_title = []
        for chunk in retrieved:
            chunks_with_title.append({
                "content": chunk["content"],
                "title": f"文档_{chunk['doc_id']}",
                "doc_id": chunk["doc_id"],
                "chunk_idx": chunk["chunk_idx"],
                "score": chunk["score"],
            })
        
        messages = self.prompt_builder(question, chunks_with_title)
        
        # 4. 调用 LLM 生成答案（使用延迟加载的 llm_client）
        answer = await self.llm_client.chat(
            messages=messages,
            temperature=self.temperature
        )
        
        # 5. 提取来源
        sources = self._extract_sources(retrieved)
        
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(retrieved),
        }
    
    async def answer_question_stream(
        self,
        question: str,
        top_k: Optional[int] = None,
        doc_id_filter: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式问答：检索 → 流式生成 → 逐 token 返回
        
        Args:
            question: 用户问题
            top_k: 检索数量
            doc_id_filter: 限定检索的文档 ID
            
        Yields:
            字典: {"type": "token", "data": str} 
                或 {"type": "sources", "data": list}
                或 {"type": "done", "data": dict}
        """
        print(f"=== RAGService.answer_question_stream 开始 ===")
        print(f"问题: {question[:50]}...")
        
        # 1. 检索
        retrieved = self._retrieve(question, top_k, doc_id_filter)
        
        # 2. 如果无结果，直接返回空结果提示
        if not retrieved:
            empty_answer = "抱歉，知识库中暂未找到与您问题相关的内容。"
            for char in empty_answer:
                yield {"type": "token", "data": char}
            yield {"type": "sources", "data": []}
            yield {
                "type": "done",
                "data": {
                    "full_answer": empty_answer,
                    "sources": [],
                    "retrieved_count": 0,
                }
            }
            return
        
        # 3. 构建 Prompt
        chunks_with_title = []
        for chunk in retrieved:
            chunks_with_title.append({
                "content": chunk["content"],
                "title": f"文档_{chunk['doc_id']}",
                "doc_id": chunk["doc_id"],
                "chunk_idx": chunk["chunk_idx"],
                "score": chunk["score"],
            })
        
        messages = self.prompt_builder(question, chunks_with_title)
        
        # 4. 流式生成（使用延迟加载的 llm_client）
        answer_parts = []
        async for token in self.llm_client.chat_stream(
            messages=messages,
            temperature=self.temperature
        ):
            answer_parts.append(token)
            yield {"type": "token", "data": token}
        
        # 5. 发送来源信息
        sources = self._extract_sources(retrieved)
        yield {"type": "sources", "data": sources}
        
        # 6. 发送完成标记
        yield {
            "type": "done",
            "data": {
                "full_answer": "".join(answer_parts),
                "sources": sources,
                "retrieved_count": len(retrieved),
            }
        }


# ============ 全局实例（供王嘉欣调用） ============

rag_service = RAGService()


# ============ 对外接口函数（供 document_service.py 调用） ============

def process_document(doc_id: int, file_path: str) -> Dict[str, int]:
    """
    处理文档：切分 → 向量化 → 入库
    
    供 document_service.py 调用
    
    Args:
        doc_id: 文档 ID
        file_path: 文件路径
        
    Returns:
        {"chunk_count": int}
    """
    return rag_service.process_document(doc_id, file_path)


def search_documents(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    向量检索
    
    供 document_service.py 调用
    
    Args:
        question: 用户问题
        top_k: 返回的最大结果数
        
    Returns:
        [{content, doc_id, chunk_idx, score}]
    """
    return rag_service.search_documents(question, top_k)


# ============ 供路由调用的函数 ============

async def answer_question(
    question: str,
    top_k: Optional[int] = None,
    doc_id_filter: Optional[int] = None
) -> Dict[str, Any]:
    """同步问答"""
    return await rag_service.answer_question(question, top_k, doc_id_filter)


async def answer_question_stream(
    question: str,
    top_k: Optional[int] = None,
    doc_id_filter: Optional[int] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """流式问答"""
    async for item in rag_service.answer_question_stream(question, top_k, doc_id_filter):
        yield item