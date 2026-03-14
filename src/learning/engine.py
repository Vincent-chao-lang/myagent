"""学习引擎主模块"""

import time
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from .searcher import WebSearcher
from .parser import ContentParser
from .extractor import KnowledgeExtractor


class LearningEngine:
    """学习引擎"""

    def __init__(self, llm, knowledge_store, config):
        """
        初始化学习引擎

        Args:
            llm: LLM实例
            knowledge_store: 知识库实例
            config: 配置对象
        """
        self.llm = llm
        self.knowledge_store = knowledge_store
        self.config = config

        self.searcher = WebSearcher(config)
        self.parser = ContentParser()
        self.extractor = KnowledgeExtractor(llm)

        self.logger = logger

    async def search_all(self) -> List[Dict[str, Any]]:
        """执行所有搜索"""
        return await self.searcher.search_all()

    async def parse_all(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析所有搜索结果"""
        return await self.parser.parse_all(search_results)

    async def extract_all(self, parsed_contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从所有解析内容中提取知识"""
        return await self.extractor.extract_all(parsed_contents)

    async def learn(self) -> Dict[str, Any]:
        """
        执行完整学习流程，记录每个阶段的时长

        Returns:
            学习统计信息（包含时长）
        """
        self.logger.info("开始学习流程")
        start_time = time.time()
        start_datetime = datetime.now()

        # 存储各阶段时长
        stage_times = {}

        # 1. 搜索阶段
        stage_start = time.time()
        search_results = await self.search_all()
        stage_times["search"] = time.time() - stage_start
        self.logger.info(f"搜索完成：{len(search_results)} 条结果 (耗时: {stage_times['search']:.2f}秒)")

        # 2. 解析阶段
        stage_start = time.time()
        parsed_contents = await self.parse_all(search_results)
        stage_times["parse"] = time.time() - stage_start
        self.logger.info(f"解析完成：{len(parsed_contents)} 条内容 (耗时: {stage_times['parse']:.2f}秒)")

        # 3. 提取阶段
        stage_start = time.time()
        learnings = await self.extract_all(parsed_contents)
        stage_times["extract"] = time.time() - stage_start
        self.logger.info(f"提取完成：{len(learnings)} 条知识 (耗时: {stage_times['extract']:.2f}秒)")

        # 总时长
        total_time = time.time() - start_time

        return {
            "search_results": len(search_results),
            "parsed": len(parsed_contents),
            "learnings": learnings,
            "stage_times": stage_times,
            "total_time": total_time,
            "start_time": start_datetime.isoformat(),
            "end_time": datetime.now().isoformat()
        }

    def format_duration(self, seconds: float) -> str:
        """
        格式化时长为可读字符串

        Args:
            seconds: 秒数

        Returns:
            格式化的时长字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            return f"{int(hours)}小时{int(minutes)}分钟"

    async def close(self):
        """关闭学习引擎"""
        await self.searcher.close()
        await self.parser.close()
