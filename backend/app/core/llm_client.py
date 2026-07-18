import json
import httpx
from typing import AsyncGenerator, Optional, Dict, Any

from app.core.config import settings


class LLMClient:
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = settings.LLM_BASE_URL or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = settings.LLM_MODEL or "qwen-turbo"
        self.timeout = 60.0

    async def chat(self, messages: list, temperature: float = 0.3) -> str:
        """同步调用 LLM（非流式）"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list, temperature: float = 0.3) -> AsyncGenerator[str, None]:
        """流式调用 LLM，逐 token 返回"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue


# 全局实例
llm_client = LLMClient()