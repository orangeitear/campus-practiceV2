"""
FAISS 向量库模块
支持向量的增删查改，以及索引的持久化存储
使用 IndexFlatIP（内积）进行相似度检索

元数据结构（每个向量对应一个）:
    - content: 文本块内容
    - doc_id: 文档 ID
    - chunk_idx: 块序号
"""
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import faiss

from app.core.config import settings
from app.core.exceptions import BizException
from app.ai.embedding import embedding_client


# ============ 配置常量 ============

DEFAULT_INDEX_DIR = "./data/faiss_index"
DEFAULT_INDEX_NAME = "kb_index"


class FAISSVectorStore:
    """
    FAISS 向量存储封装
    
    元数据结构（每个向量对应一个）:
        - content: 文本块内容
        - doc_id: 所属文档 ID
        - chunk_idx: 块序号
    """
    
    def __init__(
        self,
        index_dir: str = DEFAULT_INDEX_DIR,
        index_name: str = DEFAULT_INDEX_NAME
    ):
        """
        初始化向量存储
        
        Args:
            index_dir: 索引存储目录
            index_name: 索引文件名称（不含扩展名）
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_name = index_name
        self.index_path = self.index_dir / f"{index_name}.faiss"
        self.metadata_path = self.index_dir / f"{index_name}_metadata.pkl"
        
        self._index: Optional[faiss.Index] = None
        self._metadata: List[Dict[str, Any]] = []
        self._dimension: Optional[int] = None
        
        # 尝试加载已有索引
        self._load()
    
    # ============ 属性 ============
    
    @property
    def index(self) -> faiss.Index:
        """获取 FAISS 索引（不存在则创建）"""
        if self._index is None:
            self._create_index()
        return self._index
    
    @property
    def metadata(self) -> List[Dict[str, Any]]:
        """获取元数据列表"""
        return self._metadata
    
    @property
    def dimension(self) -> int:
        """获取向量维度"""
        if self._dimension is None:
            self._dimension = embedding_client.embedding_dim
        return self._dimension
    
    @property
    def total_count(self) -> int:
        """获取向量总数"""
        if self._index is None:
            return 0
        return self._index.ntotal
    
    # ============ 索引管理 ============
    
    def _create_index(self) -> None:
        """创建新的 FAISS 索引（IndexFlatIP 内积）"""
        print(f"=== 创建 FAISS 索引 ===")
        print(f"向量维度: {self.dimension}")
        self._index = faiss.IndexFlatIP(self.dimension)
        self._metadata = []
        self._save()
    
    def _load(self) -> bool:
        """从磁盘加载索引和元数据"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                print(f"=== 加载 FAISS 索引 ===")
                print(f"索引路径: {self.index_path}")
                self._index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, "rb") as f:
                    self._metadata = pickle.load(f)
                self._dimension = self._index.d
                print(f"加载成功，向量数量: {self.total_count}")
                return True
            except Exception as e:
                print(f"加载索引失败: {e}")
                return False
        return False
    
    def _save(self) -> None:
        """保存索引和元数据到磁盘"""
        if self._index is not None:
            faiss.write_index(self._index, str(self.index_path))
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self._metadata, f)
        print(f"=== 索引已保存 ===")
        print(f"向量数量: {self.total_count}")
    
    def rebuild(self) -> None:
        """重建索引（清空所有数据）"""
        print(f"=== 重建 FAISS 索引 ===")
        self._create_index()
        self._save()
    
    # ============ 向量操作 ============
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """归一化向量（用于内积相似度）"""
        faiss.normalize_L2(vectors)
        return vectors
    
    def add_vectors(
        self,
        vectors: np.ndarray,
        metadatas: List[Dict[str, Any]]
    ) -> int:
        """
        添加向量到索引
        
        Args:
            vectors: 向量矩阵，shape (n, dim)
            metadatas: 对应的元数据列表，长度必须与 vectors 一致
            
        Returns:
            添加的向量数量
        """
        if len(vectors) == 0:
            return 0
        
        if len(vectors) != len(metadatas):
            raise BizException(code=400, message="vectors 和 metadatas 长度不一致")
        
        print(f"=== add_vectors 开始 ===")
        print(f"向量数量: {len(vectors)}")
        
        # 确保向量是 float32
        vectors = vectors.astype(np.float32)
        
        # 归一化向量
        self._normalize_vectors(vectors)
        
        # 添加到索引
        start_idx = self.total_count
        self.index.add(vectors)
        
        # 添加元数据（每个向量对应一条）
        for i, meta in enumerate(metadatas):
            meta["vector_idx"] = start_idx + i
        self._metadata.extend(metadatas)
        
        # 持久化
        self._save()
        
        return len(vectors)
    
    def add_document_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        添加文档的所有切分块到向量库
        
        Args:
            chunks: 切分块列表，每个包含 content, doc_id, chunk_idx
            
        Returns:
            添加的向量数量
        """
        if not chunks:
            return 0
        
        print(f"=== add_document_chunks 开始 ===")
        print(f"文档块数量: {len(chunks)}")
        
        # 提取文本内容
        contents = [chunk["content"] for chunk in chunks]
        
        # 批量向量化
        vectors = embedding_client.embed(contents)
        
        if len(vectors) == 0:
            raise BizException(code=500, message="向量化失败")
        
        # 构建元数据
        metadatas = [
            {
                "content": chunk["content"],
                "doc_id": chunk["doc_id"],
                "chunk_idx": chunk["chunk_idx"],
            }
            for chunk in chunks
        ]
        
        return self.add_vectors(vectors, metadatas)
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索最相似的向量
        
        Args:
            query_vector: 查询向量，shape (dim,)
            top_k: 返回的最大结果数
            
        Returns:
            检索结果列表，每个元素包含:
                - content: 文本块内容
                - doc_id: 文档 ID
                - chunk_idx: 块序号
                - score: 相似度分数 (0~1, 越高越相似)
        """
        if self.total_count == 0:
            return []
        
        print(f"=== search 开始 ===")
        print(f"Top K: {top_k}, 总向量数: {self.total_count}")
        
        # 确保查询向量是 float32
        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        
        # 归一化查询向量
        self._normalize_vectors(query_vector)
        
        # 检索
        k = min(top_k, self.total_count)
        scores, indices = self.index.search(query_vector, k)
        
        # 解析结果
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._metadata):
                continue
            meta = self._metadata[idx]
            results.append({
                "content": meta["content"],
                "doc_id": meta["doc_id"],
                "chunk_idx": meta["chunk_idx"],
                "score": float(score),
            })
        
        print(f"检索完成，返回 {len(results)} 条结果")
        return results
    
    # ============ 文档管理 ============
    
    def delete_by_doc_id(self, doc_id: int) -> int:
        """
        删除指定文档的所有向量
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            删除的向量数量
        """
        print(f"=== delete_by_doc_id 开始 ===")
        print(f"文档 ID: {doc_id}")
        
        # 找出该文档的所有元数据
        to_delete_metas = [
            meta for meta in self._metadata
            if meta["doc_id"] == doc_id
        ]
        
        if not to_delete_metas:
            print(f"文档 {doc_id} 没有向量数据")
            return 0
        
        to_delete_count = len(to_delete_metas)
        print(f"需要删除的向量数: {to_delete_count}")
        
        # 从元数据中移除
        self._metadata = [
            meta for meta in self._metadata
            if meta["doc_id"] != doc_id
        ]
        
        # FAISS 不支持直接删除，需要重建索引
        if self._metadata:
            self._rebuild_from_metadatas(self._metadata)
        else:
            self._create_index()
        
        self._save()
        return to_delete_count
    
    def _rebuild_from_metadatas(self, metadatas: List[Dict[str, Any]]) -> None:
        """
        从元数据重建索引
        
        Args:
            metadatas: 元数据列表
        """
        if not metadatas:
            self._create_index()
            return
        
        print(f"=== 重建索引 ===")
        print(f"元数据数量: {len(metadatas)}")
        
        # 提取文本内容
        contents = [meta["content"] for meta in metadatas]
        
        # 重新向量化
        vectors = embedding_client.embed(contents)
        
        if len(vectors) == 0:
            self._create_index()
            return
        
        # 归一化向量
        self._normalize_vectors(vectors)
        
        # 重置索引
        self._index = faiss.IndexFlatIP(self.dimension)
        self._index.add(vectors)
        
        # 更新元数据中的 vector_idx
        for idx, meta in enumerate(metadatas):
            meta["vector_idx"] = idx
    
    def get_doc_stats(self, doc_id: int) -> Dict[str, Any]:
        """
        获取文档的向量统计信息
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            统计信息: {count: 向量数量, chunk_indices: 块序号列表}
        """
        doc_metas = [
            meta for meta in self._metadata
            if meta["doc_id"] == doc_id
        ]
        return {
            "count": len(doc_metas),
            "chunk_indices": sorted([m["chunk_idx"] for m in doc_metas]),
        }


# ============ 全局实例 ============

vector_store = FAISSVectorStore()