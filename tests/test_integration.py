"""集成测试"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from src.core.agent import PyAgent
from src.core.config import Config


class TestAgent:
    """Agent集成测试"""

    @pytest.fixture
    def temp_config(self):
        """创建临时配置"""
        temp = tempfile.mkdtemp()
        config_content = """
agent:
  name: "TestAgent"
  version: "0.1.0"

model:
  type: "claude"
  claude:
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 1000

knowledge:
  file_store_path: "{temp}/knowledge"
  vector_db_path: "{temp}/vector_db"
  embedding_model: "all-MiniLM-L6-v2"

learning:
  schedule: "02:00"
  sources: []
  max_daily_learnings: 5

daily:
  report_path: "{temp}/reports"

cli:
  max_history: 10
"""
        config_path = Path(temp) / "config.yaml"
        with open(config_path, "w") as f:
            f.write(config_content.format(temp=temp))

        yield temp, config_path

        shutil.rmtree(temp)

    @pytest.fixture
    def config_obj(self, temp_config):
        """创建配置对象"""
        temp, config_path = temp_config
        return Config(str(config_path))

    @pytest.mark.asyncio
    async def test_agent_initialization(self, config_obj):
        """测试Agent初始化"""
        # Mock LLM creation
        from unittest.mock import patch, Mock

        with patch("src.models.factory.create_llm") as mock_create:
            mock_llm = Mock()
            mock_llm.achat = asyncio.coroutine(lambda x: "Test response")
            mock_create.return_value = mock_llm

            agent = PyAgent(config_obj)
            await agent.initialize()

            # 检查目录创建
            assert config_obj.file_store_path.exists()
            assert config_obj.vector_db_path.exists()
            assert config_obj.report_path.exists()

            await agent.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
