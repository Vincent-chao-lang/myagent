"""本地模型实现（Ollama）"""

import asyncio
import httpx
from typing import List, Dict, Any, AsyncGenerator
from loguru import logger

from .base import BaseLLM


class LocalLLM(BaseLLM):
    """本地模型实现（通过Ollama API）"""

    def __init__(self, config: Dict[str, Any], endpoint: str):
        """
        初始化本地模型

        Args:
            config: 模型配置
            endpoint: 模型服务端点
        """
        super().__init__(config)

        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.Client(timeout=120.0)
        self.async_client = httpx.AsyncClient(timeout=120.0)

    def _make_request(self, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
        """构造请求数据"""
        # 提取系统消息
        system = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        data = {
            "model": self.model,
            "messages": chat_messages,
            "stream": stream,
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature
            }
        }

        if system:
            data["system"] = system

        return data

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步对话"""
        try:
            data = self._make_request(messages)

            response = self.client.post(
                f"{self.endpoint}/v1/chat/completions",
                json=data
            )

            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Local model chat error: {e}")
            raise

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """异步对话"""
        try:
            data = self._make_request(messages)

            response = await self.async_client.post(
                f"{self.endpoint}/v1/chat/completions",
                json=data
            )

            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Local model async chat error: {e}")
            raise

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话"""
        try:
            data = self._make_request(messages, stream=True)

            with self.client.stream(
                "POST",
                f"{self.endpoint}/v1/chat/completions",
                json=data
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        # 解析SSE格式
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break

                            import json
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Local model stream chat error: {e}")
            raise

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        try:
            data = self._make_request(messages, stream=True)

            async with self.async_client.stream(
                "POST",
                f"{self.endpoint}/v1/chat/completions",
                json=data
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break

                            import json
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Local model async stream chat error: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        """生成嵌入向量"""
        try:
            response = self.client.post(
                f"{self.endpoint}/api/embeddings",
                json={
                    "model": "nomic-embed-text",  # 常用的本地嵌入模型
                    "prompt": text
                }
            )

            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])

        except Exception as e:
            logger.warning(f"Local model embed error: {e}, using sentence-transformers")
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
        self.client.close()

    async def aclose(self):
        """关闭异步客户端"""
        await self.async_client.aclose()
