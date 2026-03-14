"""智谱AI (GLM) 模型实现"""

import asyncio
from typing import List, Dict, Any, AsyncGenerator
from zhipuai import ZhipuAI
from loguru import logger

from .base import BaseLLM


class GLMLLM(BaseLLM):
    """智谱AI GLM模型实现"""

    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        初始化GLM模型

        Args:
            config: 模型配置
            api_key: 智谱API密钥
        """
        super().__init__(config)

        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY is required")

        # 获取自定义base_url（可选）
        base_url = config.get("base_url", "")

        # 创建客户端，支持自定义API端点
        if base_url:
            self.client = ZhipuAI(api_key=api_key, base_url=base_url)
        else:
            self.client = ZhipuAI(api_key=api_key)

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
            logger.error(f"GLM chat error: {e}")
            raise

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """异步对话"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chat, messages, **kwargs)

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
            logger.error(f"GLM stream chat error: {e}")
            raise

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        loop = asyncio.get_event_loop()

        def sync_gen():
            return self.stream_chat(messages, **kwargs)

        async def async_gen():
            gen = sync_gen()
            while True:
                try:
                    chunk = await loop.run_in_executor(None, next, gen)
                    yield chunk
                except StopIteration:
                    break

        async for chunk in async_gen():
            yield chunk

    def embed(self, text: str) -> List[float]:
        """生成嵌入向量"""
        try:
            response = self.client.embeddings.create(
                model="embedding-2",
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"GLM embed error: {e}")
            # 降级到sentence-transformers
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode(text).tolist()

    async def aembed(self, text: str) -> List[float]:
        """异步嵌入"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed, text)
