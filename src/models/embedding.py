"""嵌入模型实现"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional
from loguru import logger


class SentenceTransformerEmbedding:
    """SentenceTransformer嵌入模型（支持本地缓存）"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: Optional[str] = None):
        """
        初始化嵌入模型

        Args:
            model_name: 模型名称或本地路径
            cache_dir: 模型缓存目录（优先使用环境变量）
        """
        self.model_name = model_name
        self._model = None

        # 设置模型缓存目录
        # 优先级: 参数 > 环境变量 > 默认值
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        elif os.getenv("SENTENCE_TRANSFORMERS_HOME"):
            self.cache_dir = Path(os.getenv("SENTENCE_TRANSFORMERS_HOME"))
        elif os.getenv("TRANSFORMERS_CACHE"):
            self.cache_dir = Path(os.getenv("TRANSFORMERS_CACHE"))
        else:
            # 默认使用项目下的缓存目录
            self.cache_dir = Path("./data/models/sentence_transformers")

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def model(self):
        """延迟加载模型（支持本地缓存）"""
        if self._model is None:
            try:
                logger.info(f"加载嵌入模型: {self.model_name}")

                # 设置环境变量，使用本地缓存
                os.environ["TRANSFORMERS_CACHE"] = str(self.cache_dir)
                os.environ["HF_HUB_OFFLINE"] = "1" if self._is_local_model() else "0"

                from sentence_transformers import SentenceTransformer

                # 检查是否为本地路径
                if Path(self.model_name).exists():
                    logger.info(f"使用本地模型: {self.model_name}")
                    self._model = SentenceTransformer(str(self.model_name))
                else:
                    # 尝试从缓存加载
                    cached_path = self.cache_dir / "models--sentence-transformers" / self.model_name
                    if cached_path.exists():
                        logger.info(f"从缓存加载模型: {cached_path}")
                        self._model = SentenceTransformer(str(self.model_name))
                    else:
                        # 第一次使用，需要下载（会缓存到本地）
                        logger.info(f"下载并缓存模型到: {self.cache_dir}")
                        self._model = SentenceTransformer(
                            self.model_name,
                            cache_folder=str(self.cache_dir)
                        )

                logger.info("嵌入模型加载完成")

            except Exception as e:
                logger.warning(f"加载嵌入模型失败: {e}")
                # 降级：返回None，调用者需要处理
                self._model = None

        return self._model

    def _is_local_model(self) -> bool:
        """检查是否使用本地模型"""
        return Path(self.model_name).exists()

    def encode(self, text: str) -> List[float]:
        """
        编码文本为向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        if self.model is None:
            # 模型加载失败，返回零向量
            logger.warning("嵌入模型不可用，使用零向量")
            return [0.0] * 384  # all-MiniLM-L6-v2 的维度

        return self.model.encode(text).tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量编码文本

        Args:
            texts: 输入文本列表

        Returns:
            嵌入向量列表
        """
        if self.model is None:
            logger.warning("嵌入模型不可用，使用零向量")
            return [[0.0] * 384 for _ in texts]

        return self.model.encode(texts).tolist()

    async def aencode(self, text: str) -> List[float]:
        """异步编码"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.encode, text)

    async def aencode_batch(self, texts: List[str]) -> List[List[float]]:
        """异步批量编码"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.encode_batch, texts)


class APIEmbedding:
    """API嵌入（使用LLM API生成嵌入，避免下载模型）"""

    def __init__(self, llm=None):
        """
        初始化API嵌入

        Args:
            llm: LLM实例（用于生成嵌入）
        """
        self.llm = llm

    async def aencode(self, text: str) -> List[float]:
        """异步编码（通过API）"""
        if self.llm is None:
            # 返回简单的哈希向量
            return self._text_to_hash_vector(text)

        try:
            # 使用LLM生成嵌入
            return await self.llm.aembed(text)
        except Exception as e:
            logger.warning(f"API嵌入失败: {e}")
            return self._text_to_hash_vector(text)

    def _text_to_hash_vector(self, text: str, dim: int = 384) -> List[float]:
        """文本转哈希向量（降级方案）"""
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # 扩展到指定维度
        vector = list(hash_bytes[:dim // 4])
        while len(vector) < dim:
            vector.extend(vector)

        # 归一化
        return [float(v) / 256.0 for v in vector[:dim]]
