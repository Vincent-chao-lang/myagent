"""知识库基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class Knowledge:
    """知识条目"""

    def __init__(
        self,
        content: str,
        title: str = "",
        category: str = "",
        tags: Optional[List[str]] = None,
        source: str = "",
        importance: int = 3,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.title = title
        self.category = category
        self.tags = tags or []
        self.source = source
        self.importance = importance
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "title": self.title,
            "category": self.category,
            "tags": self.tags,
            "source": self.source,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class BaseKnowledgeStore(ABC):
    """知识库基类"""

    @abstractmethod
    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        添加知识

        Args:
            content: 知识内容
            metadata: 元数据

        Returns:
            知识ID
        """
        pass

    @abstractmethod
    async def get(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """
        获取知识

        Args:
            knowledge_id: 知识ID

        Returns:
            知识内容
        """
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知识

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            搜索结果列表
        """
        pass

    @abstractmethod
    async def delete(self, knowledge_id: str) -> bool:
        """
        删除知识

        Args:
            knowledge_id: 知识ID

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    async def update(self, knowledge_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """
        更新知识

        Args:
            knowledge_id: 知识ID
            content: 新内容
            metadata: 新元数据

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    async def initialize(self):
        """初始化知识库"""
        pass

    @abstractmethod
    async def close(self):
        """关闭知识库"""
        pass
