"""LLM基类接口"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional


class BaseLLM(ABC):
    """大语言模型基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化LLM

        Args:
            config: 模型配置
        """
        self.config = config
        self.model = config.get("model", "")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        同步对话接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            模型回复
        """
        pass

    @abstractmethod
    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        异步对话接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            模型回复
        """
        pass

    @abstractmethod
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        流式对话接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            流式响应生成器
        """
        pass

    @abstractmethod
    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """
        异步流式对话接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Yields:
            模型回复片段
        """
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        生成文本嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        pass

    @abstractmethod
    async def aembed(self, text: str) -> List[float]:
        """
        异步生成文本嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        pass


class BaseEmbedding(ABC):
    """嵌入模型基类"""

    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """编码文本为向量"""
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码文本"""
        pass
