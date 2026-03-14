"""向量数据库存储"""

import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import loguru

from ..models.embedding import SentenceTransformerEmbedding
from .base import BaseKnowledgeStore


class VectorStore(BaseKnowledgeStore):
    """向量数据库存储实现"""

    def __init__(self, db_path: Path, embedding_model: SentenceTransformerEmbedding):
        """
        初始化向量存储

        Args:
            db_path: 数据库路径
            embedding_model: 嵌入模型
        """
        self.db_path = Path(db_path).absolute()
        self.embedding_model = embedding_model
        self.logger = loguru.logger
        self._client = None
        self._collection = None

    async def initialize(self):
        """初始化向量数据库"""
        # 创建目录
        self.db_path.mkdir(parents=True, exist_ok=True)

        # 初始化ChromaDB客户端
        self._client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 获取或创建集合
        self._collection = self._client.get_or_create_collection(
            name="knowledge",
            metadata={"description": "PyAgent知识库"}
        )

        self.logger.info(f"向量数据库初始化完成: {self.db_path}")

    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """添加知识到向量数据库"""
        knowledge_id = str(uuid.uuid4())

        # 生成嵌入向量
        embedding = await self.embedding_model.aencode(content)

        # 准备元数据
        chroma_metadata = {
            "title": metadata.get("title", ""),
            "category": metadata.get("category", ""),
            "source": metadata.get("source", ""),
            "importance": str(metadata.get("importance", 3)),
            "created_at": metadata.get("date", "")
        }

        # 添加标签
        tags = metadata.get("tags", [])
        if tags:
            chroma_metadata["tags"] = ", ".join(tags)

        # 添加到数据库
        self._collection.add(
            ids=[knowledge_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[chroma_metadata]
        )

        return knowledge_id

    async def get(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """获取知识"""
        try:
            result = self._collection.get(ids=[knowledge_id])

            if not result["ids"]:
                return None

            return {
                "id": result["ids"][0],
                "content": result["documents"][0],
                "metadata": result["metadatas"][0]
            }

        except Exception as e:
            self.logger.error(f"获取知识失败: {e}")
            return None

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索知识"""
        try:
            # 生成查询向量
            query_embedding = await self.embedding_model.aencode(query)

            # 搜索
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # 格式化结果
            formatted_results = []
            for i, knowledge_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "id": knowledge_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else 0
                })

            return formatted_results

        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return []

    async def delete(self, knowledge_id: str) -> bool:
        """删除知识"""
        try:
            self._collection.delete(ids=[knowledge_id])
            return True
        except Exception as e:
            self.logger.error(f"删除知识失败: {e}")
            return False

    async def update(self, knowledge_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """更新知识"""
        try:
            # 先删除旧的
            await self.delete(knowledge_id)

            # 添加新的
            await self.add(content, metadata)

            return True
        except Exception as e:
            self.logger.error(f"更新知识失败: {e}")
            return False

    async def close(self):
        """关闭向量数据库"""
        if self._client:
            self._client.reset()
