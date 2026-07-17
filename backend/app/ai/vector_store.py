"""
FAISS 向量存储 - 向量索引管理
支持增、删、查、持久化
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS 向量存储服务"""
    
    def __init__(self):
        self.index = None
        self.dim = settings.EMBEDDING_DIM
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = settings.METADATA_PATH
        self.metadata = []  # 每个向量对应的元数据
        self._ensure_data_dir()
        self._load_index()
        self._load_metadata()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
    
    def _load_index(self):
        """加载 FAISS 索引"""
        import faiss
        
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info(f"加载 FAISS 索引: {self.index_path}, 向量数: {self.index.ntotal}")
                return
            except Exception as e:
                logger.warning(f"加载 FAISS 索引失败: {e}，将创建新索引")
        
        # 创建新索引（内积相似度）
        self.index = faiss.IndexFlatIP(self.dim)
        logger.info(f"创建新的 FAISS 索引，维度: {self.dim}")
    
    def _load_metadata(self):
        """加载元数据"""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"加载元数据: {len(self.metadata)} 条")
            except Exception as e:
                logger.warning(f"加载元数据失败: {e}")
                self.metadata = []
        else:
            self.metadata = []
    
    def _persist(self):
        """持久化索引和元数据"""
        import faiss
        
        # 保存 FAISS 索引
        if self.index is not None and self.index.ntotal > 0:
            faiss.write_index(self.index, self.index_path)
            logger.debug(f"FAISS 索引已保存: {self.index_path}")
        
        # 保存元数据
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        logger.debug(f"元数据已保存: {self.metadata_path}")
    
    def add(self, vectors: np.ndarray, metas: List[Dict[str, Any]]):
        """
        添加向量和元数据
        
        Args:
            vectors: 向量数组，shape=(n, dim)
            metas: 元数据列表，每个元素包含 content, doc_id, chunk_idx
        """
        if len(vectors) == 0:
            return
        
        import faiss
        
        # 确保向量维度正确
        if vectors.shape[1] != self.dim:
            raise ValueError(f"向量维度不匹配: 期望 {self.dim}, 实际 {vectors.shape[1]}")
        
        # 归一化（如果 embedding_service 没有做）
        # faiss.normalize_L2(vectors)
        
        # 添加到索引
        self.index.add(vectors)
        
        # 记录起始索引
        start_idx = len(self.metadata)
        
        # 添加元数据
        for i, meta in enumerate(metas):
            meta['_idx'] = start_idx + i  # 保存向量在索引中的位置
            self.metadata.append(meta)
        
        # 持久化
        self._persist()
        logger.info(f"添加 {len(vectors)} 个向量，当前总数: {self.index.ntotal}")
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        检索相似向量
        
        Args:
            query_vector: 查询向量，shape=(dim,)
            top_k: 返回结果数量
        
        Returns:
            List[Dict]: 检索结果，包含 content, doc_id, chunk_idx, score
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # 确保向量是 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # 检索
        scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            # 相似度阈值过滤
            if score < settings.SIMILARITY_THRESHOLD:
                continue
            
            meta = self.metadata[idx].copy()
            meta['score'] = float(score)
            # 移除内部字段
            meta.pop('_idx', None)
            results.append(meta)
        
        return results
    
    def delete_by_doc_id(self, doc_id: int):
        """
        按文档 ID 删除向量
        
        NOTE: FAISS 不支持直接删除，需要重建索引
        """
        import faiss
        
        # 找出要保留的向量
        keep_indices = []
        keep_metas = []
        
        for i, meta in enumerate(self.metadata):
            if meta.get('doc_id') != doc_id:
                keep_indices.append(i)
                keep_metas.append(meta)
        
        if len(keep_indices) == len(self.metadata):
            logger.info(f"文档 {doc_id} 不存在，无需删除")
            return
        
        # 重建索引
        if keep_indices:
            # 获取所有向量
            all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
            keep_vectors = all_vectors[keep_indices]
            
            # 创建新索引
            new_index = faiss.IndexFlatIP(self.dim)
            new_index.add(keep_vectors)
            self.index = new_index
            self.metadata = keep_metas
        else:
            # 全部删除
            self.index = faiss.IndexFlatIP(self.dim)
            self.metadata = []
        
        # 持久化
        self._persist()
        logger.info(f"删除文档 {doc_id} 的向量，剩余: {self.index.ntotal}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dim,
            "metadata_count": len(self.metadata)
        }
    
    def get_doc_stats(self, doc_id: int) -> Dict[str, Any]:
        """获取某个文档的向量统计"""
        chunks = [m for m in self.metadata if m.get('doc_id') == doc_id]
        return {
            "doc_id": doc_id,
            "chunk_count": len(chunks),
            "chunks": chunks
        }


# 全局单例
vector_store = VectorStore()