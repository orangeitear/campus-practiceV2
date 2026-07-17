"""
Embedding 向量化模块
使用阿里云百炼 DashScope API 进行文本向量化
"""
import os
import numpy as np
from typing import List, Optional

from app.core.config import settings
from app.core.exceptions import BizException


class EmbeddingClient:
    """Embedding 客户端封装类（使用阿里云百炼 API）"""
    
    # 阿里云百炼 Embedding 模型
    DEFAULT_MODEL = "text-embedding-v4"
    DEFAULT_DIM = 1024  # text-embedding-v4 默认维度
    
    def __init__(self):
        """初始化 Embedding 客户端"""
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = settings.EMBEDDING_BASE_URL or "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        self.model = settings.EMBEDDING_MODEL or self.DEFAULT_MODEL
        self.dim = settings.EMBEDDING_DIM or self.DEFAULT_DIM
        
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 未设置，请在 .env 文件中配置")
        
        # 缓存向量维度
        self._dimension = None
    
    @property
    def embedding_dim(self) -> int:
        """获取向量维度"""
        if self._dimension is None:
            self._dimension = self.dim
        return self._dimension
    
    def _call_api(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        调用阿里云百炼 Embedding API
        
        Args:
            texts: 文本列表
            
        Returns:
            向量数组，shape: (n, dim)
        """
        import dashscope
        from dashscope import TextEmbedding
        
        if not texts:
            return None
        
        print(f"=== Embedding API 调用 ===")
        print(f"模型: {self.model}, 目标维度: {self.dim}")
        print(f"文本数量: {len(texts)}")
        
        try:
            dashscope.api_key = self.api_key
            resp = TextEmbedding.call(
                model=self.model,
                input=texts,
                dimensions=self.dim,  # 显式指定向量维度为 1024
            )
            
            if resp.status_code == 200:
                embeddings = []
                for item in resp.output.get("embeddings", []):
                    embeddings.append(item.get("embedding", []))
                actual_dim = len(embeddings[0]) if embeddings else 0
                print(f"向量化成功，实际维度: {actual_dim}")
                return np.array(embeddings, dtype=np.float32)
            else:
                raise BizException(
                    code=resp.status_code, 
                    message=f"Embedding API 调用失败: {resp.message}"
                )
                
        except BizException:
            raise
        except Exception as e:
            raise BizException(code=500, message=f"Embedding 向量化失败: {str(e)}")
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        将文本列表转换为向量（支持批量）
        
        Args:
            texts: 文本列表
            
        Returns:
            向量数组，shape: (n, embedding_dim)，float32 类型
        """
        if not texts:
            return np.array([], dtype=np.float32)
        
        # 阿里云百炼单次最多支持 25 条文本，分批处理
        batch_size = 25
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_emb = self._call_api(batch)
            if batch_emb is not None:
                all_embeddings.append(batch_emb)
        
        if not all_embeddings:
            return np.array([], dtype=np.float32)
        
        return np.vstack(all_embeddings)
    
    def embed_single(self, text: str) -> np.ndarray:
        """
        向量化单个文本
        
        Args:
            text: 单个文本
            
        Returns:
            向量数组，shape: (embedding_dim,)
        """
        result = self.embed([text])
        if len(result) == 0:
            return np.array([], dtype=np.float32)
        return result[0]


# ============ 全局实例 ============

embedding_client = EmbeddingClient()