"""Claude模型实现"""

import asyncio
from typing import List, Dict, Any, AsyncGenerator
from anthropic import AsyncAnthropic, Anthropic
from loguru import logger

from .base import BaseLLM


class ClaudeLLM(BaseLLM):
    """Claude模型实现"""

    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        初始化Claude模型

        Args:
            config: 模型配置
            api_key: Anthropic API密钥
        """
        super().__init__(config)

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步对话"""
        try:
            # 提取系统消息
            system_message = None
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system_message,
                messages=chat_messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude chat error: {e}")
            raise

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """异步对话"""
        try:
            # 提取系统消息
            system_message = None
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system_message,
                messages=chat_messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude async chat error: {e}")
            raise

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话"""
        try:
            system_message = None
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            with self.client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system_message,
                messages=chat_messages
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Claude stream chat error: {e}")
            raise

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        try:
            system_message = None
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            async with self.async_client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system_message,
                messages=chat_messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Claude async stream chat error: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        """
        Claude不提供嵌入API，使用sentence-transformers

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        # 使用sentence-transformers作为备选
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()

    async def aembed(self, text: str) -> List[float]:
        """异步嵌入"""
        # 在线程池中运行同步代码
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed, text)
