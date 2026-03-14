"""测试知识管理模块"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from src.knowledge.file_store import FileStore
from src.knowledge.vector_store import VectorStore
from src.knowledge.hybrid_store import HybridKnowledgeStore
from src.models.embedding import SentenceTransformerEmbedding


class TestFileStore:
    """测试文件存储"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    async def file_store(self, temp_dir):
        """创建文件存储实例"""
        store = FileStore(temp_dir)
        await store.initialize()
        yield store
        await store.close()

    @pytest.mark.asyncio
    async def test_initialize(self, file_store, temp_dir):
        """测试初始化"""
        assert (temp_dir / "patterns").exists()
        assert (temp_dir / "metadata").exists()

    @pytest.mark.asyncio
    async def test_add_and_get(self, file_store):
        """测试添加和获取知识"""
        metadata = {
            "title": "Test Knowledge",
            "category": "pattern",
            "tags": ["test", "python"]
        }

        knowledge_id = await file_store.add("Test content", metadata)
        assert knowledge_id is not None

        knowledge = await file_store.get(knowledge_id)
        assert knowledge is not None
        assert knowledge["title"] == "Test Knowledge"
        assert knowledge["content"] == "Test content"

    @pytest.mark.asyncio
    async def test_search(self, file_store):
        """测试搜索"""
        # 添加几条知识
        await file_store.add("Python async/await content", {
            "title": "Async Programming",
            "category": "practice",
            "tags": ["async", "python"]
        })

        await file_store.add("FastAPI guide", {
            "title": "FastAPI Tutorial",
            "category": "practice",
            "tags": ["fastapi", "web"]
        })

        # 搜索
        results = await file_store.search("async")
        assert len(results) > 0
        assert "async" in results[0]["title"].lower() or "async" in str(results[0].get("tags", []))


class TestVectorStore:
    """测试向量存储"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def embedding_model(self):
        """创建嵌入模型"""
        return SentenceTransformerEmbedding("all-MiniLM-L6-v2")

    @pytest.fixture
    async def vector_store(self, temp_dir, embedding_model):
        """创建向量存储实例"""
        store = VectorStore(temp_dir, embedding_model)
        await store.initialize()
        yield store
        await store.close()

    @pytest.mark.asyncio
    async def test_initialize(self, vector_store, temp_dir):
        """测试初始化"""
        assert temp_dir.exists()

    @pytest.mark.asyncio
    async def test_add_and_search(self, vector_store):
        """测试添加和搜索"""
        metadata = {
            "title": "Python Type Hints",
            "category": "practice",
            "tags": ["typing", "python"]
        }

        knowledge_id = await vector_store.add(
            "Python type hints allow you to specify types for variables",
            metadata
        )
        assert knowledge_id is not None

        # 搜索
        results = await vector_store.search("typing", top_k=1)
        assert len(results) > 0
        assert "type" in results[0]["content"].lower()


class TestHybridStore:
    """测试混合存储"""

    @pytest.fixture
    def temp_dirs(self):
        """创建临时目录"""
        temp1 = tempfile.mkdtemp()
        temp2 = tempfile.mkdtemp()
        yield Path(temp1), Path(temp2)
        shutil.rmtree(temp1)
        shutil.rmtree(temp2)

    @pytest.fixture
    async def hybrid_store(self, temp_dirs):
        """创建混合存储实例"""
        file_path, vector_path = temp_dirs
        store = HybridKnowledgeStore(
            file_path,
            vector_path,
            "all-MiniLM-L6-v2"
        )
        await store.initialize()
        yield store
        await store.close()

    @pytest.mark.asyncio
    async def test_add_to_file_store(self, hybrid_store):
        """测试添加到文件存储"""
        metadata = {
            "title": "Singleton Pattern",
            "category": "pattern",
            "tags": ["design pattern"]
        }

        knowledge_id = await hybrid_store.add(
            "The singleton pattern ensures a class has only one instance",
            metadata
        )
        assert knowledge_id is not None

    @pytest.mark.asyncio
    async def test_add_to_vector_store(self, hybrid_store):
        """测试添加到向量存储"""
        metadata = {
            "title": "Learning Article",
            "category": "general",
            "tags": ["python"]
        }

        knowledge_id = await hybrid_store.add(
            "This is a general learning article about Python",
            metadata
        )
        assert knowledge_id is not None

    @pytest.mark.asyncio
    async def test_search(self, hybrid_store):
        """测试混合搜索"""
        # 添加一些知识
        await hybrid_store.add(
            "Async programming in Python",
            {"title": "Async", "category": "practice", "tags": ["async"]}
        )

        await hybrid_store.add(
            "Design pattern: Singleton",
            {"title": "Singleton", "category": "pattern", "tags": ["pattern"]}
        )

        # 搜索
        results = await hybrid_store.search("async")
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
