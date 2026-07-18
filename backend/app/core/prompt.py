from typing import List, Dict, Any

SYSTEM_PROMPT = """你是河海大学校园问答助手。你的任务是基于提供的参考资料，准确回答用户的问题。

规则：
1. **仅依据参考资料回答**：你的回答必须完全基于下面提供的参考资料，不要使用你自身的知识。
2. **资料中没有的，如实说明**：如果参考资料中没有包含回答所需的信息，请明确告诉用户"资料中没有相关信息"。
3. **引用来源**：在回答中需要引用具体来源时，用 [来源: 文档标题] 标注。
4. **语言风格**：回答要准确、清晰、有条理，语气友好专业。
"""


def build_prompt(question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    构建 LLM 对话消息列表
    """
    if not chunks:
        # 无检索结果时的回退提示
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""用户问题：{question}

检索结果：未找到与问题相关的参考资料。

请告知用户：资料中没有相关信息，无法回答该问题。"""}
        ]

    # 拼接参考资料
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        content = chunk.get("content", "")
        title = chunk.get("title", "未知文档")
        context_parts.append(f"[{i}] 来自《{title}》：\n{content}")

    context = "\n\n---\n\n".join(context_parts)

    user_content = f"""用户问题：{question}

参考资料：
{context}

请根据以上参考资料回答用户的问题。如果资料中没有相关信息，请明确说明。"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]


def build_chat_messages(question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """build_prompt 的别名，保持命名一致"""
    return build_prompt(question, chunks)