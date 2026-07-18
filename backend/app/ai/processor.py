"""
文本切分与文件读取模块
使用 LangChain RecursiveCharacterTextSplitter 进行中文文本智能切分
支持 PDF、Word、TXT 文件格式
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any

import pdfplumber
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.exceptions import BizException


# ============ 配置常量 ============

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

# 中文优先的分隔符
SEPARATORS = [
    "\n\n",  # 段落分隔
    "\n",    # 换行
    "。",    # 句号
    "！",    # 感叹号
    "？",    # 问号
    "；",    # 分号
    "，",    # 逗号
    " ",     # 空格
    "",      # 字符级别
]


class DocumentProcessor:
    """文档处理器：负责文件读取和文本切分"""
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 每块文本的最大字符数
            chunk_overlap: 块之间的重叠字符数（保证上下文连贯）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=SEPARATORS,
            keep_separator=False,
            strip_whitespace=True,
        )
    
    # ============ 文件读取 ============
    
    def extract_text(self, file_path: str) -> str:
        """
        根据文件扩展名提取文本内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的纯文本内容
            
        Raises:
            BizException: 不支持的文件格式或读取失败
        """
        print(f"=== extract_text 开始 ===")
        print(f"文件路径: {file_path}")
        
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        print(f"文件扩展名: {ext}")
        
        if ext == ".txt":
            return self._read_txt(file_path)
        elif ext == ".pdf":
            return self._read_pdf(file_path)
        elif ext in (".docx", ".doc"):
            return self._read_docx(file_path)
        else:
            raise BizException(code=400, message=f"不支持的文件格式: {ext}，仅支持 .txt, .pdf, .docx")
    
    def _read_txt(self, file_path: Path) -> str:
        """读取 TXT 文件，统一 UTF-8 编码"""
        encodings = ["utf-8", "gbk", "gb2312", "utf-16"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise BizException(code=400, message=f"无法解码文件: {file_path}，尝试的编码: {encodings}")
    
    def _read_pdf(self, file_path: Path) -> str:
        """使用 pdfplumber 读取 PDF 文件"""
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            full_text = "\n\n".join(text_parts)
            if not full_text.strip():
                raise BizException(code=400, message="PDF 文件未提取到任何文本内容，可能为扫描件或图片型 PDF")
            return full_text
        except BizException:
            raise
        except Exception as e:
            raise BizException(code=500, message=f"PDF 读取失败: {str(e)}")
    
    def _read_docx(self, file_path: Path) -> str:
        """使用 python-docx 读取 Word 文档"""
        try:
            doc = DocxDocument(file_path)
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            full_text = "\n".join(text_parts)
            if not full_text.strip():
                raise BizException(code=400, message="Word 文档未提取到任何文本内容")
            return full_text
        except BizException:
            raise
        except Exception as e:
            raise BizException(code=500, message=f"Word 文档读取失败: {str(e)}")
    
    # ============ 文本切分 ============
    
    def split_text(self, text: str, doc_id: int) -> List[Dict[str, Any]]:
        """
        将文本切分为多个块，并附加元数据
        
        Args:
            text: 待切分的原始文本
            doc_id: 文档 ID，用于溯源
            
        Returns:
            切分结果列表，每个元素包含:
                - content: 文本块内容
                - doc_id: 文档 ID
                - chunk_idx: 块序号（从 0 开始）
        """
        print(f"=== split_text 开始 ===")
        print(f"文档 ID: {doc_id}, 文本长度: {len(text)}")
        
        if not text or not text.strip():
            return []
        
        # 使用 LangChain 切分
        chunks = self.text_splitter.split_text(text)
        
        # 过滤空块
        chunks = [c.strip() for c in chunks if c.strip()]
        
        # 构建带元数据的结果
        results = []
        for idx, chunk in enumerate(chunks):
            results.append({
                "content": chunk,
                "doc_id": doc_id,
                "chunk_idx": idx,
            })
        
        print(f"切分完成，共 {len(results)} 块")
        return results
    
    def process_document(self, file_path: str, doc_id: int) -> List[Dict[str, Any]]:
        """
        完整的文档处理流程：读取 + 切分
        
        Args:
            file_path: 文件路径
            doc_id: 文档 ID
            
        Returns:
            切分后的文本块列表（带元数据）
        """
        print(f"=== process_document 开始 ===")
        print(f"文档 ID: {doc_id}, 文件路径: {file_path}")
        
        # 1. 提取文本
        raw_text = self.extract_text(file_path)
        
        # 2. 基本清洗：去除多余空白，合并连续换行
        raw_text = re.sub(r"\n\s*\n", "\n\n", raw_text)
        raw_text = raw_text.strip()
        
        if not raw_text:
            raise BizException(code=400, message="文档内容为空")
        
        # 3. 切分
        chunks = self.split_text(raw_text, doc_id)
        
        if not chunks:
            raise BizException(code=400, message="文档切分后无有效内容")
        
        return chunks


# ============ 全局实例 ============

document_processor = DocumentProcessor()