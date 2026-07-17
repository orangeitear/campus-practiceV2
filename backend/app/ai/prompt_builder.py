"""
Prompt 构建器 - 系统指令 + 上下文拼接
"""

from typing import List, Dict, Any
import tiktoken
from app.core.config import settings


class PromptBuilder:
    """Prompt 构建服务"""
    
    def __init__(self):
        self.system_prompt = """你是河海大学校园问答助手。请严格遵循以下规则：

1. 只根据【参考资料】中的内容回答问题
2. 如果参考资料中没有相关内容，请诚实地说"知识库中暂无相关信息，无法回答您的问题"
3. 不要编造或猜测任何信息
4. 回答要简洁、准确、有条理
5. 如果参考资料中有多个相关段落，综合组织后回答
6. 引用参考资料时，在回答中标注来源"""

        self.user_template = """
【参考资料】
{context}

【用户问题】
{question}

【回答】
"""
    
    def build(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """
        构建完整的 Prompt
        
        Args:
            question: 用户问题
            chunks: 检索到的文本块列表
        
        Returns:
            str: 完整的 Prompt
        """
        # 拼接上下文
        if not chunks:
            context = "（暂无相关参考资料）"
        else:
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                content = chunk.get('content', '')
                doc_id = chunk.get('doc_id', '未知')
                context_parts.append(f"[{i}] {content} (来源: 文档 {doc_id})")
            context = "\n".join(context_parts)
        
        # 拼接完整 Prompt
        user_prompt = self.user_template.format(
            context=context,
            question=question
        )
        
        return f"{self.system_prompt}\n\n{user_prompt}"
    
    def build_without_context(self, question: str) -> str:
        """构建无上下文的 Prompt（仅系统指令 + 问题）"""
        return f"{self.system_prompt}\n\n【用户问题】\n{question}\n\n【回答】\n"
    
    def count_tokens(self, text: str) -> int:
        """估算 Token 数量"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # 粗略估算：中文约 1.5 字/token
            return len(text) // 2


# 全局单例
prompt_builder = PromptBuilder()