"""阿里云通义千问 (Qwen) 模型实现"""

import asyncio
from typing import List, Dict, Any, AsyncGenerator
import httpx
from loguru import logger

from .base import BaseLLM


class QwenLLM(BaseLLM):
    """阿里云通义千问模型实现"""

    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        初始化Qwen模型

        Args:
            config: 模型配置
            api_key: DashScope API密钥
        """
        super().__init__(config)

        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY is required")

        self.api_key = api_key
        # 支持自定义base_url
        self.base_url = config.get("base_url", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        self.client = None
        self.async_client = None

    def _get_client(self):
        """获取同步客户端"""
        if self.client is None:
            self.client = httpx.Client(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=120.0
            )
        return self.client

    def _get_async_client(self):
        """获取异步客户端"""
        if self.async_client is None:
            self.async_client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=120.0
            )
        return self.async_client

    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """格式化消息"""
        # 系统消息转换为user消息
        formatted = []
        for msg in messages:
            if msg["role"] == "system":
                formatted.append({"role": "system", "content": msg["content"]})
            else:
                formatted.append(msg)
        return formatted

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步对话"""
        try:
            client = self._get_client()

            data = {
                "model": self.model,
                "input": {
                    "messages": self._format_messages(messages)
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature)
                }
            }

            response = client.post(self.base_url, json=data)
            response.raise_for_status()
            result = response.json()

            return result["output"]["text"]

        except Exception as e:
            logger.error(f"Qwen chat error: {e}")
            raise

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """异步对话"""
        try:
            client = self._get_async_client()

            data = {
                "model": self.model,
                "input": {
                    "messages": self._format_messages(messages)
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature)
                }
            }

            response = await client.post(self.base_url, json=data)
            response.raise_for_status()
            result = response.json()

            return result["output"]["text"]

        except Exception as e:
            logger.error(f"Qwen async chat error: {e}")
            raise

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话"""
        try:
            client = self._get_client()

            data = {
                "model": self.model,
                "input": {
                    "messages": self._format_messages(messages)
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "incremental_output": True
                }
            }

            with client.stream("POST", self.base_url, json=data) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        import json
                        try:
                            chunk = json.loads(line)
                            if "output" in chunk and "text" in chunk["output"]:
                                yield chunk["output"]["text"]
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Qwen stream chat error: {e}")
            raise

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        try:
            client = self._get_async_client()

            data = {
                "model": self.model,
                "input": {
                    "messages": self._format_messages(messages)
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "incremental_output": True
                }
            }

            async with client.stream("POST", self.base_url, json=data) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            chunk = json.loads(line)
                            if "output" in chunk and "text" in chunk["output"]:
                                yield chunk["output"]["text"]
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Qwen async stream chat error: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        """生成嵌入向量"""
        try:
            client = self._get_client()

            data = {
                "model": "text-embedding-v2",
                "input": {"texts": [text]}
            }

            embed_url = self.base_url.replace(
                "/services/aigc/text-generation/generation",
                "/services/embeddings/text-embedding/text-embedding"
            )
            if not embed_url.endswith("/text-embedding"):
                # 如果base_url已经被完整自定义，使用默认的embed端点
                embed_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"

            response = client.post(embed_url, json=data)
            response.raise_for_status()
            result = response.json()

            return result["output"]["embeddings"][0]["embedding"]

        except Exception as e:
            logger.error(f"Qwen embed error: {e}")
            # 降级到sentence-transformers
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode(text).tolist()

    async def aembed(self, text: str) -> List[float]:
        """异步嵌入"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed, text)

    def close(self):
        """关闭客户端"""
        if self.client:
            self.client.close()

    async def aclose(self):
        """关闭异步客户端"""
        if self.async_client:
            await self.async_client.aclose()
