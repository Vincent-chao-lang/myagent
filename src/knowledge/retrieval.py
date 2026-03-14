"""检索引擎"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class RetrievalResult:
    """检索结果"""
    content: str
    title: str
    category: str
    source: str
    score: float
    metadata: Dict[str, Any]


class RetrievalEngine:
    """检索引擎"""

    def __init__(self, knowledge_store):
        """
        初始化检索引擎

        Args:
            knowledge_store: 知识库实例
        """
        self.knowledge_store = knowledge_store
        self.logger = logger

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        检索相关知识

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            检索结果列表
        """
        try:
            # 基础搜索
            results = await self.knowledge_store.search(query, top_k * 2)

            # 应用过滤
            if filters:
                results = self._apply_filters(results, filters)

            # 转换为检索结果
            retrieval_results = []
            for result in results[:top_k]:
                retrieval_results.append(RetrievalResult(
                    content=result.get("content", ""),
                    title=result.get("title", ""),
                    category=result.get("category", ""),
                    source=result.get("source", ""),
                    score=result.get("_score", result.get("distance", 0)),
                    metadata=result.get("metadata", {})
                ))

            return retrieval_results

        except Exception as e:
            self.logger.error(f"检索失败: {e}")
            return []

    def _apply_filters(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """应用过滤条件"""
        filtered = results

        # 按类别过滤
        if "category" in filters:
            category = filters["category"]
            filtered = [r for r in filtered if r.get("category", "").lower() == category.lower()]

        # 按标签过滤
        if "tags" in filters:
            required_tags = set(filters["tags"])
            filtered = [
                r for r in filtered
                if required_tags.intersection(set(r.get("tags", [])))
            ]

        # 按重要性过滤
        if "min_importance" in filters:
            min_imp = filters["min_importance"]
            filtered = [r for r in filtered if r.get("importance", 0) >= min_imp]

        return filtered

    async def retrieve_with_rerank(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        检索并重排序

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            重排序后的检索结果
        """
        # 获取更多候选结果
        results = await self.retrieve(query, top_k * 3, filters)

        # 简单的重排序：基于标题和类别的匹配度
        query_lower = query.lower()

        for result in results:
            boost = 0

            # 标题匹配加分
            if query_lower in result.title.lower():
                boost += 2

            # 类别匹配加分
            if query_lower in result.category.lower():
                boost += 1

            result.score += boost

        # 重新排序
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:top_k]

    async def retrieve_by_category(
        self,
        category: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        按类别检索

        Args:
            category: 类别名称
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        return await self.retrieve(
            query="",
            top_k=top_k,
            filters={"category": category}
        )
