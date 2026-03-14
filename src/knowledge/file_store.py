"""文件存储"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import loguru

from .base import BaseKnowledgeStore


class FileStore(BaseKnowledgeStore):
    """文件存储实现"""

    def __init__(self, store_path: Path):
        """
        初始化文件存储

        Args:
            store_path: 存储路径
        """
        self.store_path = Path(store_path).absolute()
        self.logger = loguru.logger

    async def initialize(self):
        """初始化文件存储"""
        # 创建必要目录
        directories = [
            self.store_path / "patterns",
            self.store_path / "architectures",
            self.store_path / "best_practices",
            self.store_path / "python_features",
            self.store_path / "general",
            self.store_path / "metadata"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"文件存储初始化完成: {self.store_path}")

    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        添加知识到文件存储

        Args:
            content: 知识内容
            metadata: 元数据

        Returns:
            知识ID
        """
        knowledge_id = str(uuid.uuid4())

        # 确定存储目录
        category = metadata.get("category", "general")
        category_path = self._get_category_path(category)

        # 保存内容
        content_file = category_path / f"{knowledge_id}.md"
        with open(content_file, "w", encoding="utf-8") as f:
            f.write(content)

        # 保存元数据
        metadata_file = self.store_path / "metadata" / f"{knowledge_id}.json"
        metadata_entry = {
            "id": knowledge_id,
            "content_path": str(content_file),
            "category": category,
            "title": metadata.get("title", ""),
            "tags": metadata.get("tags", []),
            "source": metadata.get("source", ""),
            "importance": metadata.get("importance", 3),
            "created_at": datetime.now().isoformat()
        }

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata_entry, f, ensure_ascii=False, indent=2)

        return knowledge_id

    async def get(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """获取知识"""
        metadata_file = self.store_path / "metadata" / f"{knowledge_id}.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # 读取内容
        content_path = Path(metadata["content_path"])
        if content_path.exists():
            with open(content_path, "r", encoding="utf-8") as f:
                metadata["content"] = f.read()
        else:
            metadata["content"] = ""

        return metadata

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知识（基于关键词匹配）

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            搜索结果列表
        """
        results = []
        query_lower = query.lower()

        # 遍历所有元数据文件
        metadata_dir = self.store_path / "metadata"
        if not metadata_dir.exists():
            return results

        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                # 检查匹配
                score = 0

                # 标题匹配
                if query_lower in metadata.get("title", "").lower():
                    score += 10

                # 标签匹配
                for tag in metadata.get("tags", []):
                    if query_lower in tag.lower():
                        score += 5

                # 类别匹配
                if query_lower in metadata.get("category", "").lower():
                    score += 3

                if score > 0:
                    # 读取内容
                    content_path = Path(metadata["content_path"])
                    if content_path.exists():
                        with open(content_path, "r", encoding="utf-8") as f:
                            metadata["content"] = f.read()

                    metadata["_score"] = score
                    results.append(metadata)

            except Exception as e:
                self.logger.warning(f"读取元数据失败 {metadata_file}: {e}")

        # 按得分排序
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)

        return results[:top_k]

    async def delete(self, knowledge_id: str) -> bool:
        """删除知识"""
        metadata_file = self.store_path / "metadata" / f"{knowledge_id}.json"

        if not metadata_file.exists():
            return False

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # 删除内容文件
            content_path = Path(metadata["content_path"])
            if content_path.exists():
                content_path.unlink()

            # 删除元数据文件
            metadata_file.unlink()

            return True

        except Exception as e:
            self.logger.error(f"删除知识失败: {e}")
            return False

    async def update(self, knowledge_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """更新知识"""
        metadata_file = self.store_path / "metadata" / f"{knowledge_id}.json"

        if not metadata_file.exists():
            return False

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                old_metadata = json.load(f)

            # 更新内容
            content_path = Path(old_metadata["content_path"])
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(content)

            # 更新元数据
            old_metadata.update({
                "title": metadata.get("title", old_metadata.get("title", "")),
                "tags": metadata.get("tags", old_metadata.get("tags", [])),
                "importance": metadata.get("importance", old_metadata.get("importance", 3)),
                "updated_at": datetime.now().isoformat()
            })

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(old_metadata, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            self.logger.error(f"更新知识失败: {e}")
            return False

    def _get_category_path(self, category: str) -> Path:
        """获取类别路径"""
        category_map = {
            "pattern": "patterns",
            "patterns": "patterns",
            "architecture": "architectures",
            "architectures": "architectures",
            "practice": "best_practices",
            "best_practice": "best_practices",
            "best_practices": "best_practices",
            "feature": "python_features",
            "python_feature": "python_features",
            "python_features": "python_features"
        }

        dir_name = category_map.get(category.lower(), "general")
        return self.store_path / dir_name

    async def close(self):
        """关闭文件存储"""
        pass
