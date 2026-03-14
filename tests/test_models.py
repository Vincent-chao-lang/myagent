"""测试模型模块"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from src.models.base import BaseLLM
from src.models.claude import ClaudeLLM
from src.models.openai import OpenAILLM
from src.models.local import LocalLLM
from src.models.glm import GLMLLM
from src.models.qwen import QwenLLM
from src.models.deepseek import DeepSeekLLM
from src.models.kimi import KimiLLM
from src.models.factory import create_llm


class TestBaseLLM:
    """测试LLM基类"""

    def test_base_llm_is_abstract(self):
        """测试基类是抽象的"""
        with pytest.raises(TypeError):
            BaseLLM({})


class TestClaudeLLM:
    """测试Claude模型"""

    @pytest.fixture
    def mock_config(self):
        return {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "temperature": 0.7
        }

    @pytest.fixture
    def claude_llm(self, mock_config):
        with patch("src.models.claude.Anthropic"), \
             patch("src.models.claude.AsyncAnthropic"):
            return ClaudeLLM(mock_config, "test_api_key")

    def test_init(self, claude_llm):
        """测试初始化"""
        assert claude_llm.model == "claude-3-5-sonnet-20241022"
        assert claude_llm.max_tokens == 4096


class TestGLMLLM:
    """测试智谱GLM模型"""

    @pytest.fixture
    def mock_config(self):
        return {
            "model": "glm-4-flash",
            "max_tokens": 4096,
            "temperature": 0.7
        }

    @pytest.fixture
    def glm_llm(self, mock_config):
        with patch("src.models.glm.ZhipuAI"):
            return GLMLLM(mock_config, "test_api_key")

    def test_init(self, glm_llm):
        """测试初始化"""
        assert glm_llm.model == "glm-4-flash"


class TestQwenLLM:
    """测试通义千问模型"""

    @pytest.fixture
    def mock_config(self):
        return {
            "model": "qwen-turbo",
            "max_tokens": 4096,
            "temperature": 0.7
        }

    @pytest.fixture
    def qwen_llm(self, mock_config):
        return QwenLLM(mock_config, "test_api_key")

    def test_init(self, qwen_llm):
        """测试初始化"""
        assert qwen_llm.model == "qwen-turbo"
        assert qwen_llm.api_key == "test_api_key"


class TestDeepSeekLLM:
    """测试DeepSeek模型"""

    @pytest.fixture
    def mock_config(self):
        return {
            "model": "deepseek-chat",
            "max_tokens": 4096,
            "temperature": 0.7
        }

    @pytest.fixture
    def deepseek_llm(self, mock_config):
        with patch("src.models.deepseek.OpenAI"), \
             patch("src.models.deepseek.AsyncOpenAI"):
            return DeepSeekLLM(mock_config, "test_api_key")

    def test_init(self, deepseek_llm):
        """测试初始化"""
        assert deepseek_llm.model == "deepseek-chat"


class TestKimiLLM:
    """测试Kimi模型"""

    @pytest.fixture
    def mock_config(self):
        return {
            "model": "moonshot-v1-8k",
            "max_tokens": 4096,
            "temperature": 0.7
        }

    @pytest.fixture
    def kimi_llm(self, mock_config):
        with patch("src.models.kimi.OpenAI"), \
             patch("src.models.kimi.AsyncOpenAI"):
            return KimiLLM(mock_config, "test_api_key")

    def test_init(self, kimi_llm):
        """测试初始化"""
        assert kimi_llm.model == "moonshot-v1-8k"


class TestModelFactory:
    """测试模型工厂"""

    def test_create_claude_llm(self):
        """测试创建Claude模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.anthropic_api_key = "test_key"

            with patch("src.models.claude.Anthropic"), \
                 patch("src.models.claude.AsyncAnthropic"):
                llm = create_llm("claude", {})
                assert isinstance(llm, ClaudeLLM)

    def test_create_openai_llm(self):
        """测试创建OpenAI模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.openai_api_key = "test_key"

            with patch("src.models.openai.OpenAI"), \
                 patch("src.models.openai.AsyncOpenAI"):
                llm = create_llm("openai", {})
                assert isinstance(llm, OpenAILLM)

    def test_create_glm_llm(self):
        """测试创建智谱GLM模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.zhipuai_api_key = "test_key"

            with patch("src.models.glm.ZhipuAI"):
                llm = create_llm("glm", {})
                assert isinstance(llm, GLMLLM)

    def test_create_qwen_llm(self):
        """测试创建通义千问模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.dashscope_api_key = "test_key"
            llm = create_llm("qwen", {})
            assert isinstance(llm, QwenLLM)

    def test_create_deepseek_llm(self):
        """测试创建DeepSeek模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.deepseek_api_key = "test_key"

            with patch("src.models.deepseek.OpenAI"), \
                 patch("src.models.deepseek.AsyncOpenAI"):
                llm = create_llm("deepseek", {})
                assert isinstance(llm, DeepSeekLLM)

    def test_create_kimi_llm(self):
        """测试创建Kimi模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.moonshot_api_key = "test_key"

            with patch("src.models.kimi.OpenAI"), \
                 patch("src.models.kimi.AsyncOpenAI"):
                llm = create_llm("kimi", {})
                assert isinstance(llm, KimiLLM)

    def test_create_local_llm(self):
        """测试创建本地模型"""
        with patch("src.models.factory.global_config") as mock_config:
            mock_config.local_model_endpoint = "http://localhost:11434"

            llm = create_llm("local", {})
            assert isinstance(llm, LocalLLM)

    def test_create_unsupported_model(self):
        """测试不支持的模型类型"""
        with pytest.raises(ValueError) as exc_info:
            create_llm("unsupported", {})
        assert "不支持的模型类型" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
