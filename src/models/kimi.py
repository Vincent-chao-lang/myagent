"""月之暗面 (Kimi/Moonshot) 模型实现

Kimi API兼容OpenAI格式
"""

import asyncio
from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI, OpenAI
from loguru import logger

from .base import BaseLLM


class KimiLLM(BaseLLM):
    """Kimi (Moonshot) 模型实现 (兼容OpenAI API)"""

    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        初始化Kimi模型

        Args:
            config: 模型配置
            api_key: Moonshot API密钥
        """
        super().__init__(config)

        if not api_key:
            raise ValueError("MOONSHOT_API_KEY is required")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        self.async_client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步对话"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Kimi chat error: {e}")
            raise

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """异步对话"""
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Kimi async chat error: {e}")
            raise

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Kimi stream chat error: {e}")
            raise

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                stream=True
            )

            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Kimi async stream chat error: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        """生成嵌入向量 (Kimi不提供embed API)"""
        # 降级到sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()

    async def aembed(self, text: str) -> List[float]:
        """异步嵌入"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed, text)
