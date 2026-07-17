"""
Embedding 服务 - 文本向量化
支持 BGE / M3E / OpenAI 等多种模型
"""

import numpy as np
from typing import List, Union
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """文本向量化服务"""
    
    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL
        self.dim = settings.EMBEDDING_DIM
        self._load_model()
    
    def _load_model(self):
        """加载 Embedding 模型"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"加载 Embedding 模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding 模型加载完成")
        except ImportError:
            logger.error("请安装 sentence-transformers: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"加载 Embedding 模型失败: {e}")
            raise
    
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        将文本转换为向量
        
        Args:
            texts: 单个文本或文本列表
        
        Returns:
            numpy.ndarray: 向量数组，shape=(n, dim)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        try:
            # 批量编码，自动归一化
            vectors = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return np.array(vectors, dtype=np.float32)
        except Exception as e:
            logger.error(f"向量化失败: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        分批向量化（处理大量文本）
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
        
        Returns:
            numpy.ndarray: 向量数组
        """
        all_vectors = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            vectors = self.embed(batch)
            all_vectors.append(vectors)
        
        if not all_vectors:
            return np.array([])
        
        return np.vstack(all_vectors)


# 全局单例
embedding_service = EmbeddingService()