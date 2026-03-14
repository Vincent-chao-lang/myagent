"""混合存储实现"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import loguru

from .base import BaseKnowledgeStore
from .file_store import FileStore
from .vector_store import VectorStore
from ..models.factory import create_embedding_model
from ..daily.skills import SkillTracker


class HybridKnowledgeStore(BaseKnowledgeStore):
    """混合存储实现（文件 + 向量，支持禁用向量库）"""

    def __init__(
        self,
        file_store_path: Path,
        vector_db_path: Path,
        embedding_model: str,
        use_vector_db: bool = True,
        offline_mode: bool = False,
        cache_dir: Path = None
    ):
        """
        初始化混合存储

        Args:
            file_store_path: 文件存储路径
            vector_db_path: 向量数据库路径
            embedding_model: 嵌入模型名称
            use_vector_db: 是否使用向量数据库
            offline_mode: 离线模式
            cache_dir: 模型缓存目录
        """
        self.use_vector_db = use_vector_db
        self.offline_mode = offline_mode

        # 文件存储始终启用
        self.file_store = FileStore(file_store_path)
        self.skill_tracker = SkillTracker()
        self.logger = loguru.logger

        # 向量存储和嵌入模型（可选）
        self.vector_store = None
        self.embedding = None

        if use_vector_db and not offline_mode:
            try:
                self.embedding = create_embedding_model(embedding_model)
                if cache_dir:
                    # 设置缓存目录
                    self.embedding.cache_dir = cache_dir
                self.vector_store = VectorStore(vector_db_path, self.embedding)
            except Exception as e:
                self.logger.warning(f"向量存储初始化失败，将仅使用文件存储: {e}")
                self.use_vector_db = False

    async def initialize(self):
        """初始化混合存储"""
        # 始终初始化文件存储
        await self.file_store.initialize()

        # 条件初始化向量存储
        if self.use_vector_db and self.vector_store:
            try:
                await self.vector_store.initialize()
                self.logger.info("向量数据库已启用")
            except Exception as e:
                self.logger.warning(f"向量数据库初始化失败，将仅使用文件存储: {e}")
                self.use_vector_db = False

        # 初始化技能追踪器
        await self.skill_tracker.initialize()

        if self.offline_mode:
            self.logger.info("离线模式：仅使用文件存储")
        elif self.use_vector_db:
            self.logger.info("混合知识库初始化完成（文件 + 向量）")
        else:
            self.logger.info("知识库初始化完成（仅文件存储）")

    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        添加知识到存储

        根据配置决定存储策略：
        - 向量库启用时：结构化内容→文件，非结构化→向量
        - 向量库禁用时：所有内容→文件
        """
        category = metadata.get("category", "").lower()

        if self.use_vector_db and self.vector_store:
            # 混合模式
            use_file = category in ["pattern", "architecture", "practice", "feature"]

            if use_file:
                # 存储到文件
                knowledge_id = await self.file_store.add(content, metadata)
                self.logger.debug(f"知识添加到文件存储: {knowledge_id}")
            else:
                # 存储到向量数据库
                knowledge_id = await self.vector_store.add(content, metadata)
                self.logger.debug(f"知识添加到向量存储: {knowledge_id}")
        else:
            # 仅文件模式
            knowledge_id = await self.file_store.add(content, metadata)
            self.logger.debug(f"知识添加到文件存储: {knowledge_id}")

        # 更新技能
        tags = metadata.get("tags", [])
        title = metadata.get("title", "")
        self.skill_tracker.update_from_content(content, title, tags)

        return knowledge_id

    async def get(self, knowledge_id: str) -> Dict[str, Any]:
        """获取知识"""
        # 先尝试文件存储
        result = await self.file_store.get(knowledge_id)
        if result:
            return result

        # 再尝试向量存储
        if self.vector_store:
            result = await self.vector_store.get(knowledge_id)
            return result or {}

        return {}

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知识

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.use_vector_db or not self.vector_store:
            # 仅使用文件存储的关键词搜索
            return await self.file_store.search(query, top_k)

        # 混合搜索（文件 + 向量）
        try:
            file_results, vector_results = await asyncio.gather(
                self.file_store.search(query, top_k),
                self.vector_store.search(query, top_k)
            )

            # 合并结果（去重）
            seen_ids = set()
            merged_results = []

            for result in vector_results + file_results:
                result_id = result.get("id", "")
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    merged_results.append(result)

            return merged_results[:top_k]

        except Exception as e:
            self.logger.warning(f"向量搜索失败，使用文件搜索: {e}")
            return await self.file_store.search(query, top_k)

    async def delete(self, knowledge_id: str) -> bool:
        """删除知识"""
        # 尝试从两个存储中删除
        results = await asyncio.gather(
            self.file_store.delete(knowledge_id),
            self.vector_store.delete(knowledge_id) if self.vector_store else asyncio.sleep(0),
            return_exceptions=True
        )

        return any(r if not isinstance(r, Exception) else False for r in results)

    async def update(self, knowledge_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """更新知识"""
        # 尝试更新两个存储
        results = await asyncio.gather(
            self.file_store.update(knowledge_id, content, metadata),
            self.vector_store.update(knowledge_id, content, metadata) if self.vector_store else asyncio.sleep(0),
            return_exceptions=True
        )

        return any(r if not isinstance(r, Exception) else False for r in results)

    async def close(self):
        """关闭混合存储"""
        await self.file_store.close()

        if self.vector_store:
            await self.vector_store.close()

    async def get_all_knowledge(self) -> List[Dict[str, Any]]:
        """获取所有知识"""
        all_knowledge = []

        # 从文件存储获取
        metadata_dir = self.file_store.store_path / "metadata"
        if metadata_dir.exists():
            import json
            for metadata_file in metadata_dir.glob("*.json"):
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    all_knowledge.append(metadata)
                except Exception:
                    pass

        return all_knowledge
