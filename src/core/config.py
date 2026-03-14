"""配置管理模块 - 支持纯环境变量配置"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类 - 优先从环境变量读取，config.yaml 可选"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径（可选）
        """
        if config_path is None:
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件（可选）"""
        if self.config_path.exists():
            import yaml
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}

    def _get_str(self, env_key: str, default: str = "", yaml_path: str = "") -> str:
        """获取字符串配置"""
        env_val = os.getenv(env_key)
        if env_val is not None:
            return env_val
        if yaml_path:
            val = self._config
            for key in yaml_path.split("."):
                val = val.get(key, {}) if isinstance(val, dict) else {}
                if val == {}:
                    return default
            return str(val) if val is not None else default
        return default

    def _get_int(self, env_key: str, default: int = 0, yaml_path: str = "") -> int:
        """获取整数配置"""
        env_val = os.getenv(env_key)
        if env_val is not None and env_val.isdigit():
            return int(env_val)
        if yaml_path:
            val = self._config
            for key in yaml_path.split("."):
                val = val.get(key, {}) if isinstance(val, dict) else {}
                if val == {}:
                    return default
            return int(val) if isinstance(val, int) else default
        return default

    def _get_bool(self, env_key: str, default: bool = False, yaml_path: str = "") -> bool:
        """获取布尔配置"""
        env_val = os.getenv(env_key)
        if env_val is not None:
            return env_val.lower() in ("true", "1", "yes", "on")
        if yaml_path:
            val = self._config
            for key in yaml_path.split("."):
                val = val.get(key, {}) if isinstance(val, dict) else {}
                if val == {}:
                    return default
            return bool(val) if isinstance(val, bool) else default
        return default

    def _get_path(self, env_key: str, default: str, yaml_path: str = "") -> Path:
        """获取路径配置"""
        path_str = self._get_str(env_key, default, yaml_path)
        return Path(path_str).absolute()

    # ==================== Agent 配置 ====================

    @property
    def agent_name(self) -> str:
        return self._get_str("AGENT_NAME", "PyAgent", "agent.name")

    @property
    def agent_version(self) -> str:
        return self._get_str("AGENT_VERSION", "0.1.0", "agent.version")

    # ==================== 模型配置 ====================

    @property
    def model_type(self) -> str:
        return self._get_str("MODEL_TYPE", "claude", "model.type")

    @property
    def model_config(self) -> Dict[str, Any]:
        """模型配置（从环境变量构建）"""
        model_type = self.model_type
        config = {}

        if model_type == "claude":
            config = {
                "model": self._get_str("CLAUDE_MODEL", "claude-3-5-sonnet-20241022", "model.claude.model"),
                "max_tokens": self._get_int("CLAUDE_MAX_TOKENS", 4096, "model.claude.max_tokens"),
                "temperature": self._get_float("CLAUDE_TEMPERATURE", 0.7, "model.claude.temperature"),
                "base_url": self._get_str("CLAUDE_BASE_URL", "https://api.anthropic.com", "model.claude.base_url"),
            }
        elif model_type == "openai":
            config = {
                "model": self._get_str("OPENAI_MODEL", "gpt-4-turbo", "model.openai.model"),
                "max_tokens": self._get_int("OPENAI_MAX_TOKENS", 4096, "model.openai.max_tokens"),
                "temperature": self._get_float("OPENAI_TEMPERATURE", 0.7, "model.openai.temperature"),
                "base_url": self._get_str("OPENAI_BASE_URL", "https://api.openai.com/v1", "model.openai.base_url"),
            }
        elif model_type == "glm":
            config = {
                "model": self._get_str("GLM_MODEL", "glm-4-flash", "model.glm.model"),
                "max_tokens": self._get_int("GLM_MAX_TOKENS", 4096, "model.glm.max_tokens"),
                "temperature": self._get_float("GLM_TEMPERATURE", 0.7, "model.glm.temperature"),
                "base_url": self._get_str("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4", "model.glm.base_url"),
            }
        elif model_type == "qwen":
            config = {
                "model": self._get_str("QWEN_MODEL", "qwen-turbo", "model.qwen.model"),
                "max_tokens": self._get_int("QWEN_MAX_TOKENS", 4096, "model.qwen.max_tokens"),
                "temperature": self._get_float("QWEN_TEMPERATURE", 0.7, "model.qwen.temperature"),
                "base_url": self._get_str("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation", "model.qwen.base_url"),
            }
        elif model_type == "deepseek":
            config = {
                "model": self._get_str("DEEPSEEK_MODEL", "deepseek-chat", "model.deepseek.model"),
                "max_tokens": self._get_int("DEEPSEEK_MAX_TOKENS", 4096, "model.deepseek.max_tokens"),
                "temperature": self._get_float("DEEPSEEK_TEMPERATURE", 0.7, "model.deepseek.temperature"),
                "base_url": self._get_str("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1", "model.deepseek.base_url"),
            }
        elif model_type == "kimi":
            config = {
                "model": self._get_str("KIMI_MODEL", "moonshot-v1-8k", "model.kimi.model"),
                "max_tokens": self._get_int("KIMI_MAX_TOKENS", 4096, "model.kimi.max_tokens"),
                "temperature": self._get_float("KIMI_TEMPERATURE", 0.7, "model.kimi.temperature"),
                "base_url": self._get_str("KIMI_BASE_URL", "https://api.moonshot.cn/v1", "model.kimi.base_url"),
            }
        elif model_type == "local":
            config = {
                "endpoint": self._get_str("LOCAL_MODEL_ENDPOINT", "http://localhost:11434", "model.local.endpoint"),
                "model": self._get_str("LOCAL_MODEL", "codellama", "model.local.model"),
                "max_tokens": self._get_int("LOCAL_MAX_TOKENS", 2048, "model.local.max_tokens"),
            }

        return config

    def _get_float(self, env_key: str, default: float = 0.0, yaml_path: str = "") -> float:
        """获取浮点数配置"""
        env_val = os.getenv(env_key)
        if env_val is not None:
            try:
                return float(env_val)
            except ValueError:
                pass
        if yaml_path:
            val = self._config
            for key in yaml_path.split("."):
                val = val.get(key, {}) if isinstance(val, dict) else {}
                if val == {}:
                    return default
            return float(val) if isinstance(val, (int, float)) else default
        return default

    # ==================== API 密钥 ====================

    @property
    def anthropic_api_key(self) -> str:
        return os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def zhipuai_api_key(self) -> str:
        return os.getenv("ZHIPUAI_API_KEY", "")

    @property
    def dashscope_api_key(self) -> str:
        return os.getenv("DASHSCOPE_API_KEY", "")

    @property
    def deepseek_api_key(self) -> str:
        return os.getenv("DEEPSEEK_API_KEY", "")

    @property
    def moonshot_api_key(self) -> str:
        return os.getenv("MOONSHOT_API_KEY", "")

    @property
    def local_model_endpoint(self) -> str:
        return self._get_str("LOCAL_MODEL_ENDPOINT", "http://localhost:11434", "model.local.endpoint")

    # ==================== 知识库配置 ====================

    @property
    def file_store_path(self) -> Path:
        return self._get_path("FILE_STORE_PATH", "./data/knowledge", "knowledge.file_store_path")

    @property
    def vector_db_path(self) -> Path:
        return self._get_path("VECTOR_DB_PATH", "./data/vector_db", "knowledge.vector_db_path")

    @property
    def embedding_model(self) -> str:
        return self._get_str("EMBEDDING_MODEL", "all-MiniLM-L6-v2", "knowledge.embedding_model")

    @property
    def embedding_cache_dir(self) -> Path:
        return self._get_path("EMBEDDING_CACHE_DIR", "./data/models/sentence_transformers", "knowledge.embedding_cache_dir")

    @property
    def use_vector_db(self) -> bool:
        return self._get_bool("USE_VECTOR_DB", True, "knowledge.use_vector_db")

    @property
    def offline_mode(self) -> bool:
        return self._get_bool("OFFLINE_MODE", False, "knowledge.offline_mode")

    @property
    def chunk_size(self) -> int:
        return self._get_int("CHUNK_SIZE", 500, "knowledge.chunk_size")

    @property
    def chunk_overlap(self) -> int:
        return self._get_int("CHUNK_OVERLAP", 50, "knowledge.chunk_overlap")

    # ==================== 学习配置 ====================

    @property
    def learning_schedule(self) -> str:
        return self._get_str("LEARNING_SCHEDULE", "02:00", "learning.schedule")

    @property
    def learning_sources(self) -> List[Dict[str, Any]]:
        """学习源配置（从 YAML 读取，暂不支持环境变量）"""
        return self._config.get("learning", {}).get("sources", [
            {"type": "blog", "name": "Python Official Blog", "url": "https://blog.python.org"},
            {"type": "github", "name": "Trending Python", "query": "language:python"},
            {"type": "pypi", "name": "PyPI New Packages", "url": "https://pypi.org"},
        ])

    @property
    def max_daily_learnings(self) -> int:
        return self._get_int("MAX_DAILY_LEARNINGS", 20, "learning.max_daily_learnings")

    @property
    def search_queries(self) -> List[str]:
        """搜索查询列表"""
        return self._config.get("learning", {}).get("search_queries", [
            "Python 3.12 新特性详解",
            "Python type hints 最佳实践",
            "FastAPI 最佳实践",
        ])

    # ==================== 日报配置 ====================

    @property
    def report_path(self) -> Path:
        return self._get_path("REPORT_PATH", "./data/reports", "daily.report_path")

    @property
    def max_report_items(self) -> int:
        return self._get_int("MAX_REPORT_ITEMS", 10, "daily.max_report_items")

    # ==================== CLI 配置 ====================

    @property
    def max_history(self) -> int:
        return self._get_int("MAX_HISTORY", 100, "cli.max_history")

    @property
    def history_file(self) -> Path:
        return self._get_path("HISTORY_FILE", "./data/history.json", "cli.history_file")

    # ==================== 守护进程配置 ====================

    @property
    def pid_file(self) -> Path:
        return self._get_path("PID_FILE", "./data/daemon.pid", "daemon.pid_file")

    @property
    def log_file(self) -> Path:
        return self._get_path("LOG_FILE", "./data/logs/daemon.log", "daemon.log_file")

    @property
    def check_interval(self) -> int:
        return self._get_int("CHECK_INTERVAL", 60, "daemon.check_interval")

    # ==================== 通用方法 ====================

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def reload(self) -> None:
        """重新加载配置"""
        self._config = self._load_config()


# 全局配置实例
config = Config()
