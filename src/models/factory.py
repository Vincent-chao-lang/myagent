"""模型工厂"""

from typing import Dict, Any

from .base import BaseLLM
from .claude import ClaudeLLM
from .openai import OpenAILLM
from .local import LocalLLM
from .glm import GLMLLM
from .qwen import QwenLLM
from .deepseek import DeepSeekLLM
from .kimi import KimiLLM
from .embedding import SentenceTransformerEmbedding


def create_llm(model_type: str, config: Dict[str, Any]) -> BaseLLM:
    """
    创建LLM实例的工厂方法

    Args:
        model_type: 模型类型 (claude | openai | glm | qwen | deepseek | kimi | local)
        config: 模型配置（已包含环境变量合并后的值）

    Returns:
        LLM实例

    Raises:
        ValueError: 不支持的模型类型
    """
    model_type = model_type.lower()
    from ..core.config import config as global_config

    if model_type == "claude":
        return ClaudeLLM(config, global_config.anthropic_api_key)

    elif model_type == "openai":
        return OpenAILLM(config, global_config.openai_api_key)

    elif model_type == "glm":
        return GLMLLM(config, global_config.zhipuai_api_key)

    elif model_type == "qwen":
        return QwenLLM(config, global_config.dashscope_api_key)

    elif model_type == "deepseek":
        return DeepSeekLLM(config, global_config.deepseek_api_key)

    elif model_type == "kimi":
        return KimiLLM(config, global_config.moonshot_api_key)

    elif model_type == "local":
        return LocalLLM(config, global_config.local_model_endpoint)

    else:
        supported = ["claude", "openai", "glm", "qwen", "deepseek", "kimi", "local"]
        raise ValueError(
            f"不支持的模型类型: {model_type}\n"
            f"支持的模型: {', '.join(supported)}"
        )


def create_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformerEmbedding:
    """
    创建嵌入模型实例

    Args:
        model_name: 模型名称

    Returns:
        嵌入模型实例
    """
    return SentenceTransformerEmbedding(model_name)
