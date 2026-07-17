"""
文档处理器 - 文本提取与切分
支持 PDF、DOCX、TXT、MD 等格式
"""

import os
import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理服务"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self._init_splitter()
    
    def _init_splitter(self):
        """初始化文本切分器"""
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
                keep_separator=False,
                length_function=len,
            )
            logger.info(f"文本切分器初始化: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
        except ImportError:
            logger.error("请安装 langchain-text-splitters: pip install langchain-text-splitters")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """
        从文件中提取文本
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 提取的文本内容
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt' or ext == '.md':
            return self._extract_txt(file_path)
        elif ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext == '.docx':
            return self._extract_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def _extract_txt(self, file_path: str) -> str:
        """提取 TXT/MD 文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_pdf(self, file_path: str) -> str:
        """提取 PDF 文本"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
        except ImportError:
            logger.error("请安装 pypdf: pip install pypdf")
            raise
    
    def _extract_docx(self, file_path: str) -> str:
        """提取 DOCX 文本"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(text)
        except ImportError:
            logger.error("请安装 python-docx: pip install python-docx")
            raise
    
    def split_text(self, text: str) -> List[str]:
        """
        切分文本为 chunks
        
        Args:
            text: 原始文本
        
        Returns:
            List[str]: 切分后的文本块列表
        """
        if not text or not text.strip():
            return []
        
        chunks = self.splitter.split_text(text)
        logger.debug(f"文本切分完成: {len(chunks)} 个块")
        return chunks
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        完整处理：提取 + 切分
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict: {chunks: List[str], text: str, chunk_count: int}
        """
        text = self.extract_text(file_path)
        chunks = self.split_text(text)
        
        return {
            "text": text,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }


# 全局单例
document_processor = DocumentProcessor()