"""
LLM 客户端 - 大模型 API 调用
支持通义千问、DeepSeek、OpenAI 等
"""

import json
import logging
from typing import Optional, Iterator, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LlmClient:
    """大模型调用客户端"""
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        
        if not self.api_key:
            logger.warning("LLM_API_KEY 未配置，请检查 .env 文件")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        同步调用 LLM
        
        Args:
            prompt: 用户 Prompt
            system_prompt: 系统指令（可选，覆盖默认）
        
        Returns:
            str: 模型生成的回答
        """
        messages = []
        
        # 系统指令
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            logger.error("LLM 调用超时")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API 错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
    
    def chat_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """
        流式调用 LLM
        
        Args:
            prompt: 用户 Prompt
            system_prompt: 系统指令（可选）
        
        Yields:
            str: 逐字输出的文本片段
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"流式 LLM 调用失败: {e}")
            raise


# 全局单例
llm_client = LlmClient()